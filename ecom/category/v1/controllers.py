"""Category Management Controller."""
from flask.helpers import url_for
from sqlalchemy.exc import SQLAlchemyError

from ecom.design.models import (
    Category,
)
from ecom.utils import (
    RecordNotFound,
    Response,
    FieldMissing,
    CategoryAlreadyExists,
)
from ecom.constants import ERROR_IN_EXECUTION_QUERY,NEW_CATEGORY_REQUIRED_FIELDS
from ecom.extensions import db
from ..schema import (
    category_schema_child_list,
)

def get_all_categories():
    """Get list of all the category"""
    try:
        query = Category.query.filter(Category.is_active == True)
    except Exception as exc:
        return Response.failure(400, msg=ERROR_IN_EXECUTION_QUERY, payload=str(exc))
    return Response.success(category_schema_child_list.dump(query))


def get_category_list(args: dict):
    """List all the category with filters

    Args:
        args (dict): pagination and filter information

    Returns:
        list : list of user objects
    """

    category_name = args["category_name"]
    try:
        query = Category.query.filter(
            Category.is_active == True,
        ).order_by(Category.category_id.asc())
        if category_name is not None:
            query = query.filter(Category.category_name.like(f"%{category_name}%"))

    except Exception as exc:
        return Response.failure(400, ERROR_IN_EXECUTION_QUERY, payload=str(exc))

    return Response.success(
        data=category_schema_child_list.dump(query)
    )


def delete_category(category_id: int):
    """Delete an existing category

    Args:
        category_id (int): id of the user to be deleted

    Returns:
        str : Status of deletion
    """
    try:
        category = Category.lookup(category_id)

        if not category:
            raise RecordNotFound
        
        db.session.query(Category).filter(
            Category.category_id == category_id
        ).update({Category.is_active: False})
        db.session.commit()

        return Response.success("Category deleted successfully"), 204
    except RecordNotFound as re:
        return Response.failure(400, "Category does not exist", payload=str(re))
    except SQLAlchemyError as exc:
        return Response.failure(500, f"Error while submitting data", payload=str(exc))
    except Exception as exc:
        return Response.failure(500, "Failed to delete category", payload=str(exc))


def create_new_category(request_json):
    try:
        new_category_json_keys = request_json.keys()
        new_category_parent = None
        if NEW_CATEGORY_REQUIRED_FIELDS <= new_category_json_keys:
            if 'category_parent_id' in request_json.keys():
                print("Inside")
                new_category_parent = Category.get_category_by_single_id(
                    category_id=request_json["category_parent_id"]
                )

            new_category_parent_id = new_category_parent.category_id if new_category_parent is not None else None
            print("new_category_parent_id : ",new_category_parent_id)
            category = Category.create_category(
                category_name=request_json["category_name"],
                category_desc=(
                    request_json["category_desc"]
                    if "category_desc" in new_category_json_keys
                    else None
                ),
                parent_id=new_category_parent_id,
            )
            if not category:
                raise CategoryAlreadyExists

        else:
            raise FieldMissing

        return (
            Response.success(msg="New Categories Created"),
            201,
        )

    except RecordNotFound as re:
        return Response.success(data=[], msg=re)
    except CategoryAlreadyExists as cae:
        return Response.failure(error_code=400,payload=str(cae))
    except FieldMissing as exc:
        return Response.failure(
            error_code=400,
            msg="Required field in request does not exist!",
            payload=str(exc),
        )
    except SQLAlchemyError as exc:
        return Response.failure(
            error_code=400, msg="Error in execution of database query", payload=str(exc)
        )
    except Exception as exc:
        Response.failure(500, payload=str(exc))


def update_category(args):
    try:
        category_id = args["category_id"]
        new_category_parent_id = args["parent_cat_id"]
        old_category = Category.lookup(category_id=category_id)
        if not old_category:
            raise RecordNotFound
        old_category_name = old_category.category_name
        old_category_parent_id = old_category.category_parent_id
        old_category_desc = old_category.category_desc
        if (
            old_category_name == args["category_name"]
            and old_category_parent_id == new_category_parent_id
            and old_category_desc == args["category_desc"]
        ):
            return Response.success(msg="Everything is up to date.")
        
        Category.update_category(
            category_id=int(category_id),
            category_desc=args["category_desc"],
            category_name=args["category_name"],
            category_parent_id=new_category_parent_id,
        )

        return Response.success(msg="Category updated succesfully."), 204

    except RecordNotFound as re:
        return Response.failure(error_code=400, payload=str(re))
    except SQLAlchemyError as exc:
        return Response.failure(500, f"Error while submitting data", payload=str(exc))
    except Exception as exc:
        return Response.failure(500, payload=str(exc))