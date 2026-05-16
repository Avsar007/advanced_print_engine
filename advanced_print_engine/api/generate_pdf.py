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
	"""Returns enabled Advanced Print Formats configured for the reference doctype."""
	return frappe.get_all(
		"Advanced Print Format",
		filters={"reference_doctype": reference_doctype, "enabled": 1},
		fields=["name", "print_format_name"]
	)

