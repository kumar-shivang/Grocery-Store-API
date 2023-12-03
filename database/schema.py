from datetime import datetime
from uuid import uuid1

import PIL
import bleach
from PIL import Image
from marshmallow import Schema, fields, ValidationError, validates, post_load
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from .models import (User, Role, Product, Category, Order, CategoryRequest,
                     ManagerCreationRequests, ProductImage)


def clean(string):
    string = string.strip()
    string = string.lower()
    string = bleach.clean(string)
    return string


def validate_password(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    elif not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit")
    elif not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase character")
    elif not any(char.islower() for char in password):
        raise ValidationError("Password must contain at least one lowercase character")


class UserSchema(Schema):
    """
    :class:`UserSchema` class for serializing and deserializing User objects.

    Attributes
        - id (Int, optional): The ID of the user. (read-only)
        - username (Str): The username of the user.
        - email (Email): The email address of the user.
        - password (Str, write-only): The password of the user.
        - role (RoleSchema, optional): The role of the user.

    Methods
        - validate_password(password): Validates the password field.
        - validate_username(username): Validates the username field.
        - make_user(data): Creates a User object from the serialized data.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role_id', 'role')

    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    password = fields.Str(load_only=True)
    role_id = fields.Int(load_only=True, required=False)
    role = fields.Nested("RoleSchema", exclude=('users',))

    @validates("password")
    def validate_pass(self, password):
        validate_password(password)

    @validates("username")
    def validate_username(self, username):
        username = username.strip()
        username = username.lower()
        username = bleach.clean(username)
        if len(username) < 6:
            raise ValidationError("Username must be at least 6 characters long")
        elif username[0].isdigit():
            raise ValidationError("Username must start with a letter")
        elif not username.isalnum():
            raise ValidationError("Username must only contain letters and numbers")
        elif User.query.filter_by(username=username).first():
            raise ValidationError("Username already exists")

    @validates('email')
    def validate_email(self, email):
        if User.query.filter_by(email=email).first():
            raise ValidationError("Email already exists")

    @validates('role_id')
    def validate_role_id(self, role_id):
        if not Role.query.filter_by(id=role_id).first():
            raise ValidationError("Role with id {} does not exist".format(role_id))

    @post_load
    def make_user(self, data, **kwargs):
        try:
            username = data.get('username')
            username = clean(username)
            data['username'] = username
            return User(**data)
        except Exception as e:
            raise ValidationError(str(e))
        finally:
            del kwargs


class RoleSchema(Schema):
    """
    :class:`RoleSchema` class for serializing and deserializing Role objects.

    Attributes
        - id (Int, optional): The ID of the role. (read-only)
        - role_name (Str): The name of the role.
        - role_description (Str): The description of the role.

    """

    class Meta:
        model = Role
        fields = ('id', 'role_name', 'role_description', 'users')

    id = fields.Int(dump_only=True)
    role_name = fields.Str()
    role_description = fields.Str()


class ProductSchema(Schema):
    """
    :class:`ProductSchema` class for serializing and deserializing Product objects.

    Attributes
        - id (Int, optional): The ID of the product. (read-only)
        - name (Str): The name of the product.
        - rate (Float): The rate of the product.
        - unit (Str): The unit of the product.
        - description (Str): The description of the product.
        - current_stock (Int): The current stock of the product.
        - expiry_date (Date): The expiry date of the product.
        - added_by (Int, write-only): The ID of the user who added the product.
        - category_id (Int, write-only): The ID of the category to which the product belongs.
        - category (CategorySchema): The category to which the product belongs.
        - image_id (Int, write-only): The ID of the image of the product.
        - image (ProductImageSchema): The image of the product.

    Methods
        - validate_name(name): Validates the name field.
        - validate_rate(rate): Validates the rate field.
        - validate_unit(unit): Validates the unit field.
        - validate_description(description): Validates the description field.
        - validate_current_stock(current_stock): Validates the current_stock field.
        - validate_expiry_date(expiry_date): Validates the expiry_date field.
        - validate_added_by(added_by): Validates the added_by field.
        - validate_category_id(category_id): Validates the category_id field.
        - make_product(data): Creates a Product object from the serialized data.

    """

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'rate', 'unit', 'description', 'current_stock',
            'expiry_date', 'added_by', 'category_id', 'category',
            'image_id', 'image')
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    name = fields.Str()
    rate = fields.Float()
    unit = fields.Str()
    description = fields.Str()
    current_stock = fields.Int()
    expiry_date = fields.Date(format='%Y-%m-%d')
    added_by = fields.Int(load_only=True)  # added_by is the user id of the user who added the product
    category_id = fields.Int(load_only=True, required=False)
    category = fields.Nested('CategorySchema', exclude=('products', 'added_on', 'last_updated'))
    image_id = fields.Int(load_only=True, required=False, default=1)
    image = fields.Nested('ProductImageSchema', exclude=('products',))

    @validates('added_by')
    def validate_added_by(self, added_by):
        if not User.query.filter_by(id=added_by).first():
            raise ValidationError("User with id {} does not exist".format(added_by))
        elif not User.query.get(added_by).role.role_name == 'manager':
            raise ValidationError("Only managers can add products")

    @validates('category_id')
    def validate_category_id(self, category_id):
        if not Category.query.filter_by(id=category_id).first():
            raise ValidationError("Category with id {} does not exist".format(category_id))

    @validates('expiry_date')
    def validate_expiry_date(self, expiry_date):
        if expiry_date < datetime.utcnow().date():
            raise ValidationError("Expiry date cannot be in the past")

    @validates('rate')
    def validate_rate(self, rate):
        if rate <= 0:
            raise ValidationError("Product rate cannot be negative or zero")

    @validates('unit')
    def validate_unit(self, unit):
        if unit not in ['kg', 'litre', 'unit']:
            raise ValidationError("Product unit must be one of 'kg', 'litre', 'unit'")

    @validates('name')
    def validate_name(self, name):
        name = clean(name)
        if len(name) < 3:
            raise ValidationError("Product name must be at least 3 characters long")
        elif not all([char.isalnum() or char.isspace() for char in name]):
            raise ValidationError("Product name must only contain letters and numbers")
        elif Product.query.filter_by(name=name).first():
            raise ValidationError("Product with name {} already exists".format(name))

    @validates('description')
    def validate_description(self, description):
        description = clean(description)
        if len(description) < 10:
            raise ValidationError("Product description must be at least 10 characters long")

    @validates('current_stock')
    def validate_current_stock(self, current_stock):
        if current_stock < 0:
            raise ValidationError("Current stock cannot be negative")

    @validates('image_id')
    def validate_image_id(self, image_id):
        if not ProductImage.query.filter_by(id=image_id).first():
            raise ValidationError("Image with id {} does not exist".format(image_id))

    @post_load()
    def make_product(self, data, **kwargs):
        try:
            name = data.get('name')
            name = clean(name)
            data['name'] = name
            description = data.get('description')
            description = clean(description)
            data['description'] = description
            if not data.get('category_id'):
                category = Category.query.filter_by(category_name='Uncategorized').first()
                data['category_id'] = category.id
            return Product(**data)
        except TypeError as e:
            raise ValidationError(str(e))


class CategorySchema(Schema):
    """
    :class:`CategorySchema` class for serializing and deserializing Category objects.

    Attributes
        - id (Int, optional): The ID of the category. (read-only)
        - category_name (Str): The name of the category.
        - category_description (Str): The description of the category.
        - added_on (DateTime, optional): The datetime when the category was added. (read-only)
        - last_updated (DateTime, optional): The datetime when the category was last updated. (read-only)
        - products (List[ProductSchema], optional): The products in the category. (read-only)

    Methods
        - validate_category_name(category_name): Validates the category_name field.
        - validate_category_description(category_description): Validates the category_description field.
        - make_category(data): Creates a Category object from the serialized data.

    """

    class Meta:
        model = Category
        fields = ('id', 'category_name', 'category_description', 'products','added_on', 'last_updated')

    id = fields.Int(dump_only=True)
    category_name = fields.Str(required=True)
    category_description = fields.Str(required=True)
    products = fields.Nested('ProductSchema', exclude=('category',), dump_only=True)

    @validates('category_name')
    def validate_category_name(self, category_name):
        category_name = clean(category_name)
        if len(category_name) < 3:
            raise ValidationError("Category name must be at least 3 characters long")
        elif not all([char.isalnum() or char.isspace() for char in category_name]):
            raise ValidationError("Category name must only contain letters and numbers")
        elif Category.query.filter_by(category_name=category_name).first():
            raise ValidationError("Category with name {} already exists".format(category_name))

    @validates('category_description')
    def validate_category_description(self, category_description):
        if len(category_description) < 10:
            raise ValidationError("Category description must be at least 10 characters long")
        if len(category_description) > 140:
            raise ValidationError("Category description must be less than 140 characters long")

    @post_load()
    def make_category(self, data, **kwargs):
        try:
            category_name = data.get('category_name')
            category_name = clean(category_name)
            data['category_name'] = category_name
            category_description = data.get('category_description')
            category_description = clean(category_description)
            data['category_description'] = category_description
            return Category(**data)
        except TypeError as e:
            raise ValidationError(str(e))
        finally:
            del kwargs


class OrderSchema(Schema):
    """
    :class:`OrderSchema` class for serializing and deserializing Order objects.

    Attributes
        - id (Int, optional): The ID of the order. (read-only)
        - order_date (DateTime, optional): The datetime when the order was placed. (read-only)
        - user_id (Int, write-only): The ID of the user who placed the order.
        - product_id (Int, write-only): The ID of the product ordered.
        - quantity (Int): The quantity of the product ordered.
        - value (Float, optional): The value of the order. (read-only)
        - confirmed (Boolean, optional): Indicates whether the order is confirmed or not. (read-only)
        - product (ProductSchema, optional): The product ordered. (read-only)

    Methods
        - validate_user_id(user_id): Validates the user_id field.
        - validate_product_id(product_id): Validates the product_id field.
        - validate_quantity(quantity): Validates the quantity field.
        - make_order(data): Creates an Order object from the serialized data.

    """

    class Meta:
        model = Order
        fields = ('id', 'order_date', 'user_id', 'product_id', 'quantity', 'value', 'confirmed', 'product')

    id = fields.Int(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    user_id = fields.Int(load_only=True)
    product_id = fields.Int(load_only=True)
    quantity = fields.Int()
    value = fields.Float(dump_only=True)
    confirmed = fields.Boolean(dump_only=True)
    product = fields.Nested('ProductSchema')

    @validates('user_id')
    def validate_user_id(self, user_id):
        if not User.query.filter_by(id=user_id).first():
            raise ValidationError("User with id {} does not exist".format(user_id))

    @validates('product_id')
    def validate_product_id(self, product_id):
        if not Product.query.filter_by(id=product_id).first():
            raise ValidationError("Product with id {} does not exist".format(product_id))

    @validates('quantity')
    def validate_quantity(self, quantity):
        if not isinstance(quantity, int):
            raise ValidationError("Quantity must be an integer")
        elif quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")

    @post_load
    def make_order(self, data):
        try:
            user_id = data.get('user_id')
            product_id = data.get('product_id')
            quantity = data.get('quantity')
            return Order(user_id=user_id, product_id=product_id, quantity=quantity)
        except TypeError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(str(e))


class CategoryRequestSchema(Schema):
    """
    :class:`CategoryRequestSchema` class for serializing and deserializing CategoryRequest objects.

    Attributes
        - id (Int, optional): The ID of the category request. (read-only)
        - category_name (Str): The name of the category requested.
        - category_description (Str): The description of the category requested.
        - added_on (DateTime, optional): The datetime when the category request was made. (read-only)
        - last_updated (DateTime, optional): The datetime when the category request was last updated. (read-only)
        - approved_at (DateTime, optional): The datetime when the category request was approved. (read-only)
        - approved (Boolean, optional): Indicates whether the category request is approved or not. (read-only)

    Methods
        - validate_category_name(category_name): Validates the category_name field.
        - validate_category_description(category_description): Validates the category_description field.
        - make_category_request(data): Creates a CategoryRequest object from the serialized data.

    """

    class Meta:
        model = CategoryRequest
        fields = ('id', 'category_id', 'category_name', 'category_description',
                  'added_on', 'approved_at', 'approved', 'request_type', 'user_id')

    id = fields.Int(dump_only=True)
    category_id = fields.Int(required=False, default=None)
    category_name = fields.Str(required=False, default=None)
    category_description = fields.Str(required=False, default=None)
    request_type = fields.Str(required=True)
    added_on = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True)
    approved_at = fields.DateTime(dump_only=True)
    approved = fields.Boolean(dump_only=True)

    @validates('category_name')
    def validate_category_name(self, category_name):
        if len(category_name) < 3:
            raise ValidationError("Category name must be at least 3 characters long")
        elif not all([char.isalnum() or char.isspace() for char in category_name]):
            raise ValidationError("Category name must only contain letters and numbers")

    @validates('category_description')
    def validate_category_description(self, category_description):
        if len(category_description) < 10:
            raise ValidationError("Category description must be at least 10 characters long")
        if len(category_description) > 140:
            raise ValidationError("Category description must be less than 140 characters long")

    @validates('request_type')
    def validate_request_type(self, request_type):
        if request_type not in {'add', 'delete', 'update'}:
            raise ValidationError("Request type must be one of 'add', 'delete','update'")

    @validates('category_id')
    def validate_category_id(self, category_id):
        if not Category.query.filter_by(id=category_id).first():
            raise ValidationError("Category with id {} does not exist".format(category_id))

    @post_load()
    def make_category_request(self, data, **kwargs):
        try:
            data['category_name'] = clean(data.get('category_name'))
            data['category_description'] = clean(data.get('category_description'))
            return CategoryRequest(**data)
        except TypeError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(str(e))
        finally:
            del kwargs


class ManagerRequestSchema(Schema):
    """
    :class:`ManagerRequestSchema` class for serializing and deserializing ManagerCreationRequests objects.

    Attributes
        - id (Int, optional): The ID of the manager request. (read-only)
        - username (Str): The username of the manager requested.
        - email (Email): The email address of the manager requested.
        - password (Str, write-only): The password of the manager requested.
        - added_on (DateTime, optional): The datetime when the manager request was made. (read-only)
        - approved_at (DateTime, optional): The datetime when the manager request was approved. (read-only)
        - approved (Boolean, optional): Indicates whether the manager request is approved or not. (read-only)


    Methods
        - validate_username(username): Validates the username field.
        - validate_email(email): Validates the email field.
        - validate_password(password): Validates the password field.

    """

    class Meta:
        model = ManagerCreationRequests
        fields = ('id', 'username', 'email', 'password', 'added_on', 'approved_at', 'approved')

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    added_on = fields.DateTime(dump_only=True)
    approved_at = fields.DateTime(dump_only=True)
    approved = fields.Boolean(dump_only=True)

    @validates('username')
    def validate_username(self, username):
        username = clean(username)
        if len(username) < 6:
            raise ValidationError("Username must be at least 6 characters long")
        elif username[0].isdigit():
            raise ValidationError("Username must start with a letter")
        elif not username.isalnum():
            raise ValidationError("Username must only contain letters and numbers")
        elif User.query.filter_by(username=username).first():
            raise ValidationError("Username already exists")
        elif ManagerCreationRequests.query.filter_by(username=username).first():
            raise ValidationError("Manager request with username {} already exists,"
                                  "wait for admin approval".format(username))

    @validates('email')
    def validate_email(self, email):
        if User.query.filter_by(email=email).first():
            raise ValidationError("User with email {} already exists".format(email))
        elif ManagerCreationRequests.query.filter_by(email=email).first():
            raise ValidationError("Manager request with email {} already exists,"
                                  "wait for admin approval".format(email))

    @validates('password')
    def validate_pass(self, password):
        validate_password(password)

    @post_load()
    def make_manager_request(self, data, **kwargs):
        try:
            username = data.get('username')
            username = clean(username)
            data['username'] = username
            return ManagerCreationRequests(**data)
        except TypeError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(str(e))
        finally:
            del kwargs


class ProductImageSchema(Schema):
    """
    :class:`ProductImageSchema` class for serializing and deserializing ProductImage objects.

    Attributes
        - id (Int, optional): The ID of the product image. (read-only)
        - image_name (Str): The name of the product image.
        - image_path (Str, optional): The path of the product image. (read-only)
        - image_file (FileStorage, write-only): The file object of the product image.

    Methods
        - validate_image_file(image_file): Validates the image_file field.
        - make_product_image(data): Creates a ProductImage object from the serialized data.
    """

    class Meta:
        model = ProductImage
        fields = ('id', 'image_name', 'image_path', 'image_file', 'products')

    id = fields.Int(dump_only=True)
    image_name = fields.Str(dump_only=True)
    image_path = fields.Method('get_image_path', dump_only=True)
    image_file = fields.Raw(load_only=True, type='file', required=True)
    products = fields.Nested('ProductSchema', exclude=('image',))

    @validates('image_file')
    def validate_image_file(self, image_file: FileStorage) -> None:
        """
        Validates the image_file field.
        :param image_file: The image file to be validated.
        :return: Product Image object

        image_file is the file object of the image to be uploaded. It will come from the request.files object,
        so we can use all the attributes and methods of the FileStorage class.

        """
        if not image_file:
            raise ValidationError("Image file is required")
        elif image_file.filename == '':
            raise ValidationError("Image file is required")
        elif not image_file.content_type.startswith('image'):
            raise ValidationError("Uploaded file must be an image")
        elif image_file.content_length > 2 * 1024 * 1024:
            raise ValidationError("Image file must be less than 2MB")

    @staticmethod
    def get_image_path(obj):
        return 'static/images/{}'.format(obj.image_name)

    @post_load()
    def make_product_image(self, data,**kwargs):
        try:
            print("trying to load image")
            print(data)
            image_file = data.get('image_file')
            print(image_file)
            # uuid1().hex is a unique string which is usually safe, but we use secure_filename() to be extra safe
            image_name = secure_filename(uuid1().hex) + '.png'
            print(image_name)
            image = Image.open(image_file.stream)
            print(image)
            image.convert('RGB')
            image.thumbnail((300, 300))
            image.save('static/images/{}'.format(image_name))
            print("image_saved")
            data['image_name'] = image_name
            data.pop('image_file')
            return ProductImage(**data)
        except PIL.UnidentifiedImageError as e:
            raise ValidationError("Image file must be one of {}".format(['jpg', 'jpeg', 'png', 'webp']))
        except TypeError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(str(e))
