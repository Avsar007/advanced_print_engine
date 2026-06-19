import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from advanced_print_engine.custom_field import CUSTOM_FIELDS

def after_migrate():
	sync_custom_fields()

def sync_custom_fields():
	create_custom_fields(CUSTOM_FIELDS)
