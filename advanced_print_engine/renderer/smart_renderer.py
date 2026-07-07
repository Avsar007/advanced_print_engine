import os
import frappe
from playwright.sync_api import sync_playwright

class SmartRenderer:
    def __init__(self, doctype, docname, print_format_name):
        self.doctype = doctype
        self.docname = docname
        self.print_format_name = print_format_name
        self.doc = frappe.get_doc(doctype, docname)
        self.print_format = frappe.get_doc("Advanced Print Format", print_format_name)

    def get_payload(self):
        context = {
            "doc": self.doc,
            "frappe": frappe,
            "utils": frappe.utils
        }
        
        rendered_body = frappe.render_template(self.print_format.body_html or "", context)
        default_header = frappe.render_template(self.print_format.default_header_html or "", context)
        default_footer = frappe.render_template(self.print_format.default_footer_html or "", context)
        
        header_rules = []
        for rule in self.print_format.get("header_rules"):
            header_rules.append({ 
                "rule_type": rule.rule_type,
                "page_number": rule.page_number,
                "html_content": frappe.render_template(rule.html_content or "", context)
            })
                
        footer_rules = []
        for rule in self.print_format.get("footer_rules"):
            footer_rules.append({
                "rule_type": rule.rule_type,
                "page_number": rule.page_number,
                "html_content": frappe.render_template(rule.html_content or "", context)
            })

        custom_css = self.print_format.custom_css or ""
        page_size = self.print_format.page_size or "A4"
        orientation = self.print_format.orientation or "Portrait"
        repeat_header = bool(self.print_format.repeat_header)
        repeat_footer = bool(self.print_format.repeat_footer)

        return {
            "body_html": rendered_body,
            "default_header": default_header,
            "default_footer": default_footer,
            "header_rules": header_rules,
            "footer_rules": footer_rules,
            "custom_css": custom_css,
            "page_size": page_size,
            "orientation": orientation,
            "repeat_header": repeat_header,
            "repeat_footer": repeat_footer
        }

    def render_and_generate_pdf(self):
        payload = self.get_payload()
        return self._generate_via_playwright(payload)

    def render_html(self):
        payload = self.get_payload()
        return self.get_html_template(payload, is_preview=True)

    def get_html_template(self, payload, is_preview=False):
        dimensions = {
            "A4": {"width": 794, "height": 1123},
            "Letter": {"width": 816, "height": 1056},
            "Legal": {"width": 816, "height": 1344}
        }
        size = dimensions.get(payload["page_size"], {"width": 794, "height": 1123})
        is_landscape = (payload["orientation"] == "Landscape")
        
        viewport_width = size["height"] if is_landscape else size["width"]
        viewport_height = size["width"] if is_landscape else size["height"]

        base_url = frappe.utils.get_url()
        
        preview_styles = ""
        if is_preview:
            preview_styles = """
            @media screen {
                body {
                    background-color: #ffffff !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .page {
                    background-color: #ffffff !important;
                    border-bottom: 2px dashed #cbd5e1 !important;
                    margin: 0 !important;
                    padding: 40px !important;
                    height: 100vh !important;
                    width: 100% !important;
                    box-shadow: none !important;
                    border-radius: 0 !important;
                    border-top: none !important;
                    border-left: none !important;
                    border-right: none !important;
                }
                .page:last-child {
                    border-bottom: none !important;
                }
            }
            """

        html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<base href="{base_url}">
<style>
*, *:before, *:after { box-sizing: border-box; }
body { margin: 0; padding: 0; background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: sans-serif; }
.page {
    width: 100%;
    height: 100vh;
    page-break-after: always;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-start; 
    padding: 40px;
}
.page:last-child {
    page-break-after: auto;
}
.page-header { width: 100%; flex-shrink: 0; margin-bottom: 0px; }
.page-body { 
    width: 100%; 
    flex-grow: 1; 
    display: flex;
    flex-direction: column;
    overflow-wrap: break-word; 
    word-wrap: break-word; 
}
.page-footer { width: 100%; flex-shrink: 0; margin-top: auto; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 0px; text-align: left; }

.page .page-body > table {
    flex-grow: 1;
    height: 100%;
}
.page .page-body > table > tbody > tr > td {
    vertical-align: top;
    height: 1px;
}
.page .page-body > table > tbody > tr:last-child > td {
    height: auto;
}

/* User Custom CSS */
{custom_css}

/* Interactive Preview styles */
{preview_styles}
</style>
</head>
<body>
<div id="measure-area" style="position: absolute; top: 0; left: 0; width: 100%; visibility: hidden; z-index: -1; padding: 0px;"></div>
<div id="render-target"></div>
<div id="pagination-done" style="display: none;"></div>

<script>
    window.paginate = async function(config) {
        if (window._paginating || (document.getElementById("pagination-done") && document.getElementById("pagination-done").style.display === "block")) return;
        window._paginating = true;
        
        const measureArea = document.getElementById("measure-area");
        if (!measureArea) {
            window._paginating = false;
            return;
        }
        const renderTarget = document.getElementById("render-target");
        
        async function waitForImages(element) {
            const images = Array.from(element.querySelectorAll('img'));
            await Promise.all(images.map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise(resolve => {
                    img.onload = img.onerror = resolve;
                });
            }));
        }

        const pagePadding = 40; 
        const headerMarginBottom = 0;
        const footerMarginTop = 0;

        const gauge = document.createElement('div');
        gauge.className = 'page';
        gauge.style.visibility = 'hidden';
        gauge.style.position = 'absolute';
        document.body.appendChild(gauge);
        const totalPageHeight = gauge.offsetHeight || {viewport_height};
        const totalPageWidth = gauge.offsetWidth || {viewport_width};
        document.body.removeChild(gauge);

        const maxInnerHeight = totalPageHeight - (pagePadding * 2);
        const contentWidth = totalPageWidth - (pagePadding * 2);
        
        function getHeaderHtml(pageIdx, totalPages) {
            const isLast = (totalPages && pageIdx === totalPages);
            const specific = config.header_rules.find(r => r.rule_type === 'Specific Page' && r.page_number === pageIdx);
            if (specific) return specific.html_content;
            if (pageIdx === 1) {
                const first = config.header_rules.find(r => r.rule_type === 'First Page');
                if (first) return first.html_content;
            }
            if (isLast) {
                const last = config.header_rules.find(r => r.rule_type === 'Last Page');
                if (last) return last.html_content;
            }
            if (config.repeat_header || pageIdx === 1) {
                return config.default_header || "";
            }
            return "";
        }

        function getFooterHtml(pageIdx, totalPages) {
            const isLast = (totalPages && pageIdx === totalPages);
            const specific = config.footer_rules.find(r => r.rule_type === 'Specific Page' && r.page_number === pageIdx);
            if (specific) return specific.html_content;
            if (pageIdx === 1) {
                const first = config.footer_rules.find(r => r.rule_type === 'First Page');
                if (first) return first.html_content;
            }
            if (isLast) {
                const last = config.footer_rules.find(r => r.rule_type === 'Last Page');
                if (last) return last.html_content;
            }
            if (config.repeat_footer || isLast) {
                return config.default_footer || "";
            }
            return "";
        }

        async function measureHtmlHeight(htmlString, className) {
            if (!htmlString || !htmlString.trim()) return 0;
            const wrapper = document.createElement('div');
            wrapper.style.position = 'absolute';
            wrapper.style.visibility = 'hidden';
            wrapper.style.top = '0';
            wrapper.style.left = '0';
            wrapper.style.width = contentWidth + 'px';
            wrapper.innerHTML = `<div class="${className || ''}" style="margin:0; padding:0;">${htmlString}</div>`;
            document.body.appendChild(wrapper);
            await waitForImages(wrapper);
            const height = wrapper.offsetHeight;
            document.body.removeChild(wrapper);
            return height;
        }

        measureArea.innerHTML = config.body_html;
        await waitForImages(measureArea);
        
        const chunks = [];
        const bodyChildren = Array.from(measureArea.children);
        
        let dummyRowTemplate = "";

        for (let el of bodyChildren) {
            if (el.tagName.toLowerCase() === 'table') {
                const thead = el.querySelector('thead');
                const colgroup = el.querySelector('colgroup');
                const tbody = el.querySelector('tbody');
                const rows = tbody ? Array.from(tbody.querySelectorAll('tr')) : Array.from(el.querySelectorAll('tr'));
                
                const shellHtml = `<table class="${el.className}" style="${el.getAttribute('style') || ''} width: 100%; border-collapse: collapse; margin: 0; padding: 0;">${colgroup ? colgroup.outerHTML : ''}${thead ? thead.outerHTML : ''}<tbody></tbody></table>`;
                const shellHeight = await measureHtmlHeight(shellHtml, 'page-body');
                
                chunks.push({
                    type: 'table_start',
                    tableClass: el.className,
                    tableStyle: el.getAttribute('style') || '',
                    theadHtml: thead ? thead.outerHTML : '',
                    colgroupHtml: colgroup ? colgroup.outerHTML : '',
                    shellHeight: shellHeight
                });
                
                for (let tr of rows) {
                    if (!dummyRowTemplate) {
                        let cloneTr = tr.cloneNode(true);
                        let cells = cloneTr.querySelectorAll('td, th');
                        cells.forEach(td => td.innerHTML = ''); 
                        dummyRowTemplate = cloneTr.outerHTML;
                    }

                    const rowTableHtml = `<table class="${el.className}" style="${el.getAttribute('style') || ''} width: 100%; border-collapse: collapse; margin: 0; padding: 0;">${colgroup ? colgroup.outerHTML : ''}${thead ? thead.outerHTML : ''}<tbody>${tr.outerHTML}</tbody></table>`;
                    const rowHeightWithHeader = await measureHtmlHeight(rowTableHtml, 'page-body');
                    
                    let actualRowHeight = rowHeightWithHeader - shellHeight;
                    if (actualRowHeight < 0) actualRowHeight = 0; 
                    
                    chunks.push({
                        type: 'table_row',
                        html: tr.outerHTML,
                        height: actualRowHeight
                    });
                }
                
                chunks.push({ type: 'table_end', height: 0 });
            } else {
                chunks.push({
                    type: 'block',
                    html: el.outerHTML,
                    height: await measureHtmlHeight(el.outerHTML, 'page-body')
                });
            }
        }

        async function getHeightsForPage(pageIdx) {
            const hHeight = await measureHtmlHeight(getHeaderHtml(pageIdx, null), 'page-header');
            
            const stdFHtml = getFooterHtml(pageIdx, pageIdx + 1); 
            const stdFHeight = await measureHtmlHeight(stdFHtml, 'page-footer');
            
            const lastFHtml = getFooterHtml(pageIdx, pageIdx);
            const lastFHeight = await measureHtmlHeight(lastFHtml, 'page-footer');
            
            return {
                stdAvail: maxInnerHeight - hHeight - stdFHeight - headerMarginBottom - footerMarginTop,
                lastAvail: maxInnerHeight - hHeight - lastFHeight - headerMarginBottom - footerMarginTop
            };
        }

        const pages = [];
        let currentPage = {
            pageIdx: 1,
            bodyHtmlStrings: [],
            currentBodyHeight: 0,
            inTable: false,
            tableShell: null
        };
        pages.push(currentPage);

        let heights = await getHeightsForPage(currentPage.pageIdx);
        const safeBuffer = 5;
        let lastSeenTableShell = null;

        for (let i = 0; i < chunks.length; i++) {
            const chunk = chunks[i];
            
            if (chunk.type === 'table_start') {
                currentPage.inTable = true;
                currentPage.tableShell = chunk;
                lastSeenTableShell = chunk;
                currentPage.bodyHtmlStrings.push({
                    type: 'table',
                    shell: chunk,
                    rowsHtml: []
                });
                currentPage.currentBodyHeight += chunk.shellHeight;
                continue;
            }
            
            if (chunk.type === 'table_end') {
                currentPage.inTable = false;
                currentPage.tableShell = null;
                continue;
            }

            const itemHeight = chunk.height || 0;
            
            if (currentPage.currentBodyHeight + itemHeight > (heights.stdAvail - safeBuffer) && currentPage.currentBodyHeight > 0) {
                currentPage = {
                    pageIdx: pages.length + 1,
                    bodyHtmlStrings: [],
                    currentBodyHeight: 0,
                    inTable: currentPage.inTable,
                    tableShell: currentPage.tableShell
                };
                pages.push(currentPage);
                
                heights = await getHeightsForPage(currentPage.pageIdx);
                
                if (currentPage.inTable && currentPage.tableShell) {
                    currentPage.bodyHtmlStrings.push({
                        type: 'table',
                        shell: currentPage.tableShell,
                        rowsHtml: []
                    });
                    currentPage.currentBodyHeight += currentPage.tableShell.shellHeight;
                }
            }

            if (chunk.type === 'table_row') {
                const lastTableBlock = currentPage.bodyHtmlStrings[currentPage.bodyHtmlStrings.length - 1];
                lastTableBlock.rowsHtml.push(chunk.html);
            } else {
                currentPage.bodyHtmlStrings.push({
                    type: 'block',
                    html: chunk.html
                });
            }
            currentPage.currentBodyHeight += itemHeight;
        }

        if (currentPage.currentBodyHeight > (heights.lastAvail - safeBuffer)) {
            let overflowPage = {
                pageIdx: pages.length + 1,
                bodyHtmlStrings: [],
                currentBodyHeight: 0,
                inTable: false,
                tableShell: null
            };
            
            if (lastSeenTableShell) {
                overflowPage.bodyHtmlStrings.push({
                    type: 'table',
                    shell: lastSeenTableShell,
                    rowsHtml: dummyRowTemplate ? [dummyRowTemplate] : [] 
                });
            }
            
            pages.push(overflowPage);
        }

        const totalPages = pages.length;
        let finalHtml = "";

        for (let p of pages) {
            const hHtml = getHeaderHtml(p.pageIdx, totalPages);
            const fHtml = getFooterHtml(p.pageIdx, totalPages);
            
            let pBodyContent = "";
            p.bodyHtmlStrings.forEach(block => {
                if (block.type === 'table') {
                    pBodyContent += `<table class="${block.shell.tableClass}" style="${block.shell.tableStyle}">${block.shell.colgroupHtml}${block.shell.theadHtml}<tbody>${block.rowsHtml.join('')}</tbody></table>`;
                } else {
                    pBodyContent += block.html;
                }
            });

            finalHtml += `
            <div class="page" data-page-number="${p.pageIdx}">
                ${hHtml ? `<div class="page-header">${hHtml}</div>` : ''}
                <div class="page-body">${pBodyContent}</div>
                ${fHtml ? `<div class="page-footer">${fHtml}</div>` : ''}
            </div>`;
        }

        renderTarget.innerHTML = finalHtml;
        if (measureArea) measureArea.remove();
        document.getElementById("pagination-done").style.display = "block";
        window._paginating = false;
        return totalPages;
    };

    // Auto-run pagination on DOM load
    window.addEventListener('DOMContentLoaded', () => {
        window.paginate({payload_json});
    });
</script>
</body>
</html>"""
        html_template = html_template.replace("{base_url}", base_url)
        html_template = html_template.replace("{custom_css}", payload["custom_css"])
        html_template = html_template.replace("{preview_styles}", preview_styles)
        html_template = html_template.replace("{viewport_width}", str(viewport_width))
        html_template = html_template.replace("{viewport_height}", str(viewport_height))
        html_template = html_template.replace("{payload_json}", frappe.as_json(payload))
        return html_template

    def _generate_via_playwright(self, payload):
        dimensions = {
            "A4": {"width": 794, "height": 1123},
            "Letter": {"width": 816, "height": 1056},
            "Legal": {"width": 816, "height": 1344}
        }
        size = dimensions.get(payload["page_size"], {"width": 794, "height": 1123})
        is_landscape = (payload["orientation"] == "Landscape")
        
        viewport_width = size["height"] if is_landscape else size["width"]
        viewport_height = size["width"] if is_landscape else size["height"]

        html_template = self.get_html_template(payload, is_preview=False)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height}
            )
            page = context.new_page()
            
            # FIX 3: Wait until the network is completely idle to ensure the logo is fetched!
            page.set_content(html_template, wait_until="networkidle")
            
            page.evaluate("async (payload) => await window.paginate(payload)", payload)
            page.wait_for_selector("#pagination-done", state="attached")

            pdf_bytes = page.pdf(
                format=payload["page_size"],
                landscape=is_landscape,
                print_background=True,
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
            )

            try:
                final_html = page.content()
                bench_tmp_path = os.path.join(frappe.utils.get_bench_path(), "tmp")
                if not os.path.exists(bench_tmp_path):
                    os.makedirs(bench_tmp_path)
                
                debug_path = os.path.join(bench_tmp_path, "tmp.html")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(final_html)
                frappe.logger().info(f"Advanced Print Engine: Saved debug HTML to {debug_path}")
            except Exception as e:
                frappe.logger().error(f"Advanced Print Engine: Failed to save debug HTML: {str(e)}")
            
            browser.close()
            return pdf_bytes