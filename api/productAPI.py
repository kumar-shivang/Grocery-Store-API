from .managerAPI import manager_blueprint
from .userAPI import user_blueprint
from error_log import logger
from database import db
from database.schema import ProductSchema
from database.models import Product
from flask import jsonify, request, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required


@user_blueprint.route('/get_products', methods=['GET'])
def get_products():
    product_schema = ProductSchema(many=True)
    try:
        products = Product.query.all()
        if products:
            return make_response(jsonify({'message': 'Products fetched successfully',
                                          'products': product_schema.dump(products, many=True)}),
                                 200)
        else:
            return make_response(jsonify({'message': 'No products found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/create_product', methods=['POST'])
@jwt_required()
def create_product():
    product_schema = ProductSchema(many=False)
    try:
        user_id = get_jwt_identity()
        body = request.get_json()
        body['added_by'] = user_id
        print(body)
        product = product_schema.load(body)
        db.session.add(product)
        db.session.commit()
        return make_response(jsonify({'message': 'Product created successfully',
                                      'product': product_schema.dump(product)}),
                             201)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/delete_product/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product:
            if product.added_by != get_jwt_identity():
                return make_response(jsonify({'message': 'You are not authorized to delete this product'}), 403)
            db.session.delete(product)
            db.session.commit()
            return make_response(jsonify({'message': 'Product deleted successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Product not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/add_stock/<int:product_id>', methods=['PUT'])
@jwt_required()
def add_stock(product_id):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product:
            if product.added_by != get_jwt_identity():
                return make_response(jsonify({'message': 'You are not authorized to add stock to this product'}), 403)
            body = request.get_json()
            quantity = body.get('quantity')
            if quantity:
                product.add_stock(quantity)
                return make_response(jsonify({'message': 'Stock added successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Quantity not provided'}), 400)
        else:
            return make_response(jsonify({'message': 'Product not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/update_price/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_price(product_id):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product:
            if product.added_by != get_jwt_identity():
                return make_response(jsonify({'message': 'You are not authorized to update price of this product'}), 403)
            body = request.get_json()
            price = body.get('price')
            if price:
                product.update_price(price)
                return make_response(jsonify({'message': 'Price updated successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Price not provided'}), 400)
        else:
            return make_response(jsonify({'message': 'Product not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)



@manager_blueprint.route('/update_expiry_date/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_expiry_date(product_id):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product:
            if product.added_by != get_jwt_identity():
                return make_response(jsonify({'message': 'You are not authorized to update expiry date of this product'}), 403)
            body = request.get_json()
            expiry_date = body.get('expiry_date')
            if expiry_date:
                product.update_expiry_date(expiry_date)
                return make_response(jsonify({'message': 'Expiry date updated successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Expiry date not provided'}), 400)
        else:
            return make_response(jsonify({'message': 'Product not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@manager_blueprint.route('/delete_product/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if product:
            if product.added_by != get_jwt_identity():
                return make_response(jsonify({'message': 'You are not authorized to delete this product'}), 403)
            db.session.delete(product)
            db.session.commit()
            return make_response(jsonify({'message': 'Product deleted successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Product not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


