from marshmallow import fields
import json
from ecom.extensions import mm

from ecom.design.models import (
    Category,
    DataDistinctFileMap,
    Module,
    MetaColumn,
    FileTable,
    DataDistinct,
    MetaTable,
    Notification,
    SmeCategoryMap,
    InputControl,
    UsageTracking,
    User,
)


class ModuleSchema(mm.SQLAlchemySchema):
    class Meta:
        model = Module

    module_name = mm.auto_field()


module_schema = ModuleSchema()


class DataDistinctSchema(mm.SQLAlchemySchema):
    class Meta:
        model = DataDistinct
        ordered = True

    data_table_id = mm.auto_field()
    meta_table_id = mm.auto_field()
    meta_column_id = mm.auto_field()
    value = mm.auto_field()
    created_date = mm.auto_field()
    is_active = mm.auto_field()
    cat_mapping_id = mm.auto_field()
    parent_id = mm.auto_field()


data_distinct_all_schema = DataDistinctSchema(many=True)


class FileTableSchema(mm.SQLAlchemySchema):
    class Meta:
        model = FileTable
        ordered = True

    file_id = mm.auto_field()
    user_id = mm.auto_field()
    user_full_name = fields.String()
    meta_table_id = mm.auto_field()
    file_name = mm.auto_field()
    URI_path = mm.auto_field()
    created_date = mm.auto_field()
    modified_date = mm.auto_field()
    approval_date = mm.auto_field()
    approved_flag = mm.auto_field()
    comments = mm.auto_field()
    approved_by = mm.auto_field()
    is_active = mm.auto_field()
    sme_full_name = fields.Field()
    leaf_level = fields.Method("leaf_node")
    template_group = fields.String(attribute="meta_table_name")

    def leaf_node(self, obj):
        if obj.URI_path:
            return " > ".join(obj.URI_path.split("/")[-1].split("_")[3:-2])


file_table_schema = FileTableSchema(
    exclude=("user_full_name", "sme_full_name", "leaf_level", "template_group")
)
file_table_schema_many = FileTableSchema(
    many=True,
    exclude=("user_full_name", "sme_full_name", "leaf_level", "template_group"),
)
file_table_schema_extra = FileTableSchema(many=True)


class MetaColumnSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = MetaColumn
        ordered = True

    meta_column_id = mm.auto_field()
    meta_table_id = mm.auto_field()
    meta_column_name = mm.auto_field()
    meta_column_desc = fields.String(
        attribute="meta_column_description", dump_only=True
    )
    meta_column_ordinal = mm.auto_field()
    created_date = mm.auto_field()
    meta_column_input = mm.auto_field()
    input_control_id = mm.auto_field()
    control_ranges = mm.auto_field()
    is_mandatory = mm.auto_field()
    meta_column_output = mm.auto_field()
    is_active = mm.auto_field()
    is_level = fields.Boolean()


meta_column_schema = MetaColumnSchema(
    many=True,
    only=(
        "meta_column_id",
        "meta_column_name",
        "meta_column_desc",
        "meta_column_ordinal",
        "is_mandatory",
        "control_ranges",
        "is_level",
    ),
)

meta_column_schema_file = MetaColumnSchema(exclude=("is_level",), many=True)


class MetaTableSchema(mm.SQLAlchemySchema):
    class Meta:
        model = MetaTable
        ordered = True

    meta_table_id = mm.auto_field()
    cat_mapping_id = mm.auto_field()
    meta_table_name = mm.auto_field()
    meta_table_desc = mm.auto_field()
    meta_type_flag = mm.auto_field()
    created_date = mm.auto_field()
    is_active = mm.auto_field()


meta_table_sme_schema = MetaTableSchema(many=True)


class SmeCategoryMapSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = SmeCategoryMap
        ordered = True

    sme_user_name = fields.String()
    sme_category_map_id = mm.auto_field()
    cat_mapping_id = mm.auto_field()
    user_id = mm.auto_field()


sme_category_map_schema = SmeCategoryMapSchema(many=True)
sme_category_map_schema_file = SmeCategoryMapSchema(
    many=True, exclude=("sme_user_name",)
)


class InputControlSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = InputControl
        ordered = True

    input_control_id = mm.auto_field()
    input_control_name = mm.auto_field()


input_control_schema = InputControlSchema(many=True)


class CategorySchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        ordered = True

    category_id = mm.auto_field()
    category_level_id = mm.auto_field()
    category_name = mm.auto_field()
    category_desc = mm.auto_field()
    parent_id = mm.auto_field()
    created_date = mm.auto_field()
    is_active = mm.auto_field()
    is_enabled = mm.auto_field()
    category_type_flag = mm.auto_field()


category_ordered_schema = CategorySchema(many=True)
category_ordered_single_schema = CategorySchema()


class UsageTrackingSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = UsageTracking
        ordered = True

    usage_tracking_id = mm.auto_field()
    user_id = mm.auto_field()
    action_id = mm.auto_field()
    module_id = mm.auto_field()
    project_code = mm.auto_field()
    project_name = mm.auto_field()
    project_client = mm.auto_field()
    query_inputs = fields.Method("process_query_inputs")
    created_date = mm.auto_field()
    file_id = mm.auto_field()
    file_table = fields.Nested(file_table_schema, only=("approved_flag",))
    username = fields.String(attribute="full_username")

    def process_query_inputs(self, obj, **kwargs):
        if obj.query_inputs is not None:
            query_input = json.dumps(obj.query_inputs)
            return query_input
        return obj.query_inputs


usage_tracking_schema_file = UsageTrackingSchema(
    many=True, exclude=("file_table", "username")
)
usage_tracking_nested_schema = UsageTrackingSchema(
    exclude=(
        "project_code",
        "project_name",
        "project_client",
        "action_id",
        "created_date",
    ),
)


class DataDistinctFileMapSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = DataDistinctFileMap
        ordered = True

    data_distinct_file_map_id = mm.auto_field()
    data_table_id = mm.auto_field()
    file_id = mm.auto_field()


data_distinct_file_map_schema = DataDistinctFileMapSchema(many=True)


class UserSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class ModuleMailSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Module


class UsageTrackingMailSchema(mm.SQLAlchemyAutoSchema):
    user = mm.Nested(UserSchema, only=("first_name", "last_name", "email"))
    module = mm.Pluck(ModuleMailSchema, "module_name")

    class Meta:
        model = UsageTracking


usage_tracking_mail_schema = UsageTrackingMailSchema()
usage_tracking_mail_list_schema = UsageTrackingMailSchema(many=True)


class NotificationSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        ordered = True

    notification_id = mm.auto_field()
    user_id = mm.auto_field()
    usage_tracking_id = mm.auto_field()
    notification_message = mm.auto_field()
    scheduled_notification_date = mm.auto_field()
    scheduled_notification_status = mm.auto_field()
    is_read = mm.auto_field()
    created_date = mm.auto_field()
    modified_date = mm.auto_field()


notification_file_schema = NotificationSchema(many=True)
