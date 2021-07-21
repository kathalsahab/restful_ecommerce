from flask.globals import request
from flask_restx import Resource, Namespace, reqparse

from . import controllers as c

api = Namespace(
    "Category Management", description="Endpoints related to Category management",
)


def category_get_data():

    parser = reqparse.RequestParser()

    parser.add_argument("category_id", type=int, required=False)

    return parser


category_get_data_params = category_get_data()


def category_update():

    parser = reqparse.RequestParser()

    parser.add_argument("category_id", type=int, required=True)
    parser.add_argument("category_name", type=str, required=False)
    parser.add_argument("category_desc", type=str, required=False)
    parser.add_argument("parent_cat_id", type=int, required=False)

    return parser


category_update_params = category_update()


@api.route("/get_categories", endpoint="categories")
class Categories(Resource):
    """Class for category dropdown data"""
    def get(self):
        "Get list of all categories"

        return c.get_all_categories()


@api.route("/category", endpoint="category_management")
class CategoryManagement(Resource):
    """Class for category CRUD operations"""
    
    def put(self):
        """Get list of all categories with filters"""
        parser = reqparse.RequestParser()
        parser.add_argument("category_id", type=int, location="json", default=None)
        parser.add_argument("category_name", type=str, location="json", default=None)
        args = parser.parse_args()
        return c.get_category_list(args)

    def post(self):
        """Create a new category"""
        request_json = request.json
        return c.create_new_category(request_json)


@api.route("/category/edit", endpoint="category_edit")
class CategoryEditDetails(Resource):
    """Class for category edit operations"""

    @api.expect(category_update_params)
    def put(self):

        args = category_update_params.parse_args()
        return c.update_category(args)

    def delete(self):
        """Delete an existing category"""
        parser = reqparse.RequestParser()
        parser.add_argument("category_id", type=int, location="args", required=True)

        args = parser.parse_args()
        return c.delete_category(args["category_id"])

