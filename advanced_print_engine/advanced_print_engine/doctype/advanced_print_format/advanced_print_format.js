// Copyright (c) 2026, Developer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Advanced Print Format", {
	refresh(frm) {
		if (frm.doc.__islocal) return;
		frm.add_custom_button(__("Compile Jinja HTML"), function () {
			frappe.call({
				method: "export_jinja_html",
				doc: frm.doc,
				callback: function (r) {
					if (r.message) {
						frappe.msgprint({
							title: __("Success"),
							indicator: "green",
							message: __("Jinja HTML compiled successfully to disk at:<br><code>{0}</code>", [r.message])
						});
					}
				}
			});
		});
	},
});

