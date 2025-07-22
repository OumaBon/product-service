from flask import jsonify, request 
from marshmallow import ValidationError



from . import api
from ..schema import ProductSchema
from ..model import Product, Category,Brand
from .. import db



@api.route('/product', methods=["POST"])
def new_product():
    try:
        data = request.get_json()
        category =Category.query.filter_by(slug=data.get('category_slug')).first()
        if not category:
            return jsonify({"error": "Category not Found"}), 404
        
        brand = Brand.query.filter_by(name=data.get('brand_name')).first()
        if not brand:
            return jsonify({"error": "Brand not found"}), 404
        
        data['category_id'] = category.id 
        data['brand_id'] = brand.id 
        
        schema = ProductSchema()
        product = schema.load(data, session=db.session)
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(schema.dump(product)), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



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