console.log("Advanced Print Engine JS Bundle Loaded");
$(document).on('form-refresh', function (e, frm) {
	console.log("Global form-refresh triggered for:", frm.doctype);
	if (frm.doc.__islocal) return;

	// Query if any enabled Advanced Print Format template exists for the current form's Doctype
	frappe.call({
		method: "advanced_print_engine.api.generate_pdf.get_available_templates",
		args: {
			reference_doctype: frm.doctype
		},
		callback: function (r) {
			console.log("Available templates for " + frm.doctype + ":", r);
			if (r.message && r.message.length > 0) {
				const templates = r.message;

				frm.add_custom_button(
					__("Generate Smart PDF"),
					function () {
						if (templates.length === 1) {
							render_smart_pdf(frm, templates[0]);
						} else {
							const options = templates.map(t => t.print_format_name);
							frappe.prompt([
								{
									label: __("Select Print Format"),
									fieldname: "print_format",
									fieldtype: "Select",
									options: options,
									reqd: 1
								}
							], (values) => {
								const selected = templates.find(t => t.print_format_name === values.print_format);
								if (selected) {
									render_smart_pdf(frm, selected);
								}
							}, __("Select Template"), __("Generate"));
						}
					},
					__("Print")
				);
			}
		}
	});
});

function render_smart_pdf(frm, template) {
	frappe.show_alert({
		message: __("Rendering high-fidelity multi-page PDF..."),
		indicator: "green"
	});

	const baseUrl = frappe.urllib.get_base_url();
	// Pass template.name (the ID) to the API
	const apiUrl = `${baseUrl}/api/method/advanced_print_engine.api.generate_pdf.generate_smart_pdf?doctype=${encodeURIComponent(frm.doctype)}&docname=${encodeURIComponent(frm.docname)}&print_format_name=${encodeURIComponent(template.name)}`;

	window.open(apiUrl, "_blank");
}

