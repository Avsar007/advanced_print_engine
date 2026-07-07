import frappe
from advanced_print_engine.renderer.smart_renderer import SmartRenderer


@frappe.whitelist()
def generate_smart_pdf(doctype, docname, print_format_name):
	"""Generates advanced dynamic PDF via Playwright and streams it for browser preview."""
	# Pre-flight security/access validation
	if not frappe.has_permission(doctype, "read", docname):
		frappe.throw(f"Not permitted to view {doctype} {docname}", frappe.PermissionError)

	renderer = SmartRenderer(doctype, docname, print_format_name)
	pdf_bytes = renderer.render_and_generate_pdf()

	# Use the print format name as the download filename (naming series)
	frappe.local.response.filename = f"{print_format_name}.pdf"
	frappe.local.response.filecontent = pdf_bytes
	frappe.local.response.type = "pdf"

@frappe.whitelist()
def get_available_templates(reference_doctype):
	"""Returns Advanced Print Formats configured for the reference doctype."""
	return frappe.get_all(
		"Advanced Print Format",
		filters={"reference_doctype": reference_doctype},
		fields=["name", "print_format_name"]
	)


@frappe.whitelist()
def get_linked_advanced_format(print_format):
	"""Return the Advanced Print Format linked to a standard Print Format."""
	if not print_format or print_format == "Standard":
		return None
	return frappe.db.get_value("Print Format", print_format, "custom_advanced_print_format")


@frappe.whitelist()
def get_advanced_format_meta(advanced_format_name):
	"""Return page layout metadata for screen preview sizing."""
	if not advanced_format_name:
		return {}
	return frappe.db.get_value(
		"Advanced Print Format",
		advanced_format_name,
		["name", "page_size", "orientation", "print_format_name"],
		as_dict=True,
	) or {}


@frappe.whitelist()
def get_smart_preview_html(doctype, docname, print_format_name):
	"""Return paginated HTML for in-app print preview (Frappe-style iframe injection)."""
	if not frappe.has_permission(doctype, "read", docname):
		frappe.throw(f"Not permitted to view {doctype} {docname}", frappe.PermissionError)

	renderer = SmartRenderer(doctype, docname, print_format_name)
	return renderer.render_html()


@frappe.whitelist()
def generate_smart_html(doctype, docname, print_format_name):
	"""Generates advanced dynamic HTML via SmartRenderer and streams it for screen preview."""
	# Pre-flight security/access validation
	if not frappe.has_permission(doctype, "read", docname):
		frappe.throw(f"Not permitted to view {doctype} {docname}", frappe.PermissionError)

	renderer = SmartRenderer(doctype, docname, print_format_name)
	html_content = renderer.render_html()

	frappe.local.response.filename = "preview.html"
	frappe.local.response.filecontent = html_content
	frappe.local.response.type = "download"
	frappe.local.response.display_content_as = "inline"


