import collections
from flask import Flask
from flask_jwt_extended import JWTManager
from redis.client import Redis
from sqlalchemy import and_

from store.configuration import Configuration
from store.models import database, Product, Category, ProductCategory, OrderProduct, Order

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

if __name__ == "__main__":
    database.init_app(application)

    with Redis(host=Configuration.REDIS_HOST) as redis:
        while 1:
            with application.app_context() as context:
                entryRow = redis.blpop(Configuration.REDIS_PRODUCT_LIST)[1].decode("utf-8")
                entry = entryRow.split(",")

                productCategories = entry[0].split("|")
                productTitle = entry[1]
                productQuantity = int(entry[2])
                productPrice = float(entry[3])

                currProduct = Product.query.filter(Product.title == productTitle).first()

                if currProduct is not None:
                    # product exists, check if pending orders
                    catsName = []
                    for category in productCategories:
                        cat = Category.query.filter(Category.name == category).first()
                        if cat:
                            catsName.append(cat.name)

                    if collections.Counter(productCategories) == collections.Counter(catsName):
                        price = \
                            (currProduct.quantity * currProduct.askingPrice + productQuantity * productPrice) \
                            / (currProduct.quantity + productQuantity)
                        currProduct.quantity = currProduct.quantity + productQuantity

                        currProduct.askingPrice = price
                        database.session.commit()
                        database.session.commit()

                    productOrders = OrderProduct.query.filter(and_(OrderProduct.productId == currProduct.id,
                                                                   OrderProduct.received != OrderProduct.requested
                                                                   )).all()

                    while currProduct.quantity > 0 and productOrders:
                        for po in productOrders:
                            if currProduct.quantity < (po.requested - po.received):
                                po.received = po.received + currProduct.quantity
                                currProduct.quantity = 0
                                database.session.commit()
                            else:
                                currProduct.quantity = currProduct.quantity - (po.requested - po.received)
                                po.received = po.requested
                                flag = 1
                                order = Order.query.filter(Order.id == po.orderId).first()
                                for pos in order.productOrders:
                                    if pos.requested != pos.received:
                                        flag = 0
                                if flag:
                                    order.status = "COMPLETE"
                                database.session.commit()
                                productOrders.remove(po)

                    # else bad category
                else:
                    product = Product(title=productTitle, quantity=productQuantity, askingPrice=productPrice)

                    database.session.add(product)
                    for category in productCategories:
                        cat = Category.query.filter(Category.name == category).first()
                        if cat is None:
                            cat = Category(name=category)
                            database.session.add(cat)
                            database.session.commit()

                        prodCat = ProductCategory(productId=product.id, categoryId=cat.id)
                        database.session.add(prodCat)

                    database.session.commit()

            # UKOLIKO NEKA NARUDZBINA MOZE DA SE OBAVI
