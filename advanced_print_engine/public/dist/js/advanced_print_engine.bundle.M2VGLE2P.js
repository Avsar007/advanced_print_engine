(() => {
  // ../advanced_print_engine/advanced_print_engine/public/js/advanced_print_engine.bundle.js
  console.log("Advanced Print Engine JS Bundle Loaded");
  var APE_PAGE_DIMENSIONS = {
    A4: {
      Portrait: { width: 794, height: 1123 },
      Landscape: { width: 1123, height: 794 }
    },
    Letter: {
      Portrait: { width: 816, height: 1056 },
      Landscape: { width: 1056, height: 816 }
    },
    Legal: {
      Portrait: { width: 816, height: 1344 },
      Landscape: { width: 1344, height: 816 }
    }
  };
  function ape_get_page_dimensions(meta) {
    const size = meta && meta.page_size || "A4";
    const orientation = meta && meta.orientation || "Portrait";
    const size_map = APE_PAGE_DIMENSIONS[size] || APE_PAGE_DIMENSIONS.A4;
    return size_map[orientation] || APE_PAGE_DIMENSIONS.A4.Portrait;
  }
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
					text.innerText = "Loading print preview...";
					fallbackBtn.style.display = "block";
					setTimeout(() => {
						loader.style.opacity = '0';
						setTimeout(() => { loader.style.zIndex = '-1'; }, 300);
						triggerPrint();
					}, 1200);
				};
			<\/script>
		</body>
		</html>
	`);
    printWindow.document.close();
  };
  function ape_fetch_linked_advanced_format(print_format) {
    if (!print_format || print_format === "Standard") {
      return Promise.resolve(null);
    }
    return frappe.xcall("advanced_print_engine.api.generate_pdf.get_linked_advanced_format", {
      print_format
    }).then((linked) => linked || null);
  }
  function ape_fetch_advanced_format_meta(advanced_format_name) {
    if (!advanced_format_name) {
      return Promise.resolve({});
    }
    return frappe.xcall("advanced_print_engine.api.generate_pdf.get_advanced_format_meta", {
      advanced_format_name
    });
  }
  function ape_setup_smart_preview_iframe($print_format, dims) {
    $print_format.removeAttr("src");
    $print_format.attr("scrolling", "no");
    $print_format.css({
      width: dims.width + "px",
      maxWidth: "100%",
      height: dims.height + "px",
      margin: "0 auto",
      display: "block",
      border: "none",
      borderRadius: "0"
    });
  }
  function ape_finalize_smart_preview($print_format, dims, print_view, preview_id) {
    const maxWait = 12e4;
    const start = Date.now();
    const interval = setInterval(() => {
      if (preview_id && preview_id !== print_view._ape_preview_id) {
        clearInterval(interval);
        return;
      }
      try {
        const $contents = $print_format.contents();
        if ($contents.find("#pagination-done").css("display") !== "block") {
          if (Date.now() - start > maxWait) {
            clearInterval(interval);
          }
          return;
        }
        clearInterval(interval);
        const $pages = $contents.find("#render-target .page");
        const pageHeight = dims.height;
        $pages.each(function() {
          $(this).css({
            height: pageHeight + "px",
            minHeight: pageHeight + "px",
            maxHeight: pageHeight + "px"
          });
        });
        $contents.find("body").css({
          overflow: "visible",
          margin: "0",
          padding: "0",
          background: "#fff"
        });
        const totalHeight = ($pages.length || 1) * pageHeight + 20;
        $print_format.height(totalHeight);
        const $message = print_view.wrapper.find(".page-break-message");
        if ($pages.length > 1) {
          $message.text(__("{0} pages", [$pages.length]));
        } else {
          $message.text("");
        }
      } catch (e) {
        if (Date.now() - start > maxWait) {
          clearInterval(interval);
        }
      }
    }, 150);
  }
  function ape_inject_smart_preview_html($print_format, html, dims, print_view, preview_id) {
    const iframe = $print_format[0];
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write(html);
    doc.close();
    ape_finalize_smart_preview($print_format, dims, print_view, preview_id);
  }
  function ape_load_smart_preview(print_view, advance_format, preview_id) {
    print_view.print_wrapper.find(".print-format-skeleton").remove();
    print_view.print_wrapper.find(".print-preview-wrapper .print-format-skeleton").remove();
    print_view.print_wrapper.find(".preview-beta-wrapper").hide();
    print_view.print_wrapper.find(".print-preview-wrapper").show();
    const $print_format = print_view.print_wrapper.find(".print-format-container");
    ape_fetch_advanced_format_meta(advance_format).then((meta) => {
      if (preview_id && preview_id !== print_view._ape_preview_id) {
        return;
      }
      const dims = ape_get_page_dimensions(meta);
      ape_setup_smart_preview_iframe($print_format, dims);
      frappe.xcall("advanced_print_engine.api.generate_pdf.get_smart_preview_html", {
        doctype: print_view.frm.doctype,
        docname: print_view.frm.docname,
        print_format_name: advance_format
      }).then((html) => {
        if (preview_id && preview_id !== print_view._ape_preview_id) {
          return;
        }
        ape_inject_smart_preview_html($print_format, html, dims, print_view, preview_id);
      });
    });
  }
  function ape_reset_standard_preview_container(print_view) {
    const $print_format = print_view.print_wrapper.find(".print-format-container");
    $print_format.attr("scrolling", "no");
    $print_format.removeAttr("src");
    $print_format.removeAttr("srcdoc");
    try {
      const iframe = $print_format[0];
      if (iframe && iframe.contentDocument) {
        const doc = iframe.contentDocument;
        doc.open();
        doc.write("<!DOCTYPE html><html><head></head><body></body></html>");
        doc.close();
      }
    } catch (e) {
    }
    $print_format.css({
      width: "100%",
      height: "0",
      maxWidth: "",
      margin: "",
      display: "",
      border: "none",
      borderRadius: "0"
    });
  }
  $(document).on("form-refresh", function(e, frm) {
    if (frm.doc.__islocal)
      return;
    frappe.call({
      method: "advanced_print_engine.api.generate_pdf.get_available_templates",
      args: { reference_doctype: frm.doctype },
      callback(r) {
        if (r.message && r.message.length > 0) {
          frm.add_custom_button(
            __("Generate Smart PDF"),
            function() {
              const d = new frappe.ui.Dialog({
                title: __("Generate Smart PDF"),
                fields: [
                  {
                    label: __("Select Advance Print Format"),
                    fieldname: "advance_print_format",
                    fieldtype: "Link",
                    options: "Advanced Print Format",
                    reqd: 1,
                    get_query() {
                      return {
                        filters: {
                          reference_doctype: frm.doctype
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
              d.set_value("advance_print_format", r.message[0].name);
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
      const pf_wrapper = this.sidebar.find('.frappe-control[data-fieldname="print_format"]');
      if (pf_wrapper.length && pf_wrapper[0].fieldobj) {
        this.print_format_field = pf_wrapper[0].fieldobj;
      }
      this.advance_print_format_control = this.add_sidebar_item({
        fieldtype: "Link",
        fieldname: "advance_print_format",
        options: "Advanced Print Format",
        label: __("Advanced Print Format"),
        get_query: () => ({
          filters: {
            reference_doctype: this.frm.doctype
          }
        }),
        change: () => {
          if (this._is_clearing_fields || this._ape_linked_from_print_format)
            return;
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
      this._ape_linked_from_print_format = false;
    };
    PrintViewClass.prototype._ape_unlock_advance_print_format = function() {
      if (!this.advance_print_format_control)
        return;
      this._ape_linked_from_print_format = false;
      this.advance_print_format_control.df.read_only = 0;
      this.advance_print_format_control.refresh();
    };
    PrintViewClass.prototype._ape_get_print_format_value = function() {
      if (this.print_format_field && this.print_format_field.get_value) {
        return this.print_format_field.get_value() || "";
      }
      if (this.print_format_selector) {
        return this.print_format_selector.val() || "";
      }
      return "";
    };
    PrintViewClass.prototype._ape_clear_advanced_format = function() {
      if (!this.advance_print_format_control)
        return;
      this._is_clearing_fields = true;
      this._ape_linked_from_print_format = false;
      this.advance_print_format_control.df.read_only = 0;
      this.advance_print_format_control.set_value("");
      this.advance_print_format_control.refresh();
      this._is_clearing_fields = false;
    };
    PrintViewClass.prototype._ape_sync_linked_advanced_format = function() {
      const me = this;
      const sync_id = me._ape_sync_id = (me._ape_sync_id || 0) + 1;
      const print_format = me._ape_get_print_format_value();
      if (!print_format) {
        me._ape_clear_advanced_format();
        return Promise.resolve(null);
      }
      return ape_fetch_linked_advanced_format(print_format).then((linked) => {
        if (sync_id !== me._ape_sync_id) {
          return linked;
        }
        if (!me.advance_print_format_control) {
          return linked;
        }
        me._is_clearing_fields = true;
        if (linked) {
          me._ape_linked_from_print_format = true;
          me.advance_print_format_control.df.read_only = 1;
          me.advance_print_format_control.set_value(linked);
          me.advance_print_format_control.toggle(true);
        } else {
          me._ape_clear_advanced_format();
        }
        me.advance_print_format_control.refresh();
        me._is_clearing_fields = false;
        return linked;
      });
    };
    PrintViewClass.prototype._ape_resolve_advance_format = function() {
      const print_format = this._ape_get_print_format_value();
      if (print_format) {
        if (print_format === "Standard") {
          return Promise.resolve(null);
        }
        return ape_fetch_linked_advanced_format(print_format).then((linked) => linked || null);
      }
      if (this.advance_print_format_control) {
        return Promise.resolve(this.advance_print_format_control.get_value() || null);
      }
      return Promise.resolve(null);
    };
    PrintViewClass.prototype._ape_is_advanced_mode = function() {
      return this._ape_resolve_advance_format().then((name) => Boolean(name));
    };
    PrintViewClass.prototype.refresh_print_format = function() {
      const me = this;
      const sync = this._ape_sync_linked_advanced_format();
      const run_preview = () => {
        me.set_default_print_language();
        me.toggle_raw_printing();
        me.preview();
      };
      if (sync && typeof sync.finally === "function") {
        sync.finally(run_preview);
      } else {
        run_preview();
      }
    };
    const original_show = PrintViewClass.prototype.show;
    PrintViewClass.prototype.show = function(frm) {
      const me = this;
      if (me.advance_print_format_control) {
        me.advance_print_format_control.toggle(false);
        me._ape_unlock_advance_print_format();
        me.advance_print_format_control.set_value("");
      }
      const promise = original_show.apply(this, arguments);
      frappe.call({
        method: "advanced_print_engine.api.generate_pdf.get_available_templates",
        args: { reference_doctype: frm.doctype },
        callback(r) {
          if (r.message && r.message.length > 0 && me.advance_print_format_control) {
            me.advance_print_format_control.toggle(true);
          }
          me._ape_sync_linked_advanced_format();
        }
      });
      return promise;
    };
    const original_preview = PrintViewClass.prototype.preview;
    PrintViewClass.prototype.preview = function() {
      const me = this;
      const preview_id = me._ape_preview_id = (me._ape_preview_id || 0) + 1;
      me._ape_resolve_advance_format().then((advance_format) => {
        if (preview_id !== me._ape_preview_id) {
          return;
        }
        if (advance_format) {
          ape_load_smart_preview(me, advance_format, preview_id);
          return;
        }
        ape_reset_standard_preview_container(me);
        requestAnimationFrame(() => {
          if (preview_id !== me._ape_preview_id) {
            return;
          }
          original_preview.call(me);
        });
      });
    };
    const original_printit = PrintViewClass.prototype.printit;
    PrintViewClass.prototype.printit = function() {
      const me = this;
      me._ape_is_advanced_mode().then((is_advanced) => {
        if (is_advanced) {
          me._ape_resolve_advance_format().then((advance_format) => {
            if (advance_format) {
              window.render_smart_pdf(me.frm, advance_format);
            }
          });
          return;
        }
        original_printit.call(me);
      });
    };
    const original_render_pdf = PrintViewClass.prototype.render_pdf;
    PrintViewClass.prototype.render_pdf = function() {
      const me = this;
      me._ape_resolve_advance_format().then((advance_format) => {
        if (advance_format) {
          const baseUrl = frappe.urllib.get_base_url();
          const apiUrl = `${baseUrl}/api/method/advanced_print_engine.api.generate_pdf.generate_smart_pdf?doctype=${encodeURIComponent(me.frm.doctype)}&docname=${encodeURIComponent(me.frm.docname)}&print_format_name=${encodeURIComponent(advance_format)}`;
          window.open(apiUrl, "_blank");
          return;
        }
        original_render_pdf.call(me);
      });
    };
    const original_render_page = PrintViewClass.prototype.render_page;
    PrintViewClass.prototype.render_page = function(method, printit = false) {
      const me = this;
      me._ape_resolve_advance_format().then((advance_format) => {
        if (advance_format) {
          const baseUrl = frappe.urllib.get_base_url();
          const apiUrl = `${baseUrl}/api/method/advanced_print_engine.api.generate_pdf.generate_smart_pdf?doctype=${encodeURIComponent(me.frm.doctype)}&docname=${encodeURIComponent(me.frm.docname)}&print_format_name=${encodeURIComponent(advance_format)}`;
          if (printit) {
            window.render_smart_pdf(me.frm, advance_format);
          } else {
            window.open(apiUrl, "_blank");
          }
          return;
        }
        original_render_page.call(me, method, printit);
      });
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
//# sourceMappingURL=advanced_print_engine.bundle.M2VGLE2P.js.map
