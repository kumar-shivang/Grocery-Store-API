import bleach
from datetime import datetime
from marshmallow import Schema, fields, ValidationError, validates, post_load
from .models import User, Product, Category, Order, Role, CategoryRequest


class UserSchema(Schema):
    """
    UserSchema class for serializing and deserializing User objects.

    Attributes:
        id (Int, optional): The ID of the user. (read-only)
        username (Str): The username of the user.
        email (Email): The email address of the user.
        password (Str, write-only): The password of the user.
        role (RoleSchema, optional): The role of the user.

    Methods:
        validate_password(password): Validates the password field.
        validate_username(username): Validates the username field.
        make_user(data): Creates a User object from the serialized data.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role_id', 'role')

    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    password = fields.Str(load_only=True)
    role_id = fields.Int(load_only=True,required=False)
    role = fields.Nested("RoleSchema", exclude=('users',))

    @validates("password")
    def validate_password(self, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        elif not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one digit")
        elif not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase character")
        elif not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase character")

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
            return User(**data)
        except TypeError as e:
            raise ValidationError(str(e))
        finally:
            print(kwargs)


class RoleSchema(Schema):
    """
    The RoleSchema class is used to serialize and deserialize Role objects.

    :param Schema: Base class for defining schemas.
    :type Schema: class

    :ivar int id: The ID of the role.
    :ivar str role_name: The name of the role.
    :ivar str role_description: The description of the role.
    :ivar list users: The list of associated User objects.

    :meta class Meta: An inner class for defining metadata.
    :meta field model: The Role model class from the database.
    :meta field fields: The fields to include in serialization and deserialization.

    :raises ValidationError: If there is an error validating the data.

    :Example:

    role_schema = RoleSchema()

    # Serialize Role object
    data = role_schema.dump(role)
    print(data)

    # Deserialize data into Role object
    role = role_schema.load(data)
    print(role)
    """

    class Meta:
        model = Role
        fields = ('id', 'role_name', 'role_description', 'users')

    id = fields.Int(dump_only=True)
    role_name = fields.Str()
    role_description = fields.Str()
    # users = fields.Nested("UserSchema", many=True, exclude=('role',), dump_only=True)

    # @post_load
    # def make_role(self, data, **kwargs):
    #     try:
    #         return Role(**data)
    #     except TypeError as e:
    #         raise ValidationError(str(e))


class ProductSchema(Schema):
    """
    Schema for validating and deserializing Product objects.

    :param Schema: The base class for defining schemas.
    """

    class Meta:
        model = Product
        fields = ('id', 'name', 'rate', 'unit', 'description', 'current_stock', 'expiry_date', 'added_by', 'category_id', 'category')
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    name = fields.Str()
    rate = fields.Float()
    unit = fields.Str()
    description = fields.Str()
    current_stock = fields.Int()
    expiry_date = fields.Date(format='%Y-%m-%d')
    added_by = fields.Int(load_only=True)  # added_by is the user id of the user who added the product
    category_id = fields.Int(load_only=True,required=False)
    category = fields.Nested('CategorySchema', exclude=('products','added_on','last_updated'))

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
        if unit not in ['kg', 'litre', 'piece']:
            raise ValidationError("Product unit must be one of 'kg', 'litre', 'piece'")

    @validates('name')
    def validate_name(self, name):
        if len(name) < 3:
            raise ValidationError("Product name must be at least 3 characters long")
        elif not name.isalnum():
            raise ValidationError("Product name must only contain letters and numbers")
        elif Product.query.filter_by(name=name).first():
            raise ValidationError("Product with name {} already exists".format(name))

    @validates('description')
    def validate_description(self, description):
        if len(description) < 10:
            raise ValidationError("Product description must be at least 10 characters long")

    @validates('current_stock')
    def validate_current_stock(self, current_stock):
        if current_stock < 0:
            raise ValidationError("Current stock cannot be negative")

    @post_load()
    def make_product(self, data, **kwargs):
        try:
            print(data)
            if not data.get('category_id'):
                category = Category.query.filter_by(category_name='Uncategorized').first()
                data['category_id'] = category.id
            return Product(**data)
        except TypeError as e:
            raise ValidationError(str(e))


class CategorySchema(Schema):
    """
    Schema for serializing and deserializing Category objects.

    Attributes:
        model (Category): The Category model associated with the schema
        id (Int, optional): The unique identifier of the category
        category_name (Str): The name of the category
        category_description (Str): The description of the category
        added_on (DateTime, optional): The date and time the category was added
        last_updated (DateTime, optional): The date and time the category was last updated
        products (Nested[ProductSchema], optional): The nested schema for deserializing and serializing Product objects
    """

    class Meta:
        model = Category
        fields = ('id', 'category_name', 'category_description', 'added_on', 'last_updated', 'products')

    id = fields.Int(dump_only=True)
    category_name = fields.Str()
    category_description = fields.Str()
    added_on = fields.DateTime(dump_only=True)
    last_updated = fields.DateTime(dump_only=True)
    products = fields.Nested('ProductSchema', exclude=('category',))

    @validates('category_name')
    def validate_category_name(self, category_name):
        if len(category_name) < 3:
            raise ValidationError("Category name must be at least 3 characters long")
        elif not category_name.isalnum():
            raise ValidationError("Category name must only contain letters and numbers")
        elif Category.query.filter_by(category_name=category_name).first():
            raise ValidationError("Category with name {} already exists".format(category_name))


    @validates('category_description')
    def validate_category_description(self, category_description):
        if len(category_description) < 10:
            raise ValidationError("Category description must be at least 10 characters long")

    @post_load()
    def make_category(self, data):
        try:
            return Category(**data)
        except TypeError as e:
            raise ValidationError(str(e))



class OrderSchema(Schema):
    """

    The `OrderSchema` class is responsible for serializing and deserializing Order data to and from JSON, as well as validating the structure and content of the data.

    Example usage:
    ```Python
    schema = OrderSchema()
    data = {
        'id': 1,
        'order_date': '2022-01-01',
        'order_details': 'Order details',
        'user': {
            'id': 1,
            'name': 'John Doe'
        }
    }
    # Serialize an Order object to JSON
    json_data = schema.dump(data)
    print(json_data)
    # {'id': 1, 'order_date': '2022-01-01T00:00:00', 'order_details': 'Order details', 'user': {'id': 1, 'name': 'John Doe'}}

    # Deserialize JSON data to an Order object
    order = schema.load(json_data)
    print(order)
    # <Order object>

    ```

    Class Attributes:
        - `id`: An Int field representing the order id. It is read-only and will not be serialized in the output JSON.

        - `order_date`: A DateTime field representing the date of the order. This field will be automatically validated and converted to/from a DateTime object.

        - `product`: A Nested field representing the associated Product. This field is excluded from the serialization of Category objects.

        - `category`: A Nested field representing the associated Category. This field is excluded from the serialization of Product objects.

    Methods:
        - `Meta`: The nested Meta class specifies the Order model and fields that should be serialized/deserialized. It is implemented using Marshmallow's `Meta` class.

        - `validates`: A decorator method that can be used to define additional validation logic for fields of the schema.

        - `post_load`: A decorator method that can be used to perform additional processing after deserialization.

        - `load`: A method that deserializes JSON data into an Order object. It takes a dictionary as input and returns a validated Order instance.

        - `dump`: A method that serializes an Order object into a JSON format. It takes an Order instance as input and returns a dictionary representing the serialized data.


    Note: This class requires the following imports:
    ```Python
    import bleach
    from datetime import datetime
    from marshmallow import Schema, fields, ValidationError, validates, post_load
    from .models import User, Product, Category, Order, Role, CategoryRequest
    ```
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
        if quantity < 1:
            raise ValidationError("Quantity must be greater than 0")

    @post_load
    def make_order(self, data):
        try:
            return Order(**data)
        except TypeError as e:
            raise ValidationError(str(e))


class CategoryRequestSchema(Schema):
    """
    This class represents the schema for validating and serializing category request data.

    :param Schema: The base class for defining a schema.
    :type Schema: Class
    :param fields: The fields to include in the schema.
    :type fields: Tuple

    :attribute id: The unique identifier of the category request.
    :type id: Int
    :attribute category_name: The name of the category.
    :type category_name: Str
    :attribute category_description: The description of the category.
    :type category_description: Str
    :attribute added_on: The datetime when the category request was added.
    :type added_on: DateTime
    :attribute last_updated: The datetime when the category request was last updated.
    :type last_updated: DateTime
    :attribute approved_at: The datetime when the category request was approved.
    :type approved_at: DateTime
    :attribute approved: Indicates whether the category request is approved or not.
    :type approved: Boolean
    """

    class Meta:
        model = CategoryRequest
        fields = ('id', 'category_name', 'category_description', 'added_on', 'approved_at', 'last_updated', 'approved')

    id = fields.Int(dump_only=True)
    category_name = fields.Str()
    category_description = fields.Str()
    added_on = fields.DateTime(default=datetime.utcnow)
    last_updated = fields.DateTime(dump_only=True)
    approved_at = fields.DateTime(dump_only=True)
    approved = fields.Boolean(dump_only=True)
