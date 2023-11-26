from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import create_access_token

from database.models import User, ManagerCreationRequests
from error_log import logger
from . import validate_user_credentials

login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/user', methods=['POST'])
def user_login():
    try:
        body = request.get_json()
        user = validate_user_credentials(body)
        if not user.role.role_name == 'user':
            return make_response(jsonify({'message': 'Only users can login here.'}), 403)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@login_blueprint.route('/admin', methods=['POST'])
def admin_login():
    try:
        print('admin login')
        body = request.get_json()
        print(body)
        user = validate_user_credentials(body)
        print(user.role.role_name)
        if not user.role.role_name == 'admin':
            return make_response(jsonify({'message': 'Only admins can login here.'}), 403)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@login_blueprint.route('/manager', methods=['POST'])
def manager_login():
    try:
        body = request.get_json()
        user = User.query.filter_by(username=body['username']).first()
        manager_request = ManagerCreationRequests.query.filter_by(username=body['username']).first()
        if not user:
            if not manager_request:
                return make_response(jsonify({'message': 'User does not exist'}), 404)
            else:
                return make_response(jsonify({'message': 'Manager request is pending approval'}), 403)
        if not user.check_password(body['password']):
            return make_response(jsonify({'message': 'Password is incorrect'}), 400)
        if not user.role.role_name == 'manager':
            return make_response(jsonify({'message': 'Only managers can login here.'}), 403)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)
