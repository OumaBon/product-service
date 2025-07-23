from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
from flask import current_app

from .model import Product, ProductVariant,ProductImage
from .schema import ProductSchema
from . import db


class ProductService:
    @staticmethod
    def create_product(data):
        """Create a new product with variants and images.

        Args:
            data (dict): Product data including variants and images if available

        Returns:
            tuple: (product_data, error) where product_data is the created product data 
                   or None if error occurred, and error is None or a dictionary with error details
        """
        try:
            schema = ProductSchema()
            product_data = schema.load(data)
            
            product = Product(
                id=str(uuid4()),
                name=product_data['name'],
                slug=product_data['slug'],
                description=product_data['description'],
                price=product_data['price'],
                category_id=product_data.get('category_id'),
                brand_id=product_data.get('brand_id')
            )
            
            if 'variants' in product_data:
                for variant_data in product_data['variants']:
                    variant = ProductVariant(
                        id=str(uuid4()),
                        sku=variant_data['sku'],
                        color=variant_data.get('color'),
                        size=variant_data.get('size'),
                        stock=variant_data['stock'],
                        price_override=variant_data.get('price_override'),
                    )
                    product.variants.append(variant)
            
            if "images" in product_data:
                for image_data in product_data['images']:
                    image = ProductImage(
                        id=str(uuid4()),
                        image_url=image_data['image_url'],
                        alt_text=image_data.get('alt_text')
                    )
                    product.images.append(image)
           
            db.session.add(product)
            db.session.commit()
            return schema.dump(product), None
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Integrity error creating product: {str(e)}")
            return None, {
                "error": "Database integrity error",
                "details": "Possible duplicate slug, SKU, or invalid reference"
            }
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating product: {str(e)}")
            return None, {
                'error': 'Failed to create product',
                'details': str(e)
            }
    
    
    @staticmethod
    def get_product_by_id(product_id):
        """_summary_

        Args:
            product_id (_type_): _description_
        """
        
        try:
            product = db.session.get(Product, product_id)
            if not product:
                return None, {'error': 'Product not found'}
            
            schema = ProductSchema()
            return schema.dump(product), None
        except Exception as e:
            current_app.logger.error(f'Error fetching product {product_id}: {str(e)}')
            return None, {
                'error': 'Failed to fetch product',
                'details': str(e)
            }
    
    @staticmethod
    def get_products(page=1, per_page=20):
        """_summary_

        Args:
            page (int, optional): _description_. Defaults to 1.
            per_page (int, optional): _description_. Defaults to 20.
        """
        
        try:
            paginated_products = Product.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            schema =ProductSchema(exclude=('variants', 'images'), many=True)
            return {
                'products': schema.dump(paginated_products.items),
                'total': paginated_products.total,
                'pages': paginated_products.pages,
                'current_page': paginated_products.page
            }, None
        except Exception as e:
            current_app.logger.error(f'Error fetching products: {str(e)}')
            return None, {
                'error': 'Failed to fetch products'
            }
    
    
    @classmethod
    def update_product(product_id, data):
        """_summary_

        Args:
            product_id (_type_): _description_
            data (_type_): _description_
        """
        try:
            product = db.session.get(Product, product_id)
            if not product:
                return None, {'error': 'Product not found'}
            
            schema = ProductSchema(partial=True)
            product_data=schema.load(data)
            
            for field in ['name', 'slug', 'description', 'price', 'category_id', 'brand_id']:
                if field in product_data:
                    setattr(product, field, product_data[field])
            
            if "variants" in product_data:
                existing_variants = {v.id: v for v in product.variants}
                updated_variants = []
                
                for variant_data in product_data['variants']:
                    if 'id' in variant_data and variant_data['id'] in existing_variants:
                        variant = existing_variants[variant_data['id']]
                        for field in ['sku', 'color', 'size', 'stock', 'price_override']:
                            if field in variant_data:
                                setattr(variant, field, variant_data[field])
                        updated_variants.append(variant)
                    else:
                        variant=ProductVariant(
                            id=str(uuid4()),
                            product_id=product.id,
                            sku = variant_data['sku'],
                            color = variant_data.get('color'),
                            size = variant_data.get('size') 
                        )
                        updated_variants.append(variant)
                        
                for variant in product.variants:
                    if variant not in updated_variants:
                        db.session.delete(variant)
                        
                product.variants = updated_variants
                
                if "images" in product_data:
                    existing_images = {i.id: i for i in product.images}
                    updated_images = []
                    
                    for image_data in product_data['images']:
                        if 'id' in image_data and image_data['id'] in existing_images:
                            image = existing_images[image_data['id']]
                            for field in ['image_url', 'alt_text']:
                                if field in image_data:
                                    setattr(image, field, image_data[field])
                            updated_images.append(image)
                        else:
                            image = ProductImage(
                                id = str(uuid4()),
                                product_id = product.id,
                                image_url = image_data['image_url'],
                                alt_text = image_data.get('alt_text')
                            )
                            updated_images.append(image)
                    
                    for image in product.images:
                        if image not in updated_images:
                            db.session.delete(image)
                    
                    product.images = updated_images 
                
                product.updated_at = datetime.utcnow()
                db.session.commit()
                return schema.dump(product), None
            
        except IndentationError as e:
            db.session.rollback()
            current_app.logger.error(f"Integrity error updating product: {str(e)}")
            return None, {
                "error": 'Database integrity error',
                "details": 'Possible duplicates slug, SKU, or invalid references'
            }
        except Exception as err:
            db.session.rollback()
            current_app.logger.error(f"Error updating product: {str(err)}")
            return None, {
                'error': 'Failed to update product',
                'details': str(err)
            }
    
    @staticmethod
    def delete_product(product_id):
        """_summary_

        Args:
            product_id (_type_): _description_
        """
        try:
            product = db.session.get(Product, product_id)
            if not product:
                return None, {'error': "Product not found"}
            
            db.session.delete(product)
            db.session.commit()
            return {"message": 'Product deleted succefully'}, None
        except Exception as err:
            db.session.rollback()
            current_app.logger.error(f'Error deleting product:{str(err)}')
            return None, {
                'error': "Failed to delete product",
                'details': str(err)
            }
    
    @staticmethod
    def search_products(query, page=1, per_page=20):
        """_summary_

        Args:
            query (_type_): _description_
            page (int, optional): _description_. Defaults to 1.
            per_page (int, optional): _description_. Defaults to 20.
        """
        try:
            search = f"%{query}%"
            paginated_products = Product.query.filter(
                (Product.name.ilike(search)) |
                (Product.description.ilike(search))
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            schema =ProductSchema(exclude=('variants','images'), many=True)
            return {
                'products': schema.dump(paginated_products.items),
                'total': paginated_products.total,
                'pages': paginated_products.pages,
                'current_page': paginated_products.page
            }, None 
        except Exception as err:
            current_app.logger.error(f'Error searching products: {str(err)}')
            return None, {
                'error': 'Failed to search products',
                'details': str(err)
            }
    
    @staticmethod
    def get_products_by_category(category_id, page=1, per_page=20):
        """_summary_

        Args:
            category_id (_type_): _description_
            page (int, optional): _description_. Defaults to 1.
            per_page (int, optional): _description_. Defaults to 20.
        """
        try:
            paginated_products = Product.query.filter_by(
                category_id=category_id
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            schema = ProductSchema(exclude=('variants', 'images'), many=True)
            return {
                'products': schema.dump(paginated_products.items),
                'total': paginated_products.total,
                "pages": paginated_products.pages,
                "current_page": paginated_products.page 
            }, None
        except Exception as err:
            current_app.logger.error(f'Error fetching products by category: {str(err)}')
            return None, {
                'error': 'Failed to fetch products by category',
                'details': str(err)
            }
    
    @staticmethod 
    def get_products_by_brand(brand_id, page=1, per_page=20):
        """_summary_

        Args:
            brand_id (_type_): _description_
            page (int, optional): _description_. Defaults to 1.
            per_page (int, optional): _description_. Defaults to 20.
        """
        try:
            paginated_products = Product.query.filter_by(
                brand_id=brand_id
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            schema = ProductSchema(exclude=('variants', 'images'), many=True)
            return {
                'products': schema.dump(paginated_products.items),
                'total': paginated_products.total,
                'pages': paginated_products.pages,
                'current_page': paginated_products.page 
            }, None 
        except Exception as err:
            current_app.logger.error(f'Error fetching products by brand: {str(err)}')
            return None, {
                'error': 'Failed to fetch products by brand',
                'details': str(err)
            }