from flask import jsonify, request, make_response, Blueprint, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from database.models import Product, User, Category, CategoryRequest
from database.schema import ProductSchema, UserSchema, CategoryRequestSchema, ManagerRequestSchema
from error_log import logger
from mail import send_mail
from mail.templates import manager_created
from cache import cache
from scheduled_jobs.export import export_product_as_csv

manager_blueprint = Blueprint('manager', __name__)


@manager_blueprint.route('/create_manager_request', methods=['POST'])
def create_manager_request():
    manager_request_schema = ManagerRequestSchema(many=False)
    try:
        body = request.get_json()
        manager_request = manager_request_schema.load(body)
        db.session.add(manager_request)
        db.session.commit()
        send_mail(subject='Manager Request Created',
                  sender='admin@grocerystore.com',
                  recipients=[manager_request.email],
                  html_body=manager_created(manager_request.username))
        return make_response(jsonify({'message': 'Manager request created successfully, wait for approval'}), 200)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/get_products', methods=['GET'])
@cache.cached(timeout=60)
@jwt_required()
def get_products():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user.role.role_name == 'manager':
            return make_response(jsonify({'message': 'Forbidden'}), 403)
        products = Product.query.filter_by(added_by=get_jwt_identity()).all()
        if products:
            return make_response(jsonify({'message': 'Products fetched successfully',
                                          'products': ProductSchema().dump(products, many=True)}),
                                 200)
        else:
            return make_response(jsonify({'message': 'No products found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/request_category', methods=['POST'])
@jwt_required()
def request_category():
    category_request_schema = CategoryRequestSchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == 'manager':
            body = request.get_json()
            body["user_id"] = current_user.id
            body["request_type"] = 'add'
            if Category.query.filter_by(category_name=body["category_name"].lower()).first():
                return make_response(jsonify({'message': 'Category already exists with the name ' + body["category_name"]}), 400)
            elif CategoryRequest.query.filter_by(category_name=body["category_name"].lower()).first():
                return make_response(jsonify({'message': 'Category already requested with the name ' + body["category_name"]}), 400)
            else:
                category_request = category_request_schema.load(body)
                db.session.add(category_request)
                db.session.commit()
                return make_response(jsonify({'message': 'Category requested successfully, wait for approval'}), 200)
        else:
            return make_response(jsonify({'message': 'Only managers can request new categories'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_manager():
    user_schema = UserSchema()
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user.role.role_name == 'manager':
            return make_response(jsonify({'message': 'Forbidden'}), 403)
        products = Product.query.filter_by(added_by=user_id).all()
        user = user_schema.dump(user)
        user['products'] = ProductSchema().dump(products, many=True)
        return make_response(jsonify(user), 200)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/delete_category/<int:cat_id>',methods=['POST'])
@jwt_required()
def request_delete_category(cat_id):
    category_request_schema = CategoryRequestSchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        category = Category.query.get(cat_id)
        uncategorized = Category.query.filter_by(category_name='Uncategorized').first()
        if current_user.role.role_name == 'manager':
            if not category:
                return make_response(jsonify({'message': 'Category not found'}), 404)
            elif category.id == uncategorized.id:
                return make_response(jsonify({'message': 'You cannot delete this category'}), 400)
            elif category.id in [i.category_id for i in CategoryRequest.query.filter_by(request_type='delete').all()]:
                return make_response(jsonify({'message': 'Category deletion request already exists'}), 400)
            else:
                body = dict()
                body['user_id'] = current_user.id
                body['request_type'] = 'delete'
                body['category_id'] = category.id
                body['category_name'] = category.category_name
                body['category_description'] = category.category_description
                category_request = category_request_schema.load(body)
                db.session.add(category_request)
                db.session.commit()
                return make_response(jsonify(
                    {'message': 'Category deletion request created successfully, wait for approval'}), 200)
        else:
            return make_response(jsonify({'message': 'Only managers can request to delete a category.'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/update_category/<int:cat_id>',methods=['POST'])
@jwt_required()
def update_category(cat_id):
    category_request_schema = CategoryRequestSchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        category = Category.query.get(cat_id)
        uncategorized = Category.query.filter_by(category_name='Uncategorized').first()
        if current_user.role.role_name == 'manager':
            if not category:
                return make_response(jsonify({'message': 'Category not found'}), 404)
            elif category.id == uncategorized.id:
                return make_response(jsonify({'message': 'You cannot update this category'}), 400)
            elif category.id in [i.category_id for i in CategoryRequest.query.filter_by(request_type='update').all()]:
                return make_response(jsonify({'message': 'Category update request already exists'}), 400)
            else:
                body = request.get_json()
                body['user_id'] = current_user.id
                body['request_type'] = 'update'
                category_request = category_request_schema.load(body)
                db.session.add(category_request)
                db.session.commit()
                return make_response(jsonify(
                    {'message': 'Category update request created successfully, wait for approval'}), 200)
        else:
            return make_response(jsonify({'message': 'Only managers can request to update a category.'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)



@manager_blueprint.route('/export_product/<int:product_id>', methods=['POST'])
@jwt_required()
def request_product_csv(product_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == 'manager':
            product = Product.query.get(product_id)
            if not product:
                return make_response(jsonify({'message': 'Product not found'}), 404)
            elif product.added_by != current_user.id:
                return make_response(jsonify({'message': 'You cannot request csv for this product'}), 400)
            else:
                task = export_product_as_csv.delay(product_id)
                return make_response(jsonify({'message': 'CSV requested successfully, wait a moment','taskID':task.id}), 200)
        else:
            return make_response(jsonify({'message': 'Only managers can request csv for a product.'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/task_status/<string:task_id>', methods=['GET'])
@jwt_required()
def request_product_csv_status(task_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == 'manager':
            task = export_product_as_csv.AsyncResult(task_id)
            if task.state == 'PENDING':
                return make_response(jsonify({'message': 'Task pending'}), 200)
            elif task.state == 'SUCCESS':
                return make_response(jsonify({'message': 'Task completed','taskID':task.id}), 200)
            elif task.state == 'FAILURE':
                return make_response(jsonify({'message': 'Task failed'}), 400)
            else:
                return make_response(jsonify({'message': 'Task running'}), 200)
        else:
            return make_response(jsonify({'message': 'Only managers can request csv for a product.'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/csv_download/<string:product_id>', methods=['GET'])
@jwt_required()
def csv_download(product_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == 'manager':
            product = Product.query.get(product_id)
            if product:
                return send_file('/static/products/{}.csv'.format(product.id), as_attachment=True)
            else:
                return make_response(jsonify({'message': 'Product not found'}), 404)
        else:
            return make_response(jsonify({'message': 'Only managers can request csv for a product.'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)