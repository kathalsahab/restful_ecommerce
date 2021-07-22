"""Product Schema
"""
from ecom.extensions import mm
from ecom.design.models import Product


class ProductSchema(mm.SQLAlchemySchema):
    class Meta:
        model = Product

    product_id = mm.auto_field()
    product_name = mm.auto_field()
    product_desc = mm.auto_field()
    product_image_URI = mm.auto_field()
    created_date = mm.auto_field()
    updated_date = mm.auto_field()
    is_active = mm.auto_field()
    product_price = mm.auto_field()
    product_quantity = mm.auto_field()


product_schema_list = ProductSchema(many=True)
product_schema_single = ProductSchema()
