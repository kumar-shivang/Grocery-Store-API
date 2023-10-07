from error_log import logger
from database import db
from database.schema import UserSchema
from database.models import User
from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/', methods=['POST'])
def create_user():
    user_schema = UserSchema()
    try:
        body = request.get_json()
        user = user_schema.load(body)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({'message': 'User created successfully'}), 201)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@user_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_user():
    user_schema = UserSchema()
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        return make_response(jsonify(user_schema.dump(user)), 200)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)
