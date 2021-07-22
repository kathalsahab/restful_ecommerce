from ecom.extensions import mm

from ecom.design.models import Category


class CategorySchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        ordered = True

    category_id = mm.auto_field()
    category_name = mm.auto_field()
    category_desc = mm.auto_field()
    category_parent_id = mm.auto_field()
    created_date = mm.auto_field()
    is_active = mm.auto_field()


category_ordered_schema = CategorySchema(many=True)
category_ordered_single_schema = CategorySchema()
