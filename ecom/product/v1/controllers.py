"""Product Management Controller."""
from operator import and_
from flask.helpers import url_for
from sqlalchemy.exc import SQLAlchemyError

from ecom.design.models import (
    Category,
    CategoryToProductMap,
    Product,
)
from ecom.utils import (
    RecordNotFound,
    Response,
    FieldMissing,
    CategoryAlreadyExists,
)
from ecom.constants import ERROR_IN_EXECUTION_QUERY
from ecom.extensions import db
from ..schema import product_schema_list


def get_all_products():
    """Get list of all the category"""
    try:
        query = Product.query.filter(Product.is_active == True).all()
    except Exception as exc:
        return Response.failure(400, msg=ERROR_IN_EXECUTION_QUERY, payload=str(exc))
    return Response.success(product_schema_list.dump(query))


def get_product_list(args: dict):
    """List all the products with filters

    Args:
        args (dict): pagination and filter information

    Returns:
        list : list of user objects
    """
    category_id = args["category_id"]
    try:
        query = (
            db.session.query(Product)
            .filter(Product.is_active == True)
            .join(
                CategoryToProductMap,
                and_(
                    CategoryToProductMap.product_id == Product.product_id,
                    CategoryToProductMap.category_id == category_id,
                ),
            )
        )

    except Exception as exc:
        return Response.failure(400, ERROR_IN_EXECUTION_QUERY, payload=str(exc))

    return Response.success(data=product_schema_list.dump(query))


def delete_product(product_id: int):
    """Delete an existing category

    Args:
        category_id (int): id of the user to be deleted

    Returns:
        str : Status of deletion
    """
    try:
        product = Product.lookup(product_id)

        if not product:
            raise RecordNotFound

        db.session.query(Product).filter(Product.product_id == product_id).update(
            {Product.is_active: False}
        )
        db.session.commit()

        return Response.success("Category deleted successfully"), 204
    except RecordNotFound as re:
        return Response.failure(400, "Category does not exist", payload=str(re))
    except SQLAlchemyError as exc:
        return Response.failure(500, f"Error while submitting data", payload=str(exc))
    except Exception as exc:
        return Response.failure(500, "Failed to delete category", payload=str(exc))


def create_new_product(request_json):
    try:
        product = Product.create_product(
            product_name=request_json["product_name"],
            product_desc=request_json["product_desc"],
            product_image_URI=request_json["product_image_path"],
            product_price=request_json["product_price"],
            product_quantity=request_json["product_quantity"],
        )

        errors = list()
        for category_id in request_json["category_id"]:
            category_to_product_map = CategoryToProductMap.create_category_to_product_map(
                category_id=category_id, product_id=product.product_id
            )
            if category_to_product_map is False:
                errors.append(f"Category with category_id: {category_id} not exists.")
        if len(errors) > 0:
            return Response.success(
                data=errors,
                msg="New Products Created and Mapped with Categories Other than not existing category",
            )

        return (
            Response.success(msg="New Products Created and Mapped with Categories"),
            201,
        )
    except SQLAlchemyError as exc:
        return Response.failure(
            error_code=400, msg="Error in execution of database query", payload=str(exc)
        )
    except Exception as exc:
        Response.failure(500, payload=str(exc))


def update_product(args):
    try:
        product_id = args["product_id"]
        old_product = Product.lookup(product_id=product_id)
        if not old_product:
            raise RecordNotFound

        product = Product.update_product(
            product_id=product_id,
            product_name=args["product_name"],
            product_desc=args["product_desc"],
            product_image_URI=args["product_image_path"],
            product_price=args["product_price"],
            product_quantity=args["product_quantity"],
        )
        errors = list()
        if args["category_id"] is not None:
            for category_id in args["category_id"]:
                category_to_product_map = CategoryToProductMap.create_category_to_product_map(
                    category_id=category_id, product_id=product.product_id
                )
                if category_to_product_map is False:
                    errors.append(
                        f"Category with category_id: {category_id} not exists."
                    )
            if len(errors) > 0:
                return Response.success(
                    data=errors,
                    msg="New Products Created and Mapped with Categories Other than not existing category",
                )

        return Response.success(msg="Category updated succesfully."), 204

    except RecordNotFound as re:
        return Response.failure(error_code=400, payload=str(re))
    except SQLAlchemyError as exc:
        return Response.failure(500, "Error while submitting data", payload=str(exc))
    except Exception as exc:
        return Response.failure(500, payload=str(exc))
