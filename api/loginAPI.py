from . import validate_user_credentials
from error_log import logger
from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import create_access_token


login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/user', methods=['POST'])
def user_login():
    try:
        body = request.get_json()
        user = validate_user_credentials(body)
        if not user.role.role_name == 'user':
            raise Exception('Only users can login here.')
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
            raise Exception('Only admins can login here.')
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@login_blueprint.route('/manager', methods=['POST'])
def manager_login():
    try:
        body = request.get_json()
        user = validate_user_credentials(body)
        if not user.role.role_name == 'manager':
            raise Exception('Only managers can login here.')
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)
