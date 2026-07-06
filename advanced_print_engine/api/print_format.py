import frappe


def on_print_format_trash(doc, method=None):
	"""Uncheck print_format_created on the linked Advanced Print Format."""
	advanced_format = doc.get("custom_advanced_print_format")
	if not advanced_format:
		return

	if frappe.db.exists("Advanced Print Format", advanced_format):
		frappe.db.set_value(
			"Advanced Print Format",
			advanced_format,
			"print_format_created",
			0,
			update_modified=False,
		)
