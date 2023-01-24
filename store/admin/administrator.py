from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from sqlalchemy import func

from store.admin.adminDecorator import roleCheck
from store.configuration import Configuration
from store.models import database, Product, Category, OrderProduct, ProductCategory

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/productStatistics", methods=["GET"])
@jwt_required()
@roleCheck("admin")
def productStats():
    orders = OrderProduct.query.group_by(OrderProduct.productId). \
        with_entities(OrderProduct.productId,
                      func.sum(OrderProduct.requested).label("sold"),
                      (func.sum(OrderProduct.requested) - func.sum(OrderProduct.received)).label("waiting")).all()

    statsArr = []

    for o in orders:
        productName = Product.query.filter(Product.id == o.productId).first()
        pomStat = {
            "name":  productName.title,
            "sold": int(o.sold),
            "waiting": int(o.waiting)
        }

        statsArr.append(pomStat)

    # for p in pro:
    #     sold = 0
    #     waiting = 0
    #     if len(p.productOrders) > 0:
    #         for pOrd in p.productOrders:
    #             sold = sold + pOrd.received
    #             waiting = waiting + pOrd.requested - pOrd.received
    #         pomStat = {
    #             "name": p.title,
    #             "sold": sold,
    #             "waiting": waiting
    #         }
    #
    #         statsArr.append(pomStat)

    return jsonify({"statistics": statsArr}), 200


@application.route("/categoryStatistics", methods=["GET"])
@jwt_required()
@roleCheck("admin")
def categoryStats():
    reqs = func.coalesce(func.sum(OrderProduct.requested), 0)
    cat = Category.query.outerjoin(ProductCategory, ProductCategory.categoryId == Category.id).outerjoin \
        (OrderProduct, OrderProduct.productId == ProductCategory.productId).group_by(Category.id).order_by(reqs.desc()) \
        .order_by(Category.name).all()

    catArr = []

    for c in cat:
        catArr.append(c.name)

    return jsonify({"statistics": catArr}), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5005)
