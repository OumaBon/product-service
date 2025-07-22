from flask import jsonify, request 
from marshmallow import ValidationError



from . import api
from ..schema import ProductSchema
from ..model import Product
from .. import db


@api.route('/product', methods=["POST"])
def add_product():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    schema = ProductSchema()
    
    try:
        product = schema.load(data, session=db.session)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    db.session.add(product)
    db.session.commit()
    result = schema.dump(product)
    return jsonify({"error": result}), 201
    


@api.route('/product', methods=["GET"])
def get_products():
    schema = ProductSchema(many=True)
    products = Product.query.all()
    result = schema.dump(products)
    return jsonify({"products": result}), 200




@api.route('/product/<id>', methods=["GET"])
def get_product(id):
    schema = ProductSchema()
    product = Product.query.get_or_404(id)
    result = schema.dump(product)
    return jsonify({"product": result}), 200