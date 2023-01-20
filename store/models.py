from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "product_category"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


class OrderProduct(database.Model):
    __tablename__ = "order_product"

    id = database.Column(database.Integer, primary_key=True)

    orderId = database.Column(database.Integer, database.ForeignKey("orders.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    productId = database.Column(database.Integer, database.ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    myOrder = database.relationship("Order", back_populates="productOrders")
    products = database.relationship("Product", back_populates="productOrders")

    price = database.Column(database.Float, nullable=False)
    received = database.Column(database.Integer, nullable=False)
    requested = database.Column(database.Integer, nullable=False)


class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String(256), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)
    askingPrice = database.Column(database.Float, nullable=False)

    productOrders = database.relationship("OrderProduct", back_populates="products")
    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")


class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)

    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    timestamp = database.Column(database.TIMESTAMP, nullable=False)

    buyer = database.Column(database.String(256), nullable=False)

    productOrders = database.relationship("OrderProduct", back_populates="myOrder")

    def __repr__(self):
        return "({}, {}, {})".format(self.price, self.status, self.timestamp)
