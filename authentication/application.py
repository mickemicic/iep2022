import json
import re

from flask import Flask, request, Response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_

from configuration import Configuration
from models import database, User, UserRole
from store.admin.adminDecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0

    if forenameEmpty:
        return Response(json.dumps({"message": "Field forename is missing."}), status=400)

    if surnameEmpty:
        return Response(json.dumps({"message": "Field surname is missing."}), status=400)

    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    if isCustomer is None or "isCustomer" not in request.json:
        return Response(json.dumps({"message": "Field isCustomer is missing."}), status=400)

    # result = parseaddr(email)
    # if len(result[0]) == 0:
    #     return Response("first "+result[0]+" -- -" +result[1], status=400)     RESULT[0]

    emailValid = re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

    if not emailValid:
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    if len(password) < 8 or re.search(r"\d", password) is None or re.search(r"[A-Z]", password) is None or \
            re.search(r"[a-z]", password) is None:
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    if User.query.filter(User.email == email).first():
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    user = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(user)
    database.session.commit()

    # userRole = UserRole(userId=user.id, roleId=int(isCustomer)+2)
    if isCustomer:
        roleId = 3
    else:
        roleId = 2
    userRole = UserRole(userId=user.id, roleId=roleId)
    database.session.add(userRole)
    database.session.commit()

    return Response("Registration successful!", status=200)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    emailValid = re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

    if not emailValid:
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if not user:
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    # return Response ( accessToken, status = 200 );
    # return jsonify(accessToken=accessToken, refreshToken=refreshToken)

    return Response(json.dumps({"accessToken": accessToken, "refreshToken": refreshToken}), status=200)


@application.route("/delete", methods=["POST"])
@jwt_required()
@roleCheck(role="admin")
def delete():
    email = request.json.get("email", "")

    emailEmpty = len(email) == 0
    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    emailValid = re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

    if not emailValid:
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(User.email == email).first()

    if not user:
        return Response(json.dumps({"message": "Unknown user."}), status=400)

    User.query.filter(User.email == email).delete()
    database.session.commit()

    return Response(status=200)


@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid!"


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"]
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims)), 200


#################################################################
@application.route("/proba", methods=["GET"])
def proba():
    user = User.query.filter(and_(User.email == "pera@pera.com", User.password == "1234")).first()

    if not user:
        return Response("Invalid credentials!", status=400)

    return user.forename


##################################################################
@application.route("/", methods=["GET"])
def index():
    return "RADI!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
