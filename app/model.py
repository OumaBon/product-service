import uuid
from datetime import datetime
from .import db 



class Brand(db.Model):
    __tablename__="brands"
    id  = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String, nullable=False)
    
    products = db.relationship("Product", back_populates='brand')


class Category(db.Model):
    __tablename__="categories"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False, index=True, unique=True)
    slug = db.Column(db.String, nullable=False, index=True, unique=True)
    parent_id = db.Column(db.String, db.ForeignKey('categories.id'), nullable=False)
    
    parent = db.relationship("Category", remote_side=[id], back_populates='subcategories')
    subcategories = db.relationship('Category', back_populates='parent', cascade="all, delete")
    products = db.relationship('Product', back_populates='category')
    
    
    
    
    
    

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, unique=True, nullable=False, index=True)
    slug = db.Column(db.String, unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.String, db.ForeignKey('categories.id'), nullable=True)
    brand_id =db.Column(db.String, db.ForeignKey('brands.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = db.relationship('Category', back_populates='products')
    brand = db.relationship('Brand', back_populates='products')
    variants = db.relationship('ProductVariant', back_populates='product', cascade="all, delete-orphan")
    images = db.relationship('ProductImage', back_populates='product', cascade="all, delete-orphan")


class ProductVariant(db.Model):
    __tablename__="product_variants"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String, db.ForeignKey('products.id'), nullable=False)
    sku = db.Column(db.String, nullable=False, unique=True)
    color=db.Column(db.String)
    size = db.Column(db.String)
    stock = db.Column(db.Integer, nullable=False)
    price_override=db.Column(db.Numeric(10, 2),  nullable=True)
    
    product = db.relationship('Product', back_populates='variants')
    

class ProductImage(db.Model):
    __tablename__="product_images"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String, db.ForeignKey('products.id'), nullable=False)
    image_url=db.Column(db.Text, nullable=False)
    alt_text =db.Column(db.String)
    
    product = db.relationship('Product', back_populates='images')
    

    