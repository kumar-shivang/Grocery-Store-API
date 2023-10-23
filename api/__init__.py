from error_log import logger
from flask import Blueprint
from flask_jwt_extended import JWTManager

api = Blueprint('api', __name__)
jwt = JWTManager()


def init_api(app):
    from .userAPI import user_blueprint
    from .loginAPI import login_blueprint
    from .productAPI import manager_blueprint
    from .adminAPI import admin_blueprint
    from .imageAPI import image_blueprint
    api.register_blueprint(login_blueprint, url_prefix='/login')
    api.register_blueprint(user_blueprint, url_prefix='/user')
    api.register_blueprint(manager_blueprint, url_prefix='/manager')
    api.register_blueprint(admin_blueprint, url_prefix='/admin')
    api.register_blueprint(image_blueprint, url_prefix='/image')
    app.register_blueprint(api, url_prefix='/api')
    jwt.init_app(app)


def validate_user_credentials(body: dict):
    try:
        username = body['username']
        password = body['password']
    except KeyError as e:
        error = str(e).replace('\'', '')
        raise Exception(error + ' is required')
    if not username:
        raise Exception('Username is required')
    if not password:
        raise Exception('Password is required')
    from database.models import User
    user = User.query.filter_by(username=username).first()
    if not user:
        raise Exception('User does not exist')
    if not user.check_password(password):
        raise Exception('Password is incorrect')
    return user


@api.app_errorhandler(404)
def not_found(e):
    logger.error(e)
    return {'message': 'Not found'}, 404


@api.app_errorhandler(500)
def internal_server_error(e):
    logger.error(e)
    return {'message': 'Internal server error'}, 500
