// Copyright (c) 2026, Developer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Advanced Print Format", {
	refresh(frm) {
		if (frm.doc.__islocal) return;

		if (!frm.doc.print_format_created) {
			frm.add_custom_button(__("Create Print Format"), function () {
				frappe.call({
					method: "create_linked_print_format",
					doc: frm.doc,
					freeze: true,
					freeze_message: __("Creating Print Format..."),
					callback(r) {
						if (!r.message) return;
						const { print_format, created } = r.message;
						frm.reload_doc();
						frappe.show_alert({
							message: created
								? __("Print Format {0} created.", [print_format])
								: __("Print Format {0} already exists.", [print_format]),
							indicator: "green",
						});
					},
				});
			});
		}

		if (frm.doc.print_format_created) {
			frm.add_custom_button(__("Open Print Format"), function () {
				frappe.call({
					method: "get_linked_print_format_name",
					doc: frm.doc,
					callback(r) {
						if (r.message) {
							frappe.set_route("Form", "Print Format", r.message);
						}
					},
				});
			}, __("View"));
		}
	},
});
