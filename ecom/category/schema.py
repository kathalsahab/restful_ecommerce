"""Category Schema
"""
from marshmallow import fields
from ecom.extensions import mm
from ecom.design.models import Category


class CategorySchema(mm.SQLAlchemySchema):
    class Meta:
        model = Category

    category_id = mm.auto_field()
    category_name = mm.auto_field()
    category_desc = mm.auto_field()
    created_date = mm.auto_field()
    is_active = mm.auto_field()
    category_parent_id = mm.auto_field()
    childs = fields.Nested("self", many=True, exclude=("childs",))
    category_parent_name = fields.String()


category_schema_child_list = CategorySchema(many=True)
category_schema_child_list_single = CategorySchema()
