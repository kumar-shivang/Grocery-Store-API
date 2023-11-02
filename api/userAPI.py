from error_log import logger
from database import db
from database.schema import UserSchema, OrderSchema, CategorySchema
from database.models import User, Order, Category, Role
from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/', methods=['POST'])
def create_user():
    user_schema = UserSchema()
    try:
        body = request.get_json()
        role_id = Role.query.filter_by(role_name='user').first().id
        body['role_id'] = role_id
        user = user_schema.load(body)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({'message': 'User created successfully'}), 201)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@user_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_user():
    user_schema = UserSchema()
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        user = user_schema.dump(user)
        orders = Order.query.filter_by(user_id=user_id).all()
        user['orders'] = OrderSchema(many=True).dump(orders)
        return make_response(jsonify(user), 200)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@user_blueprint.route('/get_category/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category_schema = CategorySchema(many=False)
    try:
        category = Category.query.get(category_id)
        if category:
            return make_response(jsonify({'message': 'Category fetched successfully',
                                          'category': category_schema.dump(category)}),
                                 200)
        else:
            return make_response(jsonify({'message': 'Category not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)
