import os
import shutil
import frappe
from frappe.modules.export_file import strip_default_fields

def export_advanced_print_format_json(doc):
	"""Export the Advanced Print Format doc to its app module folder as JSON."""
	if not doc.is_standard == "Yes":
		return

	if not doc.custom_app or not doc.custom_module:
		frappe.throw("App and Module must be set to save standard print format")

	# Check developer mode
	if not frappe.conf.developer_mode and not frappe.flags.in_migrate and not frappe.flags.in_install and not frappe.flags.in_test:
		frappe.throw("Developer Mode must be enabled to save Standard Advanced Print Format")

	app_path = frappe.get_app_path(doc.custom_app)
	module_path = os.path.join(app_path, frappe.scrub(doc.custom_module))
	folder = os.path.join(module_path, "advance_print_formats", frappe.scrub(doc.name))
	
	os.makedirs(folder, exist_ok=True)
	
	# Convert doc to dict (without nulls)
	doc_dict = doc.as_dict(no_nulls=True)
	
	# Clean up children fields using standard Frappe method
	doc_dict = strip_default_fields(doc, doc_dict)
	
	# Remove runtime tracking fields to keep git diffs clean
	for key in ["modified", "modified_by", "creation", "owner"]:
		if key in doc_dict:
			del doc_dict[key]
			
	# Save the file
	file_path = os.path.join(folder, f"{frappe.scrub(doc.name)}.json")
	with open(file_path, "w") as f:
		f.write(frappe.as_json(doc_dict))

def delete_advanced_print_format_json(doc):
	"""Delete the standard JSON directory for the Advanced Print Format if it exists."""
	if doc.custom_app and doc.custom_module:
		app_path = frappe.get_app_path(doc.custom_app)
		module_path = os.path.join(app_path, frappe.scrub(doc.custom_module))
		folder = os.path.join(module_path, "advance_print_formats", frappe.scrub(doc.name))
		if os.path.exists(folder):
			shutil.rmtree(folder)

def sync_standard_advanced_print_formats():
	"""Sync all standard Advanced Print Formats from apps to the database on migration."""
	from frappe.modules.import_file import import_file_by_path
	
	files_to_sync = []
	
	for app_name in frappe.get_installed_apps():
		try:
			modules = frappe.get_module_list(app_name)
		except Exception:
			continue
			
		for module in modules:
			try:
				module_path = frappe.get_module_path(module)
			except Exception:
				continue
				
			folder = os.path.join(module_path, "advance_print_formats")
			if not os.path.exists(folder):
				continue
				
			for docname in os.listdir(folder):
				subdir = os.path.join(folder, docname)
				if os.path.isdir(subdir):
					json_file = os.path.join(subdir, f"{docname}.json")
					if os.path.exists(json_file):
						files_to_sync.append(json_file)
						
	if files_to_sync:
		print(f"Syncing {len(files_to_sync)} standard Advanced Print Formats...")
		for json_file in files_to_sync:
			try:
				import_file_by_path(json_file, force=True)
				frappe.db.commit()
			except Exception as e:
				print(f"Error syncing {json_file}: {e}")

	# Ensure module alignment between Advanced Print Format and linked standard Print Formats
	print("Ensuring module synchronization between Advanced Print Format and linked standard Print Formats...")
	standard_apfs = frappe.get_all(
		"Advanced Print Format",
		filters={"is_standard": "Yes"},
		fields=["name", "custom_module"]
	)
	for apf in standard_apfs:
		if apf.custom_module:
			pf_name = apf.name
			if frappe.db.exists("Print Format", pf_name):
				current_module = frappe.db.get_value("Print Format", pf_name, "module")
				if current_module != apf.custom_module:
					print(f"Aligning module for Print Format '{pf_name}': '{current_module}' -> '{apf.custom_module}'")
					frappe.db.set_value("Print Format", pf_name, "module", apf.custom_module, update_modified=False)
					frappe.db.commit()
