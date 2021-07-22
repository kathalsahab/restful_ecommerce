from ecom.utils import strict_list
from flask_restx import Resource, Namespace, reqparse

from . import controllers as c

api = Namespace(
    "Product Management", description="Endpoints related to Product management",
)


def product_update():

    parser = reqparse.RequestParser()

    parser.add_argument("product_id", type=int, location="json", required=True)
    parser.add_argument(
        "category_id", type=strict_list, location="json", required=False
    )
    parser.add_argument(
        "product_name", type=str, location="json", required=False, default=None
    )
    parser.add_argument(
        "product_desc", type=str, location="json", required=False, default=None
    )
    parser.add_argument(
        "product_price", type=int, location="json", required=False, default=None
    )
    parser.add_argument(
        "product_quantity", type=int, location="json", required=False, default=None
    )
    parser.add_argument(
        "product_image_path", type=int, location="json", required=False, default=None
    )

    return parser


product_update_params = product_update()


def create_product():
    parser = reqparse.RequestParser()
    parser.add_argument("product_name", type=str, location="json", required=True)
    parser.add_argument("category_id", type=strict_list, location="json", required=True)
    parser.add_argument(
        "product_desc", type=str, location="json", required=False, default=None
    )
    parser.add_argument(
        "product_price", type=str, location="json", required=False, default=None
    )
    parser.add_argument(
        "product_quantity", type=str, location="json", required=False, default=None
    )
    parser.add_argument(
        "product_image_path", type=str, location="json", required=False, default=None
    )

    return parser


create_product_params = create_product()


@api.route("/get_products", endpoint="products")
class Product(Resource):
    """Class for product data"""

    def get(self):
        "Get list of all products"

        return c.get_all_products()


@api.route("/product", endpoint="product_management")
class ProductManagement(Resource):
    """Class for product CRUD operations"""

    def get(self):
        """Get list of all products by category_id"""
        parser = reqparse.RequestParser()
        parser.add_argument("category_id", type=int, default=None, required=True)
        args = parser.parse_args()
        return c.get_product_list(args)

    @api.expect(create_product_params)
    def post(self):
        """Create a new product"""
        args = create_product_params.parse_args()
        return c.create_new_product(request_json=args)


@api.route("/product/edit", endpoint="product_edit")
class ProductEditDetails(Resource):
    """Class for product edit operations"""

    @api.expect(product_update_params)
    def put(self):

        args = product_update_params.parse_args()
        return c.update_product(args)

    def delete(self):
        """Delete an existing product"""
        parser = reqparse.RequestParser()
        parser.add_argument("product_id", type=int, location="args", required=True)

        args = parser.parse_args()
        return c.delete_product(args["product_id"])
