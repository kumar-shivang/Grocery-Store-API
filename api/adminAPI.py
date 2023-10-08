from error_log import logger
from database import db
from database.schema import ProductSchema, UserSchema, CategoryRequestSchema
from database.models import Product, Role, User, CategoryRequest
from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/create_admin', methods=['POST']) #Admin is already created in the database, but this is how you would create one
def create_admin():
    user_schema = UserSchema(many=False)
    try:
        body = request.get_json()
        admin_role = Role.query.filter_by(role_name='admin').first()
        if admin_role:
            body['role_id'] = admin_role.id
        else:
            return make_response(jsonify({'message': 'Admin role not found'}), 404)
        user = user_schema.load(body)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({'message': 'Admin created successfully. Please login to continue'}, 201))
    except Exception as e:
        # db.session.rollback()
        # db.session.flush()
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/approve_category/<int:category_request_id>', methods=['PUT'])
@jwt_required()
def approve_category(category_request_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to approve categories'}), 403)
        category_request = CategoryRequest.query.get(category_request_id)
        if category_request:
            category = category_request.approve()
            db.session.add(category)
            db.session.commit()
            return make_response(jsonify({'message': 'Category {} approved successfully'.format(category.category_name)}), 200)
        else:
            return make_response(jsonify({'message': 'Category request not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/reject_category/<int:category_request_id>', methods=['PUT'])
@jwt_required()
def reject_category(category_request_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to reject categories'}), 403)
        category_request = CategoryRequest.query.get(category_request_id)
        if category_request:
            category_request.reject()
            db.session.commit()
            return make_response(jsonify({'message': 'Category request rejected successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Category request not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/get_category_requests', methods=['GET'])
@jwt_required()
def get_category_requests():
    category_request_schema = CategoryRequestSchema(many=True)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to view category requests'}), 403)
        category_requests = CategoryRequest.query.filter_by(approved=False).all()
        if category_requests:
            return make_response(jsonify({'message': 'Category requests fetched successfully',
                                          'category_requests': category_request_schema.dump(category_requests, many=True)}),
                                 200)
        else:
            return make_response(jsonify({'message': 'Category request list is empty'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


