# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AdvancedPrintFormat(Document):
	def validate(self):
		self.validate_rules("header_rules", "Header Rules")
		self.validate_rules("footer_rules", "Footer Rules")

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
				# clear page number if accidentally set
				row.page_number = 0
			elif row.rule_type == "Last Page":
				last_page_count += 1
				row.page_number = 0
			elif row.rule_type == "Specific Page":
				if not row.page_number or row.page_number <= 0:
                    # Let's use standard frappe.throw for mandatory check
					frappe.throw(f"Row #{row.idx} in {label}: Page Number is mandatory and must be > 0 for 'Specific Page' rules.")
				
				if row.page_number in specific_pages:
					frappe.throw(f"Duplicate entry for Page #{row.page_number} in {label} table.")
				specific_pages.add(row.page_number)

		if first_page_count > 1:
			frappe.throw(f"Only one 'First Page' entry is allowed in {label}.")
		if last_page_count > 1:
			frappe.throw(f"Only one 'Last Page' entry is allowed in {label}.")
