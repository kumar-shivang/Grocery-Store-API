from . import db
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """A class representing a user in the application.

    This class contains information about a user such as their username, password, email, and orders.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        password (str): The hashed password of the user.
        email (str): The email address of the user.
        role_id (int): The ID of the role of the user.

    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(256))
    email = db.Column(db.String(100), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')

    def __init__(self, username, password, email, role_id=None):
        self.username = username
        self.email = email
        self.set_password(password)
        if role_id is None:
            try:
                self.role_id = Role.query.filter_by(role_name="customer").first().id
            except NoResultFound:
                raise NoResultFound("Role does not exist")
        else:
            self.role_id = role_id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Role(db.Model):
    """
    The Role class represents a role in the system.

    Attributes:
        id (int): The id of the role.
        role_name (str): The name of the role.
        role_description (str): The description of the role.
        users (Relationship): A relationship to the users with this role.

    Methods:
        __init__(self, role_name, role_description="")
            Initializes a new instance of the Role class.
        __repr__(self)
            Returns a string representation of the role.
    """
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), unique=True)
    role_description = db.Column(db.String(100))
    # users = db.relationship('user', backref='role', lazy='dynamic')

    def __init__(self, role_name, role_description=""):
        self.role_name = role_name
        self.role_description = role_description

    def __repr__(self):
        return '<Role {}>'.format(self.role_name)


class Product(db.Model):
    """
    The Product class represents a product in the system.

    Attributes:
        id (int): The id of the product.
        product_name (str): The name of the product.
        product_rate (float): The rate of the product.
        product_unit (str): The unit of the product.
        product_description (str): The description of the product.
        current_stock (int): The current stock of the product.
        expiry_date (datetime.date): The expiry date of the product.
        category_id (int): The id of the category that the product belongs to.

    Methods:
        __init__(self, product_name, product_rate, product_unit, product_description,
                expiry_date=datetime.utcnow() + timedelta(days=365), current_stock=0)
            Initializes a new instance of the Product class.
        __repr__(self)
            Returns a string representation of the product.

    """
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    rate = db.Column(db.Float)
    unit = db.Column(db.String(100))
    description = db.Column(db.String(100))
    current_stock = db.Column(db.Integer, db.CheckConstraint('current_stock >= 0'))
    expiry_date = db.Column(db.Date())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, rate, unit, description,added_by,category_id,
                 expiry_date=None, current_stock=0):
        self.name = name
        self.rate = rate
        self.unit = unit
        self.description = description
        self.current_stock = current_stock
        self.added_by = added_by
        self.category_id = category_id
        if expiry_date is None:
            self.expiry_date = datetime.utcnow() + timedelta(days=365)
        else:
            self.expiry_date = expiry_date

    def __repr__(self):
        return '<product {}>'.format(self.product_name)

    def add_stock(self, quantity):
        self.current_stock += quantity
        db.session.add(self)
        db.session.commit()
        return self

    def update_price(self, new_price):
        self.rate = new_price
        db.session.add(self)
        db.session.commit()
        return self

    def update_expiry_date(self, new_expiry_date):
        if new_expiry_date < datetime.utcnow().date():
            raise ValueError("Expiry date cannot be in the past")
        self.expiry_date = new_expiry_date
        db.session.add(self)
        db.session.commit()
        return self





class Category(db.Model):
    """Represents a category of products in the database.

    This class defines the structure and behavior of Category objects.

    Attributes:
        id (int): The ID of the category (primary key).
        category_name (str): The name of the category (unique).
        category_description (str): The description of the category.
        added_on (datetime): The date and time when the category was added to the database.
                            (default is current UTC time).
        last_updated (datetime): The date and time when the category was last updated
                                (default is current UTC time, updated automatically).
        products (relationship): A relationship to the Product class,
                                representing the products associated with this category.

    """
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True)
    category_description = db.Column(db.String(100))
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __init__(self, category_name, category_description="Product Category"):
        self.category_name = category_name
        self.category_description = category_description

    def __repr__(self):
        return '<category {}>'.format(self.category_name)

    def update(self):
        self.last_updated = datetime.utcnow()


class Order(db.Model):
    """
    Represents an order made by a user for a specific product.

    Attributes:
        id (int): The unique identifier for the order.
        order_date (datetime): The date and time when the order was made.
        product_id (int): The ID of the product being ordered.
        user_id (int): The ID of the user making the order.
        confirmed (bool): Indicates whether the order has been confirmed.
        quantity (int): The quantity of the product being ordered.
        value (float): The total price of the order.
    """
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    confirmed = db.Column(db.Boolean, default=False)
    quantity = db.Column(db.Integer)
    value = db.Column(db.Float)

    def __init__(self, product_id, user_id, quantity):
        try:
            product = Product.query.filter_by(id=product_id).first()
            self.value = product.product_rate * quantity
            self.product_id = product_id
            self.user_id = user_id
            self.quantity = quantity
        except NoResultFound:
            raise NoResultFound("Product does not exist")

    def __repr__(self):
        return '<order {}>'.format(self.id)


class CategoryRequest(db.Model):
    """
    Represents a request to add a new category to the database.

    Attributes:
        id (int): The unique identifier for the category request.
        category_name (str): The name of the category being requested.
        category_description (str): The description of the category being requested.
        added_on (datetime): The date and time when the category request was made.
        approved_at (datetime): The date and time when the category request was last updated.
        user_id (int): The ID of the user making the category request.
        approved (bool): Indicates whether the category request has been approved.

    Methods:
        approve(self)
            Approves the category request and adds the category to the database.
        reject(self)
            Rejects the category request and deletes it from the database.
        new_requests()
            Returns a list of all category requests that have not been approved.



    """
    __tablename__ = 'category_request'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True)
    category_description = db.Column(db.String(100))
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, default=None, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved = db.Column(db.Boolean, default=False)

    def __init__(self, category_name, category_description, user_id):
        self.category_name = category_name
        self.category_description = category_description
        self.user_id = user_id

    def __repr__(self):
        return '<category_request {}>'.format(self.category_name)

    def approve(self):
        self.approved = True
        db.session.add(self)
        db.session.commit()
        return Category(self.category_name, self.category_description)

    def reject(self):
        db.session.delete(self)
        db.session.commit()
        return None

    @staticmethod
    def new_requests():
        return CategoryRequest.query.filter_by(approved=False).all()
