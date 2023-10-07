from error_log import logger
from database import db
from database.schema import ProductSchema, UserSchema
from database.models import Product, Role
from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

manager_blueprint = Blueprint('manager', __name__)


@manager_blueprint.route('/create_manager', methods=['POST'])
def create_manager():
    user_schema = UserSchema(many=False)
    try:
        body = request.get_json()
        manager_role = Role.query.filter_by(role_name='manager').first()
        if manager_role:
            body['role_id'] = manager_role.id
        else:
            return make_response(jsonify({'message': 'Manager role not found'}), 404)
        user = user_schema.load(body)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({'message': 'Manager created successfully. Please login to continue'}, 201))
    except Exception as e:
        # db.session.rollback()
        # db.session.flush()
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/get_products', methods=['GET'])
@jwt_required()
def get_products():
    try:
        products = Product.query.filter_by(added_by=get_jwt_identity()).all()
        if products:
            return make_response(jsonify({'message': 'Products fetched successfully',
                                          'products': ProductSchema.dump(products, many=True)}),
                                 200)
        else:
            return make_response(jsonify({'message': 'No products found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)
