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
from ecom.utils import RecordNotFound
from sqlalchemy import and_
from sqlalchemy.types import String


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
    child_categories = relationship(
        "Category", remote_side=[category_parent_id], uselist=True, viewonly=True
    )

    @classmethod
    def lookup(cls, category_id):
        return cls.query.filter_by(category_id=category_id, is_active=True).first()

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
        return cls.query.filter_by(category_name=category_name, is_active=True,).first()

    @staticmethod
    def get_category_by_single_id(category_id: int):
        return (
            db.session.query(Category)
            .filter(Category.category_id == category_id, Category.is_active == True,)
            .first()
        )

    @staticmethod
    def create_category(
        category_name, category_desc=None, parent_id=None,
    ):
        # TODO: Need to check the duplicate record issue
        category = Category.query.filter_by(
            category_name=category_name, is_active=True, category_parent_id=parent_id,
        ).first()

        if category:
            return

        category = Category()

        category.category_name = category_name
        if parent_id is not None:
            category.category_parent_id = parent_id
        if category_desc is not None:
            category.category_desc = category_desc

        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def update_category(
        category_id, category_desc=None, category_name=None, category_parent_id=None,
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
    __tablename__ = "product"

    product_id = Column(INTEGER, primary_key=True)
    product_name = Column(String(100), nullable=False)
    product_desc = Column(String(1000))
    product_image_URI = Column(String(1000))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    product_price = Column(INTEGER, nullable=True)
    product_quantity = Column(INTEGER, nullable=True)

    @classmethod
    def lookup(cls, product_id):
        return Product.query.filter_by(product_id=product_id).first()

    @staticmethod
    def update_product(
        product_id,
        product_name=None,
        product_desc=None,
        product_image_URI=None,
        product_price=None,
        product_quantity=None,
    ):
        product = Product.query.filter_by(product_id=product_id).first()

        if not product:
            raise RecordNotFound

        if product_name is not None:
            product.product_name = product_name
        if product_desc is not None:
            product.product_desc = product_desc
        if product_image_URI is not None:
            product.product_image_URI = product_image_URI
        if product_price is not None:
            product.product_price = product_price
        if product_quantity is not None:
            product.product_quantity = product_quantity

        db.session.commit()
        return product

    @staticmethod
    def create_product(
        product_name,
        product_desc=None,
        product_image_URI=None,
        product_price=None,
        product_quantity=None,
    ):
        product = Product()

        product.product_name = product_name
        if product_desc is not None:
            product.product_desc = product_desc
        if product_image_URI is not None:
            product.product_image_URI = product_image_URI
        if product_price is not None:
            product.product_price = product_price
        if product_quantity is not None:
            product.product_quantity = product_quantity

        db.session.add(product)
        db.session.commit()

        return product


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
    product = relationship("Product", backref="category_map", lazy=True)

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
    def create_category_to_product_map(category_id, product_id, is_active=True):
        category = Category.query.filter_by(
            category_id=category_id, is_active=True
        ).first()
        if not category:
            return False
        if is_active:
            cat_product_map = CategoryToProductMap.query.filter_by(
                category_id=category_id, product_id=product_id, is_active=is_active
            ).first()

            if cat_product_map:
                return

        cat_product_map = CategoryToProductMap()
        cat_product_map.category_id = category_id
        cat_product_map.product_id = product_id
        cat_product_map.is_active = is_active

        db.session.add(cat_product_map)
        db.session.commit()

        return cat_product_map
