(() => {
  // ../advanced_print_engine/advanced_print_engine/public/js/advanced_print_engine.bundle.js
  console.log("Advanced Print Engine JS Bundle Loaded");
  window.render_smart_pdf = function(frm, print_format_name) {
    frappe.show_alert({
      message: __("Preparing print preview..."),
      indicator: "green"
    });
    const baseUrl = frappe.urllib.get_base_url();
    const apiUrl = `${baseUrl}/api/method/advanced_print_engine.api.generate_pdf.generate_smart_pdf?doctype=${encodeURIComponent(frm.doctype)}&docname=${encodeURIComponent(frm.docname)}&print_format_name=${encodeURIComponent(print_format_name)}`;
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      frappe.msgprint(__("Please allow popups for this site to view the print preview."));
      return;
    }
    printWindow.document.write(`
		<!DOCTYPE html>
		<html>
		<head>
			<title>Print Preview - ${print_format_name}</title>
			<style>
				body, html {
					margin: 0;
					padding: 0;
					width: 100%;
					height: 100%;
					overflow: hidden;
					font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
					background-color: #f4f5f6;
				}
				#loader-container {
					position: absolute;
					top: 0;
					left: 0;
					width: 100%;
					height: 100%;
					display: flex;
					flex-direction: column;
					align-items: center;
					justify-content: center;
					background: rgba(255, 255, 255, 0.95);
					z-index: 10;
					transition: opacity 0.3s ease;
				}
				.spinner {
					border: 4px solid #f3f3f3;
					border-top: 4px solid #1a73e8;
					border-radius: 50%;
					width: 50px;
					height: 50px;
					animation: spin 1s linear infinite;
					margin-bottom: 20px;
				}
				@keyframes spin {
					0% { transform: rotate(0deg); }
					100% { transform: rotate(360deg); }
				}
				.text {
					font-size: 16px;
					color: #333;
					font-weight: 500;
				}
				iframe {
					border: none;
					width: 100%;
					height: 100%;
					position: absolute;
					top: 0;
					left: 0;
					z-index: 1;
				}
				#fallback-btn {
					margin-top: 15px;
					padding: 10px 20px;
					font-size: 14px;
					background-color: #1a73e8;
					color: white;
					border: none;
					border-radius: 4px;
					cursor: pointer;
					display: none;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					transition: background-color 0.2s;
				}
				#fallback-btn:hover {
					background-color: #1557b0;
				}
			</style>
		</head>
		<body>
			<div id="loader-container">
				<div class="spinner"></div>
				<div class="text">Generating and rendering PDF. Please wait...</div>
				<button id="fallback-btn" onclick="triggerPrint()">Print Manually</button>
			</div>
			
			<iframe id="pdf-frame" src="${apiUrl}"></iframe>

			<script>
				const iframe = document.getElementById('pdf-frame');
				const loader = document.getElementById('loader-container');
				const fallbackBtn = document.getElementById('fallback-btn');
				const text = loader.querySelector('.text');

				function triggerPrint() {
					try {
						iframe.contentWindow.focus();
						iframe.contentWindow.print();
					} catch (e) {
						console.error("Auto print failed: ", e);
						alert("Could not open print window automatically. Please use Ctrl + P inside the PDF view.");
					}
				}

				iframe.onload = function() {
					// Change loading message
					text.innerText = "Loading print preview...";
					
					// Show manual print button in case browser blocks auto-trigger
					fallbackBtn.style.display = "block";

					// Wait a bit to ensure PDF is loaded/rendered by browser plugin
					setTimeout(() => {
						// Hide the loader container
						loader.style.opacity = '0';
						setTimeout(() => {
							loader.style.zIndex = '-1';
						}, 300);

						// Trigger browser print dialog
						triggerPrint();
					}, 1200);
				};
			<\/script>
		</body>
		</html>
	`);
    printWindow.document.close();
  };
  $(document).on("form-refresh", function(e, frm) {
    console.log("Global form-refresh triggered for:", frm.doctype);
    if (frm.doc.__islocal)
      return;
    frappe.call({
      method: "advanced_print_engine.api.generate_pdf.get_available_templates",
      args: {
        reference_doctype: frm.doctype
      },
      callback: function(r) {
        console.log("Available templates for " + frm.doctype + ":", r);
        if (r.message && r.message.length > 0) {
          const templates = r.message;
          frm.add_custom_button(
            __("Generate Smart PDF"),
            function() {
              let d = new frappe.ui.Dialog({
                title: __("Generate Smart PDF"),
                fields: [
                  {
                    label: __("Select Advance Print Format"),
                    fieldname: "advance_print_format",
                    fieldtype: "Link",
                    options: "Advanced Print Format",
                    reqd: 1,
                    get_query: function() {
                      return {
                        filters: {
                          reference_doctype: frm.doctype,
                          enabled: 1
                        }
                      };
                    }
                  }
                ],
                primary_action_label: __("Print"),
                primary_action(values) {
                  d.hide();
                  window.render_smart_pdf(frm, values.advance_print_format);
                }
              });
              if (templates.length > 0) {
                d.set_value("advance_print_format", templates[0].name);
              }
              d.show();
            },
            __("Print")
          );
        }
      }
    });
  });
  function hook_print_view_class(PrintViewClass) {
    if (!PrintViewClass || !PrintViewClass.prototype)
      return;
    if (PrintViewClass.prototype._smart_print_hooked)
      return;
    PrintViewClass.prototype._smart_print_hooked = true;
    console.log("Hooking frappe.ui.form.PrintView class prototype for Advanced Print Engine");
    const original_setup_sidebar = PrintViewClass.prototype.setup_sidebar;
    PrintViewClass.prototype.setup_sidebar = function() {
      original_setup_sidebar.apply(this, arguments);
      this.advance_print_format_control = this.add_sidebar_item({
        fieldtype: "Link",
        fieldname: "advance_print_format",
        options: "Advanced Print Format",
        label: __("Select Advance Print Format"),
        get_query: () => {
          return {
            filters: {
              reference_doctype: this.frm.doctype,
              enabled: 1
            }
          };
        },
        change: () => {
          if (!this._is_clearing_fields) {
            this._is_clearing_fields = true;
            if (this.advance_print_format_control.get_value()) {
              if (this.print_format_selector) {
                this.print_format_selector.val("");
              }
            }
            this._is_clearing_fields = false;
          }
          this.preview();
        }
      });
      this.advance_print_format_selector = this.advance_print_format_control.$input;
      this.advance_print_format_control.toggle(false);
    };
    const original_refresh_print_format = PrintViewClass.prototype.refresh_print_format;
    PrintViewClass.prototype.refresh_print_format = function() {
      if (!this._is_clearing_fields) {
        this._is_clearing_fields = true;
        if (this.print_format_selector && this.print_format_selector.val()) {
          if (this.advance_print_format_control) {
            this.advance_print_format_control.set_value("");
          }
        }
        this._is_clearing_fields = false;
      }
      original_refresh_print_format.apply(this, arguments);
    };
    const original_show = PrintViewClass.prototype.show;
    PrintViewClass.prototype.show = function(frm) {
      const me = this;
      if (me.advance_print_format_control) {
        me.advance_print_format_control.toggle(false);
        me.advance_print_format_control.set_value("");
      }
      const promise = original_show.apply(this, arguments);
      frappe.call({
        method: "advanced_print_engine.api.generate_pdf.get_available_templates",
        args: {
          reference_doctype: frm.doctype
        },
        callback: function(r) {
          if (r.message && r.message.length > 0) {
            if (me.advance_print_format_control) {
              me.advance_print_format_control.toggle(true);
            }
          }
        }
      });
      return promise;
    };
    const original_preview = PrintViewClass.prototype.preview;
    PrintViewClass.prototype.preview = function() {
      const standard_selected = this.print_format_selector ? this.print_format_selector.val() : null;
      const advance_format = !standard_selected ? this.advance_print_format_control ? this.advance_print_format_control.get_value() : null : null;
      if (advance_format) {
        this.print_wrapper.find(".print-format-skeleton").remove();
        this.print_wrapper.find(".print-preview-wrapper .print-format-skeleton").remove();
        this.print_wrapper.find(".preview-beta-wrapper").hide();
        this.print_wrapper.find(".print-preview-wrapper").show();
        const $print_format = this.print_wrapper.find(".print-format-container");
        const baseUrl = frappe.urllib.get_base_url();
        const apiUrl = `${baseUrl}/api/method/advanced_print_engine.api.generate_pdf.generate_smart_html?doctype=${encodeURIComponent(this.frm.doctype)}&docname=${encodeURIComponent(this.frm.docname)}&print_format_name=${encodeURIComponent(advance_format)}`;
        $print_format.removeAttr("srcdoc");
        $print_format.attr("scrolling", "no");
        $print_format.css({
          "height": "800px",
          "border": "none",
          "border-radius": "0"
        });
        $print_format.attr("src", apiUrl);
        $print_format.off("load.smart_preview").on("load.smart_preview", function() {
          const checkPagination = setInterval(() => {
            try {
              const iframeDoc = $print_format.contents();
              const done = iframeDoc.find("#pagination-done").css("display") === "block";
              if (done) {
                clearInterval(checkPagination);
                const contentHeight = iframeDoc.find("body").outerHeight() || iframeDoc.find("#render-target").outerHeight();
                if (contentHeight) {
                  $print_format.css("height", contentHeight + 20 + "px");
                }
              }
            } catch (e) {
              clearInterval(checkPagination);
            }
          }, 100);
          setTimeout(() => clearInterval(checkPagination), 1e4);
        });
        this.wrapper.find(".page-break-message").text("");
        return;
      } else {
        const $print_format = this.print_wrapper.find(".print-format-container");
        $print_format.attr("scrolling", "no");
        $print_format.removeAttr("src");
        $print_format.css({
          "border": "none",
          "border-radius": "0"
        });
        original_preview.apply(this, arguments);
      }
    };
    const original_render_pdf = PrintViewClass.prototype.render_pdf;
    PrintViewClass.prototype.render_pdf = function() {
      const standard_selected = this.print_format_selector ? this.print_format_selector.val() : null;
      const advance_format = !standard_selected ? this.advance_print_format_control ? this.advance_print_format_control.get_value() : null : null;
      if (advance_format) {
        const baseUrl = frappe.urllib.get_base_url();
        const apiUrl = `${baseUrl}/api/method/advanced_print_engine.api.generate_pdf.generate_smart_pdf?doctype=${encodeURIComponent(this.frm.doctype)}&docname=${encodeURIComponent(this.frm.docname)}&print_format_name=${encodeURIComponent(advance_format)}`;
        window.open(apiUrl, "_blank");
        return;
      }
      original_render_pdf.apply(this, arguments);
    };
    const original_render_page = PrintViewClass.prototype.render_page;
    PrintViewClass.prototype.render_page = function(method, printit = false) {
      const standard_selected = this.print_format_selector ? this.print_format_selector.val() : null;
      const advance_format = !standard_selected ? this.advance_print_format_control ? this.advance_print_format_control.get_value() : null : null;
      if (advance_format) {
        const baseUrl = frappe.urllib.get_base_url();
        const apiUrl = `${baseUrl}/api/method/advanced_print_engine.api.generate_pdf.generate_smart_pdf?doctype=${encodeURIComponent(this.frm.doctype)}&docname=${encodeURIComponent(this.frm.docname)}&print_format_name=${encodeURIComponent(advance_format)}`;
        if (printit) {
          window.render_smart_pdf(this.frm, advance_format);
        } else {
          window.open(apiUrl, "_blank");
        }
        return;
      }
      original_render_page.apply(this, arguments);
    };
  }
  if (frappe.ui && frappe.ui.form) {
    let _PrintView = frappe.ui.form.PrintView;
    if (_PrintView) {
      hook_print_view_class(_PrintView);
    } else {
      Object.defineProperty(frappe.ui.form, "PrintView", {
        get() {
          return _PrintView;
        },
        set(val) {
          _PrintView = val;
          hook_print_view_class(val);
        },
        configurable: true
      });
    }
  }
  $(document).on("page-change", function() {
    if (frappe.ui && frappe.ui.form && frappe.ui.form.PrintView) {
      hook_print_view_class(frappe.ui.form.PrintView);
    }
  });
})();
//# sourceMappingURL=advanced_print_engine.bundle.CXDS7Y25.js.map
