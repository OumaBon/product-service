from flask import jsonify, request

from ..product_service import ProductService


from . import api 


@api.route('/product', methods=["POST"])
def new_product():
    data = request.get_json()
    product, error = ProductService.create_product(data)
    if error:
        return jsonify({"error": "Server error", "message": error}), 500
    return jsonify(product), 201

@api.route('/product', methods=['GET'])
def get_products():
    """Get paginated list of products"""
    # Extract pagination parameters
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    
    # Validate parameters (basic sanity checks)
    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({
            "error": "Validation error", 
            "message": "Invalid pagination parameters"
        }), 400
    
    # Delegate all business logic to service
    result, error = ProductService.get_all_products(page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400 if error.get('error') == "Validation error" else 500
    
    return jsonify({
        "data": result["products"],
        "meta": {
            "pagination": {
                "total": result["pagination"]["total"],
                "page": result["pagination"]["page"],
                "per_page": result["pagination"]["per_page"],
                "total_pages": (result["pagination"]["total"] + per_page - 1) // per_page
            }
        }
    }), 200

@api.route('/product/<product_id>', methods=['PATCH'])
def update_product(product_id):
    data = request.get_json()
    result, error = ProductService.update_product(product_id, data)
    
    if error:
        return jsonify({
            "error": "Update failed",
            "message": error
        }), 400 if "not found" in error.lower() else 500
    
    return jsonify(result), 200

@api.route('/product/<product_id>', methods=["GET"])
def get_product(product_id):
    product, error = ProductService.get_product_by_id(product_id)
    if error:
        return jsonify({"error": error}), 404 if error == "Product not found" else 500
    return jsonify(product), 200

@api.route('/product/<id>', methods=["DELETE"])
def delete_product(id):
    result, error = ProductService.delete_product(id)

    if error:
        return jsonify({"error": error}), 404 if "not found" in error.lower() else 500

    return jsonify(result), 200

@api.route("/product/category/<string:category_slug>", methods=["GET"])
def get_products_by_category(category_slug):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    search = request.args.get("search")

    in_stock_param = request.args.get("in_stock")
    in_stock = in_stock_param.lower() == 'true' if isinstance(in_stock_param, str) else None

    products, error = ProductService.get_products_by_category(
        category_slug, page, per_page, min_price, max_price, in_stock, search
    )

    if error:
        return jsonify({"error": "Server error", "message": error}), 500

    return jsonify(products), 200


@api.route('/product/brand/<string:brand_id>', methods=['GET'])
def get_products_by_brand(brand_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Convert in_stock to boolean if present
    in_stock_param = request.args.get('in_stock')
    in_stock = None
    if in_stock_param is not None:
        in_stock = in_stock_param.lower() == 'true'

    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    products, error = ProductService.get_products_by_brand(
        brand_id=brand_id,
        page=page,
        per_page=per_page,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_order=sort_order
    )

    if error:
        return jsonify({"error": error}), 404
    return jsonify(products), 200


@api.route('/product/search', methods=["GET"])
def search_products():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    search_term = request.args.get("search")
    category_id = request.args.get("category_id")
    brand_id = request.args.get("brand_id")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    in_stock_param = request.args.get("in_stock")
    in_stock = in_stock_param.lower() == 'true' if isinstance(in_stock_param, str) else None

    products, error = ProductService.search_products(
        search_term=search_term,
        page=page,
        per_page=per_page,
        category_id=category_id,
        brand_id=brand_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock
    )

    if error:
        return jsonify({"error": "Server error", "message": error}), 500

    return jsonify(products), 200




















