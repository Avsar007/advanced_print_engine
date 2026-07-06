# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AdvancedPrintFormat(Document):
	def validate(self):
		self.validate_rules("header_rules", "Header Rules")
		self.validate_rules("footer_rules", "Footer Rules")
		self.sync_print_format_created_flag()

	def after_insert(self):
		if not self.print_format_created:
			self.create_linked_print_format()

	def sync_print_format_created_flag(self):
		linked = frappe.db.exists(
			"Print Format", {"custom_advanced_print_format": self.name}
		)
		self.print_format_created = 1 if linked else 0

	def validate_rules(self, table_fieldname, label):
		rules = self.get(table_fieldname) or []
		first_page_count = 0
		last_page_count = 0
		specific_pages = set()

		for row in rules:
			if not row.enabled:
				continue

			if row.rule_type == "First Page":
				first_page_count += 1
				row.page_number = 0
			elif row.rule_type == "Last Page":
				last_page_count += 1
				row.page_number = 0
			elif row.rule_type == "Specific Page":
				if not row.page_number or row.page_number <= 0:
					frappe.throw(
						f"Row #{row.idx} in {label}: Page Number is mandatory and must be > 0 "
						"for 'Specific Page' rules."
					)

				if row.page_number in specific_pages:
					frappe.throw(f"Duplicate entry for Page #{row.page_number} in {label} table.")
				specific_pages.add(row.page_number)

		if first_page_count > 1:
			frappe.throw(f"Only one 'First Page' entry is allowed in {label}.")
		if last_page_count > 1:
			frappe.throw(f"Only one 'Last Page' entry is allowed in {label}.")

	@frappe.whitelist()
	def get_linked_print_format_name(self):
		return frappe.db.get_value(
			"Print Format", {"custom_advanced_print_format": self.name}, "name"
		)

	@frappe.whitelist()
	def create_linked_print_format(self):
		"""Create a Print Format linked one-way to this Advanced Print Format."""
		pf_name = (self.print_format_name or self.name).strip()
		if not pf_name:
			frappe.throw("Print Format Name is required.")

		existing_by_link = frappe.db.get_value(
			"Print Format", {"custom_advanced_print_format": self.name}, "name"
		)
		if existing_by_link:
			self.db_set("print_format_created", 1, update_modified=False)
			return {"print_format": existing_by_link, "created": False}

		if frappe.db.exists("Print Format", pf_name):
			existing_linked = frappe.db.get_value(
				"Print Format", pf_name, "custom_advanced_print_format"
			)
			if existing_linked and existing_linked != self.name:
				frappe.throw(
					f"Print Format '{pf_name}' is already linked to Advanced Print Format "
					f"'{existing_linked}'. Please use a different Print Format Name."
				)
			pf_doc = frappe.get_doc("Print Format", pf_name)
		else:
			pf_doc = frappe.new_doc("Print Format")
			pf_doc.name = pf_name
			pf_doc.print_format_name = pf_name

		pf_doc.custom_advanced_print_format = self.name
		pf_doc.doc_type = self.reference_doctype
		pf_doc.custom_format = 1
		pf_doc.print_format_type = "Jinja"
		pf_doc.standard = "No"
		pf_doc.html = "<!-- Rendered by Advanced Print Engine -->"
		pf_doc.css = ""
		pf_doc.disabled = 0
		pf_doc.save(ignore_permissions=True)

		self.db_set("print_format_created", 1, update_modified=False)
		return {"print_format": pf_doc.name, "created": True}
