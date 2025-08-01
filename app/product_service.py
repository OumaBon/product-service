from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import or_, func, and_
from .model import Product, Category, Brand, ProductVariant,ProductImage, db
from .schema import ProductSchema


class ProductService:
    @staticmethod
    def _paginate_query(query, page=None, per_page=None):
        """
        Internal helper for query pagination
        Args:
            query: SQLAlchemy query object
            page: Page number (1-based)
            per_page: Items per page
        Returns:
            Dictionary with paginated results and metadata
        """
        if page and per_page:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": paginated.items,
                "total": paginated.total,
                "page": paginated.page,
                "per_page": paginated.per_page
            }
        return {
            "items": query.all(),
            "total": query.count(),
            "page": 1,
            "per_page": None
        }

    @staticmethod
    def get_all_products(page=None, per_page=None):
        """Get products with optional pagination"""
        try:
            query = Product.query
            result = ProductService._paginate_query(query, page, per_page)
            return {
                "products": ProductSchema(many=True).dump(result["items"]),
                "pagination": {
                    "total": result["total"],
                    "page": result["page"],
                    "per_page": result["per_page"]
                }
            }, None
                
        except SQLAlchemyError as e:
            return None, {
                "error": "Database error",
                "message": str(e)
            } 
    
    # @staticmethod
    # def create_product(data):
    #     try:
    #         schema = ProductSchema()
    #         product_data = schema.load(data)

    #         # Handle or create brand
    #         brand = None
    #         if "brand" in data:
    #             brand = Brand.query.filter_by(name=data["brand"]["name"]).first()
    #             if not brand:
    #                 brand = Brand(**data["brand"])
    #                 db.session.add(brand)

    #         # Handle or create category
    #         category = None
    #         if "category" in data:
    #             category = Category.query.filter_by(name=data["category"]["name"]).first()
    #             if not category:
    #                 category = Category(**data["category"])
    #                 db.session.add(category)

    #         # Create product
    #         product = Product(
    #             name=product_data['name'],
    #             slug=product_data['slug'],
    #             description=product_data.get('description'),
    #             price=product_data['price'],
    #             brand=brand,
    #             category=category
    #         )
    #         db.session.add(product)
    #         db.session.flush()  # Generate product_id

    #         # Add images (if any)
    #         for img in data.get('images', []):
    #             image = ProductImage(image_url=img['image_url'], alt_text=img.get('alt_text'), product=product)
    #             db.session.add(image)

    #         # Add variants (if any)
    #         for var in data.get('variants', []):
    #             variant = ProductVariant(**var, product=product)
    #             db.session.add(variant)

    #         db.session.commit()

    #         return schema.dump(product), None, 201

    #     except IntegrityError as e:
    #         db.session.rollback()
    #         return None, {
    #             "error": "Integrity error",
    #             "message": "Duplicate entry or constraint violation. Check brand/category/product uniqueness."
    #         }, 400

    #     except SQLAlchemyError as e:
    #         db.session.rollback()
    #         return None, {
    #             "error": "Database error",
    #             "message": "Unexpected database error occurred."
    #         }, 500

    #     except Exception as e:
    #         return None, {
    #             "error": "Unknown error",
    #             "message": str(e)
    #         }, 500
    
    @staticmethod
    def create_product(data):
        try:
            schema = ProductSchema()
            product_data = schema.load(data)

            # Handle or create brand
            brand = None
            if "brand" in data:
                brand_data = data["brand"]
                brand = Brand.query.filter_by(name=brand_data.get("name")).first()
                if not brand:
                    brand = Brand(**brand_data)
                    db.session.add(brand)

            # Handle or create category
            category = None
            if "category" in data:
                category_data = data["category"]
                category = Category.query.filter_by(name=category_data.get("name")).first()
                if not category:
                    category = Category(**category_data)
                    db.session.add(category)

            # Create product (use attribute access instead of dict access)
            product = Product(
                name=product_data.name,
                slug=product_data.slug,
                description=getattr(product_data, 'description', None),
                price=product_data.price,
                brand=brand,
                category=category
            )
            db.session.add(product)
            db.session.flush()  # Generate product_id

            # Add images (if any)
            for img in data.get('images', []):
                image = ProductImage(
                    image_url=img.get('image_url'),
                    alt_text=img.get('alt_text'),
                    product=product
                )
                db.session.add(image)

            # Add variants (if any)
            for var in data.get('variants', []):
                variant = ProductVariant(product=product, **var)
                db.session.add(variant)

            db.session.commit()

            return schema.dump(product), None, 201

        except IntegrityError as e:
            db.session.rollback()
            return None, {
                "error": "Integrity error",
                "message": "Duplicate entry or constraint violation. Check brand/category/product uniqueness."
            }, 400

        except SQLAlchemyError as e:
            db.session.rollback()
            return None, {
                "error": "Database error",
                "message": "Unexpected database error occurred."
            }, 500

        except Exception as e:
            return None, {
                "error": "Unknown error",
                "message": str(e)
            }, 500

    
    @staticmethod
    def get_product_by_id(product_id):
        """Get a single product by ID"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return None, "Product not found"
            return ProductSchema().dump(product), None
        except SQLAlchemyError as e:
            return None, str(e)

    @staticmethod
    def update_product(product_id, update_data):
        """Update an existing product"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return None, "Product not found"

            # Handle basic fields
            if 'name' in update_data:
                product.name = update_data['name']
            if 'slug' in update_data:
                product.slug = update_data['slug']
            if 'description' in update_data:
                product.description = update_data['description']
            if 'price' in update_data:
                product.price = update_data['price']
            
            # Handle relationships - ensure they exist first
            if 'brand_id' in update_data and update_data['brand_id']:
                from .model import Brand
                brand = Brand.query.get(update_data['brand_id'])
                if not brand:
                    return None, "Brand not found"
                product.brand_id = update_data['brand_id']
            
            if 'category_id' in update_data and update_data['category_id']:
                from .model import Category
                category = Category.query.get(update_data['category_id'])
                if not category:
                    return None, "Category not found"
                product.category_id = update_data['category_id']
            
            # Update the timestamp
            product.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return ProductSchema().dump(product), None
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_product(product_id):
        """Delete a product"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return None, "Product not found"
            
            db.session.delete(product)
            db.session.commit()
            return {"message": "Product deleted successfully"}, None
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, str(e)


    @staticmethod
    def get_products_by_category(category_slug, page=1, per_page=10, min_price=None, 
                                max_price=None, in_stock=None, search=None):
        """Get products by category slug with optional filters"""
        try:
            category = Category.query.filter_by(slug=category_slug).first()
            if not category:
                return None, "Category not found"

            query = Product.query.filter_by(category_id=category.id)

            # Apply price filters
            if min_price is not None:
                query = query.filter(Product.price >= float(min_price))
            if max_price is not None:
                query = query.filter(Product.price <= float(max_price))

            # Convert in_stock to string and check
            if str(in_stock).lower() == 'true':
                query = query.join(Product.variants)\
                            .group_by(Product.id)\
                            .having(func.sum(ProductVariant.stock) > 0)

            # Search by name or description
            if search:
                query = query.filter(
                    or_(
                        Product.name.ilike(f"%{search}%"),
                        Product.description.ilike(f"%{search}%")
                    )
                )

            # Paginate result
            products = query.paginate(page=page, per_page=per_page, error_out=False)
            schema = ProductSchema(many=True)
            return schema.dump(products.items), None

        except SQLAlchemyError as e:
            return None, str(e)


    @staticmethod
    def get_products_by_brand(brand_id, page=1, per_page=10, min_price=None, max_price=None, 
                            in_stock=None, sort_by='created_at', sort_order='desc'):
        """Get products by brand ID with filters and sorting"""
        try:
            brand = Brand.query.get(brand_id)
            if not brand:
                return None, "Brand not found"

            query = Product.query.filter_by(brand_id=brand_id)

            # Apply filters
            if min_price is not None:
                query = query.filter(Product.price >= min_price)
            if max_price is not None:
                query = query.filter(Product.price <= max_price)
            if in_stock:
                query = query.join(Product.variants)\
                            .group_by(Product.id)\
                            .having(db.func.sum(ProductVariant.stock) > 0)

            # Apply sorting
            sort_column = getattr(Product, sort_by, None)
            if sort_column is not None:
                if sort_order == 'desc':
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)
            else:
                # Default sorting if invalid column provided
                query = query.order_by(Product.created_at.desc())

            products = query.paginate(page=page, per_page=per_page, error_out=False)
            schema = ProductSchema(many=True)
            return schema.dump(products.items), None
        except SQLAlchemyError as e:
            return None, str(e)

    @staticmethod
    def search_products(search_term, page=1, per_page=10, category_id=None, brand_id=None,
                       min_price=None, max_price=None, in_stock=None):
        """Search products with various filters"""
        try:
            query = Product.query

            # Basic search across name and description
            if search_term:
                query = query.filter(
                    or_(
                        Product.name.ilike(f'%{search_term}%'),
                        Product.description.ilike(f'%{search_term}%')
                    )
                )

            # Additional filters
            if category_id:
                query = query.filter_by(category_id=category_id)
            if brand_id:
                query = query.filter_by(brand_id=brand_id)
            if min_price is not None:
                query = query.filter(Product.price >= min_price)
            if max_price is not None:
                query = query.filter(Product.price <= max_price)
            if in_stock:
                query = query.join(Product.variants)\
                            .group_by(Product.id)\
                            .having(db.func.sum(ProductVariant.stock) > 0)

            # Default sorting by relevance (could be enhanced)
            query = query.order_by(Product.created_at.desc())

            products = query.paginate(page=page, per_page=per_page, error_out=False)
            schema = ProductSchema(many=True)
            return schema.dump(products.items), None
        except SQLAlchemyError as e:
            return None, str(e)
















