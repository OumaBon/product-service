from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, validate, validates, ValidationError
from .model import Product, ProductImage, Brand, Category, ProductVariant
from . import db



# Helper for avoiding circular imports
def lazy_nested(field_name, **kwargs):
    return fields.Nested(lambda: globals()[field_name], **kwargs)

# --------------------------
# Non-circular schemas first
# --------------------------

class BrandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Brand
        load_instance = True
        sqla_session = db.session 
        exclude = ("products","id")  # Avoid circular reference

    name = auto_field(required=True, validate=validate.Length(max=100))
    description = auto_field(validate=validate.Length(max=500))  # Now nullable=True in model


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
        sqla_session = db.session 
        exclude = ("products", "subcategories", 'id', 'parent_id')  # Avoid circular references

    name = auto_field(required=True, validate=validate.Length(max=100))
    slug = auto_field(required=True, validate=validate.Length(max=100))
    parent_id = auto_field(required=False)  # Now nullable=True in model


class ProductVariantSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductVariant
        load_instance = True
        sqla_session = db.session 
        exclude = ("product",'id')  # Avoid circular reference

    sku = auto_field(required=True, validate=validate.Length(max=50))
    color = auto_field(validate=validate.Length(max=50))
    size = auto_field(validate=validate.Length(max=20))
    stock = auto_field(required=True)
    price_override = auto_field()  # Nullable


class ProductImageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductImage
        load_instance = True
        sqla_session = db.session 
        exclude = ("product",'id')  # Avoid circular reference

    image_url = auto_field(required=True)
    alt_text = auto_field(validate=validate.Length(max=100))  # Nullable


# --------------------------
# Now define ProductSchema (depends on others)
# --------------------------

class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        sqla_session = db.session 
        exclude = ("id",'category_id', 'brand_id')
        

    name = auto_field(required=True, validate=validate.Length(max=100))
    slug = auto_field(required=True, validate=validate.Length(max=100))
    description = auto_field(required=True)
    price = auto_field(required=True)
    category_id = auto_field(required=False)  # Nullable
    brand_id = auto_field(required=False)  # Nullable

    # Nested relationships (avoid circular references)
    brand = fields.Nested(BrandSchema, required=False)
    category = fields.Nested(CategorySchema, required=False)
    variants = fields.List(fields.Nested(ProductVariantSchema), required=False)
    images = fields.List(fields.Nested(ProductImageSchema), required=False)