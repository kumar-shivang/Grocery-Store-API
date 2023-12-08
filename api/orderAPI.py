from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from database.models import User, Order, Product
from database.schema import OrderSchema
from error_log import logger
from cache import cache

order_blueprint = Blueprint('order', __name__)


@order_blueprint.route('/place_order', methods=['POST'])
@jwt_required()
def place_order():
    order_schema = OrderSchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        body = request.get_json()
        if current_user.role.role_name == "user":
            body['user_id'] = current_user.id
            product = Product.query.get(body['product_id'])
            if product:
                if product.current_stock >= body['quantity']:
                    order = order_schema.load(body)
                    return make_response(jsonify({'message': 'Order placed successfully',
                                                  'order': order_schema.dump(order)}),
                                         201)
                else:
                    return make_response(jsonify({'message': 'Not enough stock available'}), 400)
            else:
                return make_response(jsonify({'message': 'Product not found'}), 404)

        else:
            return make_response(jsonify({'message': 'You are not authorized to place orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/get_order/<int:order_id>', methods=['GET'])
@cache.cached(timeout=60)
@jwt_required()
def get_order(order_id):
    order_schema = OrderSchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        order = Order.query.get(order_id)
        if order:
            if current_user.role.role_name == "user" and order.user_id == current_user.id:
                return make_response(jsonify({'message': 'Order fetched successfully',
                                              'order': order_schema.dump(order)}),
                                     200)
            else:
                return make_response(jsonify({'message': 'You are not authorized to view this order'}), 403)
        else:
            return make_response(jsonify({'message': 'Order not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/unconfirmed', methods=['GET'])
@cache.cached(timeout=60)
@jwt_required()
def get_unconfirmed():
    order_schema = OrderSchema(many=True)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == "user":
            orders = Order.query.filter_by(user_id=current_user.id).filter_by(confirmed=False).all()
            if orders:
                return make_response(jsonify({'message': 'Orders fetched successfully',
                                              'orders': order_schema.dump(orders, many=True)}),
                                     200)
            else:
                return make_response(jsonify({'message': 'No orders found'}), 404)
        else:
            return make_response(jsonify({'message': 'You are not authorized to view orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/confirmed', methods=['GET'])
@cache.cached(timeout=60)
@jwt_required()
def get_confirmed():
    order_schema = OrderSchema(many=True)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == "user":
            orders = Order.query.filter_by(user_id=current_user.id).filter_by(confirmed=True).all()
            if orders:
                return make_response(jsonify({'message': 'Orders fetched successfully',
                                              'orders': order_schema.dump(orders, many=True)}),
                                     200)
            else:
                return make_response(jsonify({'message': 'No orders found'}), 404)
        else:
            return make_response(jsonify({'message': 'You are not authorized to view orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)




@order_blueprint.route('/cancel_order/<int:order_id>', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == "user":
            order = Order.query.get(order_id)
            if order:
                if order.confirmed:
                    return make_response(jsonify({'message': 'Order already confirmed, cannot cancel'}), 400)
                elif order.user_id == current_user.id:
                    order.delete()
                    return make_response(jsonify({'message': 'Order cancelled successfully'}), 200)
                else:
                    return make_response(jsonify({'message': 'You are not authorized to cancel this order'}), 403)
            else:
                return make_response(jsonify({'message': 'Order not found'}), 404)
        else:
            return make_response(jsonify({'message': 'You are not authorized to cancel orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/cancel_all', methods=['DELETE'])
@jwt_required()
def cancel_all():
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == "user":
            orders = Order.query.filter_by(user_id=current_user.id).filter_by(confirmed=False).all()
            if orders:
                for order in orders:
                    order.delete()
                return make_response(jsonify({'message': 'Orders cancelled successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'No orders found'}), 404)
        else:
            return make_response(jsonify({'message': 'You are not authorized to cancel orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/confirm_order/<int:order_id>', methods=['PUT'])
@jwt_required()
def confirm_order(order_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == "user":
            order = Order.query.get(order_id)
            if order:
                if order.user_id != current_user.id:
                    return make_response(jsonify({'message': 'You are not authorized to confirm this order'}), 403)
                if order.confirmed:
                    return make_response(jsonify({'message': 'Order already confirmed'}), 400)
                else:
                    order.confirm()
                    return make_response(jsonify({'message': 'Order confirmed successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Order not found'}), 404)
        else:
            return make_response(jsonify({'message': 'You are not authorized to confirm orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/confirm_all', methods=['PUT'])
@jwt_required()
def confirm_all():
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == "user":
            orders = Order.query.filter_by(user_id=current_user.id).filter_by(confirmed=False).all()
            if orders:
                for order in orders:
                    order.confirm()
                return make_response(jsonify({'message': 'Orders confirmed successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'No orders found'}), 404)
        else:
            return make_response(jsonify({'message': 'You are not authorized to confirm orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/update_order/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name == "user":
            order = Order.query.get(order_id)
            if order:
                if order.confirmed:
                    return make_response(jsonify({'message': 'Order already confirmed'}), 400)
                else:
                    body = request.get_json()
                    new_quantity = body['quantity']
                    order.update(new_quantity)
                    return make_response(jsonify({'message': 'Order updated successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Order not found'}), 404)
        else:
            return make_response(jsonify({'message': 'You are not authorized to update orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)
