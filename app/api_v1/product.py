from flask import request, jsonify
from marshmallow import ValidationError
from ..import db
from ..schema import ProductSchema,ProductVariantSchema, ProductImageSchema
from ..model import Product, Brand, Category, ProductVariant, ProductImage
import uuid

from . import api


@api.route('/product', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        product_schema = ProductSchema(session=db.session)
        
        # Validate main product data (returns a Product model instance)
        product_data = product_schema.load(data)
        
        # Handle brand
        brand = None
        if 'brand' in data:
            brand_data = data['brand']
            brand = Brand.query.filter_by(name=brand_data['name']).first()
            if not brand:
                brand = Brand(
                    name=brand_data['name'],
                    description=brand_data.get('description')
                )
                db.session.add(brand)
                db.session.flush()

        # Handle category
        category = None
        if 'category' in data:
            category_data = data['category']
            category = Category.query.filter_by(name=category_data['name']).first()
            if not category:
                category = Category(
                    name=category_data['name'],
                    slug=category_data['slug'],
                    parent_id=category_data.get('parent_id')
                )
                db.session.add(category)
                db.session.flush()

        # Create product (using dot notation)
        product = Product(
            name=product_data.name,      # ✅ Fixed: Using dot notation
            slug=product_data.slug,
            description=product_data.description,
            price=product_data.price,
            brand_id=brand.id if brand else None,
            category_id=category.id if category else None
        )
        db.session.add(product)
        db.session.flush()

        # Handle variants with SKU validation
        if 'variants' in data:
            for variant_data in data['variants']:
                if ProductVariant.query.filter_by(sku=variant_data['sku']).first():
                    db.session.rollback()
                    return jsonify({
                        "error": "Duplicate SKU",
                        "message": f"SKU {variant_data['sku']} already exists"
                    }), 400
                
                variant = ProductVariant(
                    product_id=product.id,
                    sku=variant_data['sku'],
                    color=variant_data['color'],
                    size=variant_data['size'],
                    stock=variant_data['stock'],
                    price_override=variant_data.get('price_override')
                )
                db.session.add(variant)

        # Handle images
        if 'images' in data:
            for image_data in data['images']:
                image = ProductImage(
                    product_id=product.id,
                    image_url=image_data['image_url'],
                    alt_text=image_data.get('alt_text')
                )
                db.session.add(image)

        db.session.commit()
        return product_schema.dump(product), 201

    except ValidationError as err:
        db.session.rollback()
        return jsonify({"error": "Validation error", "details": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server error", "message": str(e)}), 500