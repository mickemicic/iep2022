import json

from flask import Flask, request, Response
from flask_jwt_extended import JWTManager, jwt_required
from redis.client import Redis

from models import database
from roleDecorator import roleCheck
from configuration import Configuration

# from store.models import database
# from store.roleDecorator import roleCheck
# from store.configuration import Configuration

import io
import csv

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@jwt_required()
@roleCheck(role="warehouse")
def updateStore():
    # con = request.files["file"].stream.read().decode("utf-8")
    con = request.files.get("file", None)

    if con:
        stream = io.StringIO(con.stream.read().decode("utf-8"))
        reader = csv.reader(stream)

        rowNum = 0
        currProducts = []
        for row in reader:
            if len(row) != 4:
                return Response(json.dumps({"message": f"Incorrect number of values on line {rowNum}."}), status=400)

            categories = row[0]
            title = row[1]
            try:
                int(row[2])
            except ValueError:
                return Response(json.dumps({"message": f"Incorrect quantity on line {rowNum}."}), status=400)

            if float(row[2]) == int(row[2]) and int(row[2]) > 0:
                quantity = int(row[2])
            else:
                return Response(json.dumps({"message": f"Incorrect quantity on line {rowNum}."}), status=400)

            try:
                float(row[3])
            except ValueError:
                return Response(json.dumps({"message": f"Incorrect price on line {rowNum}."}), status=400)
            if float(row[3]) > 0:
                price = float(row[3])
            else:
                return Response(json.dumps({"message": f"Incorrect price on line {rowNum}."}), status=400)
               # print(str(price) + " a-a " + str(quantity))

            # if float(row[2]) > int(quantity) or quantity <= 0:
            #     return Response(json.dumps({"message": f"Incorrect quantity on line {rowNum}."}), status=400)

            rowNum += 1
            currProduct = categories + "," + title + "," + str(quantity) + "," + str(price)
            currProducts.append(currProduct)

        for p in currProducts:
            with Redis(host=Configuration.REDIS_HOST) as redis:
                redis.rpush(Configuration.REDIS_PRODUCT_LIST, p)
        return Response(status=200)
    else:
        return Response(json.dumps({"message": "Field file is missing."}), status=400)


@application.route("/", methods=["GET"])
@jwt_required()
@roleCheck("warehouse")
def index():
    return "warehouse RADI!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
