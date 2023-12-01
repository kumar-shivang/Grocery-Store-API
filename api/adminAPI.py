from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from database.models import Role, User, CategoryRequest, Category, ManagerCreationRequests
from database.schema import UserSchema, CategoryRequestSchema, ManagerRequestSchema, CategorySchema
from error_log import logger
from mail import send_mail
from mail.templates import manager_approved, manager_rejected

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/create_admin', methods=[
    'POST'])  # Admin is already created in the database, but this is how you would create one
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
            return make_response(
                jsonify({'message': 'Category {} approved successfully'.format(category.category_name)}), 200)
        else:
            return make_response(jsonify({'message': 'Category request not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/reject_request/<int:request_id>', methods=['PUT'])
@jwt_required()
def reject_request(request_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to reject categories'}), 403)
        category_request = CategoryRequest.query.get(request_id)
        if category_request:
            category_request.reject()
            db.session.commit()
            return make_response(jsonify({'message': 'Category request rejected successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Category request not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/approve_delete_category/<int:id>', methods=['POST'])
@jwt_required()
def approve_delete_category(id):
    try:
        current_user = User.query.get(get_jwt_identity())
        category_request = CategoryRequest.query.get(id)
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to approve categories'}), 403)
        if category_request:
            category = category_request.approve()
            return make_response(jsonify({'message': 'Category deleted successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Category request not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/approve_update/<int:req_id>', methods=['POST'])
@jwt_required()
def approve_update(req_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        category_request = CategoryRequest.query.get(req_id)
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to approve categories'}), 403)
        if category_request:
            if category_request.category_name == 'Uncategorized':
                return make_response(jsonify({'message': 'Cannot update Uncategorized category'}), 400)
            duplicate_category = Category.query.filter_by(category_name=category_request.category_name).first()
            if duplicate_category and duplicate_category.id != category_request.category_id:
                return make_response(jsonify({'message': 'Category already exists with the name ' + duplicate_category.category_name}), 400)
            category = category_request.approve()
            return make_response(jsonify({'message': 'Category updated successfully'}), 200)
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
                                          'category_requests': category_request_schema.dump(category_requests,
                                                                                            many=True)}),
                                 200)
        else:
            return make_response(jsonify({'message': 'Category request list is empty'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/category/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to delete categories'}), 403)
        category = Category.query.get(category_id)
        if category and category.category_name != 'Uncategorized':
            products = category.products
            uncategorized = Category.query.filter_by(category_name='Uncategorized').first()
            if products:
                for product in products:
                    product.category_id = uncategorized.id
                db.session.add_all(products)
            db.session.delete(category)
            db.session.commit()
            return make_response(jsonify({'message': 'Category deleted successfully'}), 200)
        elif category and category.category_name == 'Uncategorized':
            return make_response(jsonify({'message': 'Cannot delete Uncategorized category'}), 403)
        else:
            return make_response(jsonify({'message': 'Category not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/update_category/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to update categories'}), 403)
        category = Category.query.get(category_id)
        body = request.get_json()
        if category:
            duplicate_category = Category.query.filter_by(category_name=body['category_name']).first()
            if duplicate_category.id != category_id:
                return make_response(jsonify({'message': 'Category already exists with the name ' + duplicate_category.category_name}), 400)
            if category_id == 1:
                return make_response(jsonify({'message': 'You cannot update this category'}), 400)
            if 'category_name' in body:
                print('updating category name')
                print('old name', category.category_name)
                print('new name', body['category_name'])
                category.category_name = body['category_name']
            if 'category_description' in body:
                print('updating category description')
                print('old description', category.category_description)
                print('new description', body['category_description'])
                category.category_description = body['category_description']
            db.session.add(category)
            db.session.commit()
            return make_response(jsonify({'message': 'Category updated successfully'}), 200)
        else:
            make_response(jsonify({'message': 'Category not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/get_manager_requests', methods=['GET'])
@jwt_required()
def get_manager_requests():
    manager_request_schema = ManagerRequestSchema(many=True)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to view manager requests'}), 403)
        manager_requests = ManagerCreationRequests.query.filter_by(approved=False).all()
        if manager_requests:
            return make_response(jsonify({'message': 'Manager requests fetched successfully',
                                          'manager_requests': manager_request_schema.dump(manager_requests,
                                                                                          many=True)}), 200)
        else:
            return make_response(jsonify({'message': 'Manager request list is empty'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/approve_manager_request/<int:manager_request_id>', methods=['PUT'])
@jwt_required()
def approve_manager(manager_request_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to approve manager requests'}), 403)
        manager_request = ManagerCreationRequests.query.get(manager_request_id)
        if manager_request:
            manager_request.approve()
            send_mail(
                'Manager Request Approved',
                'admin@grocerystore.com',
                [manager_request.email],
                html_body=manager_approved(manager_request.id, manager_request.username)
            )
            return make_response(jsonify({'message': 'Manager request approved successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Manager request not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/reject_manager_request/<int:manager_request_id>', methods=['PUT'])
@jwt_required()
def reject_manager(manager_request_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to reject manager requests'}), 403)
        manager_request = ManagerCreationRequests.query.get(manager_request_id)
        if manager_request:
            manager_request.reject()
            send_mail(
                'Manager Request Rejected',
                'admin@grocerystore.com',
                [manager_request.email],
                html_body=manager_rejected()
            )
            return make_response(jsonify({'message': 'Manager request rejected successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Manager request not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@admin_blueprint.route('/create_category', methods=['POST'])
@jwt_required()
def create_category():
    category_schema = CategorySchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name != 'admin':
            return make_response(jsonify({'message': 'You are not authorized to create categories'}), 403)
        body = request.get_json()
        category = category_schema.load(body)
        db.session.add(category)
        db.session.commit()
        return make_response(jsonify({'message': 'Category created successfully'}), 201)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)




