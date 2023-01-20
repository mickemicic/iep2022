from datetime import datetime

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from store.admin.adminDecorator import roleCheck
from store.configuration import Configuration
from store.models import database, Product, Category, Order, OrderProduct

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/search", methods=["GET"])
@jwt_required()
@roleCheck("customer")
def search():
    product = request.args.get("name", default="")
    pro = Product.query.filter(Product.title.contains(product)).all()

    categoryName = request.args.get("category", default="")
    cat = Category.query.filter(Category.name.contains(categoryName)).all()

    categoryList = []  # arrCategory
    productList = []

    idHelper = []

    # imam sve kategorije sa imenom category, i sve proizvode sa imenom name

    for p in pro:
        catArr = []
        flag = 0
        for c in p.categories:
            catArr.append(c.name)
            if c in cat:
                flag = 1
                if c.name not in categoryList:
                    categoryList.append(c.name)

        if flag and p.id not in idHelper:
            pomPro = {
                "categories": catArr,  # mozda ne sme 21e142143141353124
                "id": p.id,
                "name": p.title,
                "price": p.askingPrice,
                "quantity": p.quantity
            }
            idHelper.append(p.id)
            productList.append(pomPro)

    searchResults = {"categories": categoryList, "products": productList}

    return jsonify(searchResults), 200
    # return Response(json.dumps({"categories": categoryList, "products": productList}), status=200)

    # for p in pro:
    #     print(p.title + " - ")




    # for p in pro:
    #     print("proizvod:" + p.title + '\n')
    # for p in pro:
    #     print(p.name + " - \n")
    #     flag = 0
    #     for c in cat:
    #         if c in p.categories:
    #             flag = 1
    #     if flag and p not in productList:
    #         pomCat = []
    #         for catPro in p.categories:
    #             pomCat.append(catPro.name)
    #         pomPro = {
    #             "categories": pomCat,
    #             "id": p.id,
    #             "name": p.title,
    #             "price": p.askingPrice,
    #             "quantity": p.quantity
    #         }
    #         productList.append(pomPro)
    #
    # for c in cat:
    #     flag = 0
    #     for p in pro:
    #         if p in c.products:
    #             flag = 1
    #     if flag and c.name not in categoryList:
    #         categoryList.append(c.name)


    # for c in cat:
    #     for p in pro:
    #         if c in p.categories and not c.name in arrCategory:
    #             arrCategory.append(c.name)
    #             pomCat = []
    #             for cP in p.categories:
    #                 pomCat.append(cP.name)
    #             pomPro = {
    #                 "categories": pomCat,
    #                 "id": p.id,
    #                 "name": p.title,
    #                 "price": p.askingPrice,
    #                 "quantity": p.quantity
    #             }
    #             if pomPro in productList:
    #                 print(p.title + ' imaga ')
    #             else:
    #                 productList.append(pomPro)




@application.route("/order", methods=["POST"])
@jwt_required()
@roleCheck("customer")
def order():

    try:
        requests = request.json.get("requests", "")
        for idReq, req in enumerate(requests):
            if req.get("id") is None:
                return jsonify({"message": "Product id is missing for request number " + str(idReq) + "."}), 400
            if req.get("quantity") is None:
                return jsonify({"message": "Product quantity is missing for request number " + str(idReq) + "."}), 400
            if not isinstance(req.get("id"), int) or req.get("id") <= 0:
                return jsonify({"message": "Invalid product id for request number " + str(idReq) + "."}), 400
            if not isinstance(req.get("quantity"), int) or req.get("quantity") <= 0:
                return jsonify({"message": "Invalid product quantity for request number " + str(idReq) + "."}), 400
            if Product.query.filter(Product.id == req.get("id")).first() is None:
                return jsonify({"message": "Invalid product for request number " + str(idReq) + "."}), 400

        proArr = []
        totalPrice = 0

        newOrd = Order(price=0, status="PENDING", timestamp=datetime.now().isoformat(), buyer=get_jwt_identity())
        database.session.add(newOrd)
        database.session.commit()

        flag = 1

        for req in requests:
            idPro = req["id"]
            pro = Product.query.filter((Product.id == idPro)).first()
            if pro.quantity < req["quantity"]:
                flag = 0
                received = pro.quantity
                pro.quantity = 0
            else:
                pro.quantity = pro.quantity - req["quantity"]
                received = req["quantity"]
            proArr.append(pro)
            newOrdPro = OrderProduct(orderId=newOrd.id, productId=idPro, price=pro.askingPrice, received=received,
                                     requested=req["quantity"])
            totalPrice = totalPrice + pro.askingPrice * req["quantity"]

        newOrd.price = totalPrice

        if flag:
            newOrd.status = "COMPLETE"

        database.session.add(newOrdPro)

        database.session.commit()

        return jsonify({"id": newOrd.id}), 200

    except UnboundLocalError:
        return jsonify({"message": "Field requests is missing."}), 400


@application.route("/status", methods=["GET"])
@jwt_required()
@roleCheck("customer")
def status():
    email = get_jwt_identity()
    orders = Order.query.filter(Order.buyer == email)

    ordersList = []

    for o in orders:
        productList = []
        for po in o.productOrders:
            productCategories = []
            for cP in po.products.categories:
                productCategories.append(cP.name)
            pomPro = {
                "categories": productCategories,
                "name": po.products.title,
                "price": po.price,
                "received": po.received,
                "requested": po.requested
            }
            productList.append(pomPro)
        currOrder = {
            "products": productList,
            "price": o.price,
            "status": o.status,
            "timestamp": o.timestamp
        }
        ordersList.append(currOrder)

    return jsonify({"orders": ordersList}), 200


#
# @application.route("/brm", methods=["GET"])
# @jwt_required()
# @roleCheck("customer")
# def index():
#     return "RADI!"
#

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5004)
