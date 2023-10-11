from . import db
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User Class Documentation

    This class represents a User in the system.

    Attributes
        - id (int): The unique identifier for the user.
        - username (str): The username of the user.
        - password (str): The hashed password of the user.
        - email (str): The email address of the user.
        - role_id (int): The role ID of the user.
        - role (Role): The role object associated with the user.

    Methods
        - __init__(username, password, email, role_id=None): Initializes a new instance of the User class.
        - set_password(password): Sets the password of the user.
        - check_password(password): Checks if the provided password matches the user's password.
        - __repr__(): Returns a string representation of the User object.


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
    :class:`Role` class represents a role in the system.

    Attributes
        - id (int): The ID of the role (primary key).
        - role_name (str): The name of the role.
        - role_description (str): The description of the role.

    Methods
        - __init__(role_name, role_description=""): Initializes a new instance of the Role class.
        - __repr__(): Returns a string representation of the Role object.


    """
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), unique=True)
    role_description = db.Column(db.String(100))

    def __init__(self, role_name, role_description=""):
        self.role_name = role_name
        self.role_description = role_description

    def __repr__(self):
        return '<Role {}>'.format(self.role_name)


class Product(db.Model):
    """
    :class:`Product` class represents a product in the system. Each product belongs to a category.

    Attributes
        - id (int): The ID of the product (primary key).
        - name (str): The name of the product.
        - rate (float): The rate or price of the product.
        - unit (str): The unit of measurement for the product.
        - description (str): The description of the product.
        - current_stock (int): The current stock quantity of the product.

    Methods
        - __init__(name, rate, unit, description, current_stock=0): Initializes a new instance of the Product class.
        - __repr__(): Returns a string representation of the Product object.
        - add_stock(quantity): Adds stock to the product.
        - update_price(new_price): Updates the price of the product.
        - update_expiry_date(new_expiry_date): Updates the expiry date of the product.

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

    def __init__(self, name, rate, unit, description, added_by, category_id,
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
    """
    :class:`Category` class represents a category in the system. Each category can have multiple products.

    Attributes
        - id (int): The ID of the category (primary key).
        - category_name (str): The name of the category.
        - category_description (str): The description of the category.
        - added_on (datetime): The date and time when the category was added.
        - last_updated (datetime): The date and time when the category was last updated.

    Methods
        - __init__(category_name, category_description="Product Category"):
            Initializes a new instance of the Category class.
        - __repr__(): Returns a string representation of the Category object.
        - update(): Updates the last_updated attribute of the Category object.

    """
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True)
    category_description = db.Column(db.String(100))
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __init__(self, category_name, category_description,added_by=None):
        self.category_name = category_name
        self.category_description = category_description
        self.added_by = added_by

    def __repr__(self):
        return '<category {}>'.format(self.category_name)

    def update(self):
        self.last_updated = datetime.utcnow()


class Order(db.Model):
    """
    :class:`Order` class represents an order in the system. Each order is placed by a user for a product.

    Attributes:
    ----------
        - id (int): The ID of the order (primary key).
        - order_date (datetime): The date and time when the order was placed.
        - product_id (int): The ID of the product being ordered.
        - user_id (int): The ID of the user who placed the order.
        - confirmed (bool): Indicates whether the order has been confirmed or not.
        - quantity (int): The quantity of the product being ordered.
        - value (float): The total value of the order.

    Methods:
    -------
        - __init__(product_id, user_id, quantity): Initializes a new instance of the Order class.
        - __repr__(): Returns a string representation of the Order object.
        - confirm(): Confirms the order and returns the Order object.

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

    def confirm(self):
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return self


class CategoryRequest(db.Model):
    """
    :class:`CategoryRequest` class represents a request to add a new category in the system.
        Each request is made by a manager.

    Attributes:
    ----------
        - id (int): The ID of the category request (primary key).
        - category_name (str): The name of the category being requested.
        - category_description (str): The description of the category being requested.
        - added_on (datetime): The date and time when the request was made.
        - approved_at (datetime): The date and time when the request was approved.
        - user_id (int): The ID of the user who made the request.
        - approved (bool): Indicates whether the request has been approved or not.

    Methods:
    -------
        - __init__(category_name, category_description, user_id):
            Initializes a new instance of the CategoryRequest class.
        - __repr__(): Returns a string representation of the CategoryRequest object.
        - approve(): Approves the request and returns the Category object.
        - reject(): Rejects the request and returns None.
        - new_requests(): Returns a list of all unapproved requests.

    """
    __tablename__ = 'category_request'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, nullable=True)
    category_name = db.Column(db.String(100), nullable=True)
    category_description = db.Column(db.String(100), nullable=True)
    request_type = db.Column(db.String(100), db.check_constraint('request_type in ("add", "remove", "update")'))
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
        if self.approved:
            raise ValueError("Request already approved")
        elif self.request_type == "add":
            category = Category(self.category_name, self.category_description,self.user_id)
            db.session.add(category)
            db.session.commit()
        elif self.request_type == "edit":
            category = Category.query.get(self.category_id)
            if category:
                category.category_name = self.category_name
                category.category_description = self.category_description
                category.update()
                db.session.add(category)
                db.session.commit()
            else:
                raise NoResultFound("Category does not exist")
        elif self.request_type == "remove":
            category = Category.query.get(self.category_id)
            if category:
                if category.added_by != self.user_id:
                    raise ValueError("You are not authorized to request deletion of this category")
                db.session.delete(category)
                db.session.commit()
            else:
                raise NoResultFound("Category does not exist")

    def reject(self):
        db.session.delete(self)
        db.session.commit()
        return None

    @staticmethod
    def new_requests():
        return CategoryRequest.query.filter_by(approved=False).all()
