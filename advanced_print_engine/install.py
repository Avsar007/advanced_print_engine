import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from advanced_print_engine.custom_field import CUSTOM_FIELDS


def after_migrate():
	from advanced_print_engine.advanced_print_format_utils import sync_standard_advanced_print_formats
	sync_standard_advanced_print_formats()

def after_install():
	sync_custom_fields()

def sync_custom_fields():
	create_custom_fields(CUSTOM_FIELDS)
