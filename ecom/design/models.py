"""Centralised location for all the DB Models
"""
from datetime import datetime
from sqlalchemy.sql.schema import PrimaryKeyConstraint

# Third party imports
from sqlalchemy import (
    ForeignKey,
    INTEGER,
    Table,
    Column,
    DateTime,
    String,
    Boolean,
    Text,
    JSON,
    TEXT,
    MetaData,
)
from sqlalchemy.orm import relationship

# Application imports
from ecom.extensions import db
from ecom.utils import (
    RecordNotFound,
)
from sqlalchemy import and_
from sqlalchemy.types import String
from ecom.constants import (
    CATEGORY_FLAG_CATEGORY_TABLE,
)


def build_constraints(
    table1_name: str,
    column_name: str,
    table2_name: str = None,
    is_fk: bool = False,
    is_pk: bool = False,
):
    constraint_name = ""
    if is_fk is True:
        constraint_name += "FK__"
    if is_pk is True:
        constraint_name += "PK__"
    constraint_name += table1_name + "__"
    if is_fk is True:
        constraint_name += table2_name + "__"
    constraint_name += column_name

    return constraint_name


class Category(db.Model):
    __tablename__ = "category"

    category_id = Column(INTEGER, primary_key=True)
    category_name = Column(String(100), nullable=False)
    category_desc = Column(String(1000))
    created_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    category_parent_id = Column(
        INTEGER,
        ForeignKey(
            "category.category_id",
            name=build_constraints(
                is_fk=True,
                table1_name="category",
                table2_name="category",
                column_name="category_parent_id",
            ),
        ),
    )
    childs = relationship(
        "Category", remote_side=[category_parent_id], uselist=True, viewonly=True
    )

    @classmethod
    def lookup(cls, category_id):
        return (
            cls.query.filter_by(
                category_id=category_id, is_active=True
            )
            .first()
        )

    @property
    def category_parent_name(self):
        return self.parents.category_name

    @classmethod
    def get_childs(cls, category_id):
        cat_child = cls.query.filter_by(parent_id=category_id, is_active=True).all()

        if not cat_child:
            raise RecordNotFound

        return cat_child

    @classmethod
    def get_category_by_name(cls, category_name):
        return (
            cls.query.filter_by(
                category_name=category_name,
                is_active=True,
            )
            .first()
        )

    @staticmethod
    def get_category_by_single_id(category_id: int):
        return (
            db.session.query(Category)
            .filter(
                Category.category_id == category_id,
                Category.is_active == True,
            )
            .first()
        )

    @staticmethod
    def create_category(
        category_name,
        category_desc=None,
        parent_id=None,
        category_type_flag=None,
    ):
        # TODO: Need to check the duplicate record issue
        if parent_id is None:
            return
        category = Category.query.filter_by(
            category_name=category_name,
            is_active=True,
            parent_id=parent_id,
        ).first()

        if category:
            return

        category = Category()

        category.category_name = category_name
        if parent_id is not None:
            category.parent_id = parent_id
        if category_desc is not None:
            category.category_desc = category_desc
        if category_type_flag is not None:
            category.category_type_flag = category_type_flag

        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def update_category(
        category_id,
        category_desc=None,
        category_name=None,
        category_parent_id=None,
    ):
        category = Category.query.filter_by(category_id=category_id).first()

        if not category:
            raise RecordNotFound

        if category_desc is not None:
            category.category_desc = category_desc
        if category_name is not None:
            category.category_name = category_name
        if category_parent_id is not None:
            category.category_parent_id = category_parent_id

        # db.session.add(category)
        db.session.commit()
        return category


class Product(db.Model):
    __tablename__ = 'product'
    
    product_id = Column(INTEGER, primary_key=True)
    product_name = Column(String(100), nullable=False)
    product_desc = Column(String(1000))
    product_image_URI = Column(String(1000))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class CategoryToProductMap(db.Model):
    __tablename__ = "category_to_product_map"

    cat_to_product_map = Column(INTEGER, primary_key=True)
    is_active = Column(Boolean, default=True)
    category_id = Column(
        INTEGER,
        ForeignKey(
            Category.category_id,
            name=build_constraints(
                is_fk=True,
                table1_name="category_to_product_map",
                table2_name="category",
                column_name="category_id",
            ),
        ),
    )
    product_id = Column(
        INTEGER,
        ForeignKey(
            Product.product_id,
            name=build_constraints(
                is_fk=True,
                table1_name="category_to_product_map",
                table2_name="product",
                column_name="product_id",
            ),
        ),
        nullable=False,
    )

    category = relationship("Category", backref="category_map", lazy=True)
    module = relationship("Module", backref="category_map", lazy=True)
    sme_category_map = relationship(
        "SmeCategoryMap", backref="category_map", lazy=True, uselist=True, viewonly=True
    )

    @classmethod
    def lookup(cls, cat_mapping_id):
        return cls.query.filter_by(cat_mapping_id=cat_mapping_id).first()

    @property
    def module_name(self):
        return self.product.product_name

    @classmethod
    def get_products_by_category(cls, category_id):
        return cls.query.filter_by(category_id=category_id, is_active=True).all()

    @staticmethod
    def create_category_to_product_map(
        category_id, template_URI_path, product_id, is_active=True
    ):
        if is_active:
            cat_product_map = CategoryToProductMap.query.filter_by(
                category_id=category_id, product_id=product_id, is_active=is_active
            ).first()

            if cat_product_map:
                return

        cat_product_map = CategoryToProductMap()
        cat_product_map.category_id = category_id
        cat_product_map.module_id = product_id
        cat_product_map.is_active = is_active
        if template_URI_path is not None:
            cat_product_map.template_URI_path = template_URI_path

        db.session.add(cat_product_map)
        db.session.commit()

        return cat_product_map
