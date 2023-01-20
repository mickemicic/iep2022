from datetime import datetime

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from store.admin.adminDecorator import roleCheck
from store.configuration import Configuration
from store.models import database, Product, Category, Order, OrderProduct

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/productStatistics", methods=["GET"])
@jwt_required()
@roleCheck("admin")
def productStats():
    pro = Product.query.filter().all()

    statsArr = []

    for p in pro:
        sold = 0
        waiting = 0
        if len(p.productOrders) > 0:
            for pOrd in p.productOrders:
                sold = sold + pOrd.received
                waiting = waiting + pOrd.requested - pOrd.received
            pomStat = {
                "name": p.title,
                "sold": sold,
                "waiting": waiting
            }

            statsArr.append(pomStat)

    return jsonify({"statistics": statsArr}), 200


@application.route("/categoryStatistics", methods=["GET"])
@jwt_required()
@roleCheck("admin")
def categoryStats():
    cat = Category.query.filter().all()


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5005)
