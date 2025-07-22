from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, validate

from .model import Product,ProductImage,Brand, Category, ProductVariant


class BrandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model=Brand
        load_instance =True
        include_fk = True
        
    name = auto_field(required=True, validate=validate.Length(min=12, max=100))
    description = auto_field(required=True, validate=validate.Length(min=12))
    products = fields.List(fields.Nested(lambda: ProductSchema(only=("id", "name", "slug"))), dump_only=True)   
    
    
class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
        include_fk = True
    name = auto_field(required=True, validate=validate.Length(min=12))
    parent = fields.Nested(lambda: CategorySchema(exclude=("subcategories",)), dump_only=True)
    subcategories = fields.List(fields.Nested(lambda: CategorySchema(exclude=("parent",))), dump_only=True)
    products = fields.List(fields.Nested(lambda: ProductSchema(only=("id", "name", "slug"))), dump_only=True)


class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product 
        load_instance = True
        include_fk = True
    
    name = auto_field(required=True, validate=validate.Length(min=6, max=100))
    slug=auto_field(required=True, validate=validate.Length(min=4, max=100))
    description=auto_field(required=True,validate=validate.Length(min=4, max=256))
    price = auto_field(required=True, validate=validate.Range(min=0))
    
    category = fields.Nested(CategorySchema(only=("id", "name")), dump_only=True)
    brand = fields.Nested(BrandSchema(only=("id", "name")), dump_only=True)
    variants = fields.List(fields.Nested(lambda: ProductVariantSchema(exclude=('product',))),dump_only=True)
    images = fields.List(fields.Nested(lambda: ProductImageSchema(exclude=("product",))), dump_only=True)
    

class ProductImageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductImage
        load_instance = True
        include_fk = True
    image_url = auto_field(required=True, validate=validate.Length(max=256))
    alt_text =auto_field(required=True, validate=validate.Length(min=10, max=256))
    product = fields.Nested(ProductSchema(only=("id", "name", "slug")), dump_only=True)
    
    
class ProductVariantSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductVariant
        load_instance = True
        include_fk = True
    sku = auto_field(required=True,validate=validate.Length(min=2,max=100))
    color =auto_field(required=True, validate=validate.Length(min=1, max=50))
    size = auto_field(required=True, validate=validate.Length(min=1, max=50))
    stock = auto_field(required=True, validate=validate.Range(min=0))
    price_override =auto_field(required=False)
    product=fields.Nested(ProductSchema(only=("id","name", "slug")), dump_only=True)



