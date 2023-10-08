from error_log import logger
from database import db
from database.schema import OrderSchema
from database.models import User, Order, Product
from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

order_blueprint = Blueprint('order', __name__)


@order_blueprint.route('/place_order', methods=['POST'])
@jwt_required()
def place_order():
    order_schema = OrderSchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        body = request.get_json()
        if current_user.role.role_name=="user":
            body['user_id'] = current_user.id
            product = Product.query.get(body['product_id'])
            if product:
                if product.current_stock >= body['quantity']:
                    product.current_stock -= body['quantity']
                    db.session.add(product)
                    db.session.commit()
                else:
                    return make_response(jsonify({'message': 'Not enough stock available'}), 400)
            else:
                return make_response(jsonify({'message': 'Product not found'}), 404)
            order = order_schema.load(body)
            db.session.add(order)
            db.session.commit()
            return make_response(jsonify({'message': 'Order placed successfully',
                                          'order': order_schema.dump(order)}),
                                 201)
        else:
            return make_response(jsonify({'message': 'You are not authorized to place orders'}), 403)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@order_blueprint.route('/get_orders', methods=['GET'])
@jwt_required()
def get_orders():
    order_schema = OrderSchema(many=True)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name=="user":
            orders = Order.query.filter_by(user_id=current_user.id).all()
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
        if current_user.role.role_name=="user":
            order = Order.query.get(order_id)
            if order:
                if order.confirmed:
                    return make_response(jsonify({'message': 'Order already confirmed, cannot cancel'}), 400)
                elif order.user_id == current_user.id:
                    product = Product.query.get(order.product_id)
                    if product:
                        product.current_stock += order.quantity
                        db.session.add(product)
                        db.session.commit()
                    else:
                        return make_response(jsonify({'message': 'Product not found'}), 404)
                    db.session.delete(order)
                    db.session.commit()
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


