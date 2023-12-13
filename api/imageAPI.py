import os

from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from database.models import User, ProductImage
from database.schema import ProductImageSchema
from error_log import logger

image_blueprint = Blueprint('image', __name__)


@image_blueprint.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    image_schema = ProductImageSchema(many=False)
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name not in ['admin', 'manager']:
            return make_response(jsonify({'message': 'You are not authorized to upload images'}), 403)
        files = request.files
        if 'image' not in files:
            return make_response(jsonify({'message': 'Image not found in request'}), 400)
        image_file = files['image']
        image = image_schema.load({'image_file': image_file})
        db.session.add(image)
        db.session.commit()
        return make_response(jsonify({'message': 'Image uploaded successfully',
                                      'image':{'id':image.id ,'url':"http://localhost:5000/static/images"+image.image_name}}), 201)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)


@image_blueprint.route('/delete/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if current_user.role.role_name not in ['admin', 'manager']:
            return make_response(jsonify({'message': 'You are not authorized to delete images'}), 403)
        image = ProductImage.query.get(image_id)
        if image:
            if image.image_name != 'default.png':
                os.remove(os.path.join(os.getcwd(), 'static', 'images', image.image_name))
                db.session.delete(image)
                db.session.commit()
                return make_response(jsonify({'message': 'Image deleted successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Cannot delete default image'}), 403)
        else:
            return make_response(jsonify({'message': 'Image not found'}), 404)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({'message': str(e)}), 400)
