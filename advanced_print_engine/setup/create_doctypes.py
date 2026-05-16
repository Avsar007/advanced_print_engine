import frappe

def create_all_doctypes():
	create_module_def()
	create_header_rule_doctype()
	create_footer_rule_doctype()
	create_main_print_format_doctype()

def create_module_def():
	if not frappe.db.exists("Module Def", "Advanced Print Engine"):
		frappe.get_doc({
			"doctype": "Module Def",
			"module_name": "Advanced Print Engine",
			"custom": 0,
			"app_name": "advanced_print_engine"
		}).insert(ignore_permissions=True)
		print("Created Module Def: Advanced Print Engine")

def create_header_rule_doctype():
	if not frappe.db.exists("DocType", "Advanced Print Header Rule"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Advanced Print Header Rule",
			"module": "Advanced Print Engine",
			"istable": 1,
			"custom": 0,
			"editable_grid": 1,
			"fields": [
				{"fieldname": "enabled", "label": "Enabled", "fieldtype": "Check", "default": "1", "in_list_view": 1},
				{"fieldname": "rule_type", "label": "Rule Type", "fieldtype": "Select", "options": "First Page\nLast Page\nSpecific Page", "in_list_view": 1, "reqd": 1},
				{"fieldname": "page_number", "label": "Page Number", "fieldtype": "Int", "depends_on": "eval:doc.rule_type=='Specific Page'", "in_list_view": 1},
				{"fieldname": "html_content", "label": "HTML Content", "fieldtype": "Code", "options": "HTML"},
				{"fieldname": "description", "label": "Description", "fieldtype": "Small Text"}
			]
		})
		doc.insert(ignore_permissions=True)
		print("Created Advanced Print Header Rule DocType")

def create_footer_rule_doctype():
	if not frappe.db.exists("DocType", "Advanced Print Footer Rule"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Advanced Print Footer Rule",
			"module": "Advanced Print Engine",
			"istable": 1,
			"custom": 0,
			"editable_grid": 1,
			"fields": [
				{"fieldname": "enabled", "label": "Enabled", "fieldtype": "Check", "default": "1", "in_list_view": 1},
				{"fieldname": "rule_type", "label": "Rule Type", "fieldtype": "Select", "options": "First Page\nLast Page\nSpecific Page", "in_list_view": 1, "reqd": 1},
				{"fieldname": "page_number", "label": "Page Number", "fieldtype": "Int", "depends_on": "eval:doc.rule_type=='Specific Page'", "in_list_view": 1},
				{"fieldname": "html_content", "label": "HTML Content", "fieldtype": "Code", "options": "HTML"},
				{"fieldname": "description", "label": "Description", "fieldtype": "Small Text"}
			]
		})
		doc.insert(ignore_permissions=True)
		print("Created Advanced Print Footer Rule DocType")

def create_main_print_format_doctype():
	doc_data = {
		"doctype": "DocType",
		"name": "Advanced Print Format",
		"module": "Advanced Print Engine",
		"custom": 0,
		"issingle": 0,
		"track_changes": 1,
		"autoname": "field:print_format_name",
		"fields": [
			{"fieldname": "print_format_name", "label": "Print Format Name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
			{"fieldname": "enabled", "label": "Enabled", "fieldtype": "Check", "default": "1", "in_list_view": 1},
			{"fieldname": "reference_doctype", "label": "Reference Doctype", "fieldtype": "Link", "options": "DocType", "reqd": 1, "in_list_view": 1},
			{"fieldname": "page_size", "label": "Page Size", "fieldtype": "Select", "options": "A4\nLetter\nLegal", "default": "A4"},
			{"fieldname": "orientation", "label": "Orientation", "fieldtype": "Select", "options": "Portrait\nLandscape", "default": "Portrait"},
			{"fieldname": "column_break_1", "fieldtype": "Column Break"},
			{"fieldname": "repeat_header", "label": "Repeat Header", "fieldtype": "Check", "default": "0"},
			{"fieldname": "repeat_footer", "label": "Repeat Footer", "fieldtype": "Check", "default": "0"},
			
			{"fieldname": "section_default_html", "label": "Default HTML Templates", "fieldtype": "Section Break"},
			{"fieldname": "default_header_html", "label": "Default Header HTML", "fieldtype": "Code", "options": "HTML"},
			{"fieldname": "default_footer_html", "label": "Default Footer HTML", "fieldtype": "Code", "options": "HTML"},
			
			{"fieldname": "section_body_html", "label": "Body HTML & Styling", "fieldtype": "Section Break"},
			{"fieldname": "body_html", "label": "Body HTML", "fieldtype": "Code", "options": "HTML"},
			{"fieldname": "custom_css", "label": "Custom CSS", "fieldtype": "Code", "options": "CSS"},
			
			{"fieldname": "section_rules", "label": "Header & Footer Overrides", "fieldtype": "Section Break"},
			{"fieldname": "header_rules", "label": "Header Rules", "fieldtype": "Table", "options": "Advanced Print Header Rule"},
			{"fieldname": "footer_rules", "label": "Footer Rules", "fieldtype": "Table", "options": "Advanced Print Footer Rule"}
		],
		"permissions": [
			{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
		]
	}

	if frappe.db.exists("DocType", "Advanced Print Format"):
		doc = frappe.get_doc("DocType", "Advanced Print Format")
		doc.update(doc_data)
		doc.save(ignore_permissions=True)
		print("Updated Advanced Print Format DocType")
	else:
		doc = frappe.get_doc(doc_data)
		doc.insert(ignore_permissions=True)
		print("Created Advanced Print Format DocType")
