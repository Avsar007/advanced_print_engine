# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import os
import re
import frappe
from frappe.model.document import Document



def estimate_html_height(html_content):
	if not html_content or not html_content.strip():
		return 0
		
	# Handle conditional branches by splitting on {% else %} or {% elif ... %}
	# to estimate only the active branch height instead of summing them.
	branches = re.split(r'\{%\s*(?:else|elif)[^%]*%\}', html_content)
	if len(branches) > 1:
		return max(estimate_html_height(b) for b in branches)
	
	# Strip Jinja template tags ({% ... %}, {{ ... }}, {# ... #}) to avoid parsing issues
	html = re.sub(r'\{%.*?%\}', '', html_content, flags=re.DOTALL)
	html = re.sub(r'\{\{.*?\}\}', 'XXXXXXXXXXXX', html) # replace value expressions with dummy text
	html = re.sub(r'\{#.*?#\}', '', html, flags=re.DOTALL)
	
	# Clean HTML comments
	html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
	
	# Extract explicit heights in style tags or attributes
	height_matches = re.findall(r'height:\s*(\d+)px', html)
	max_height_matches = re.findall(r'max-height:\s*(\d+)px', html)
	explicit_height = 0
	if height_matches:
		explicit_height = max(int(h) for h in height_matches)
	elif max_height_matches:
		explicit_height = max(int(h) for h in max_height_matches)

	# Find all table rows
	rows = re.findall(r'<tr[^>]*>.*?</tr>', html, flags=re.DOTALL | re.IGNORECASE)
	row_heights_sum = 0
	
	for row in rows:
		# Find cells inside this row
		cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, flags=re.DOTALL | re.IGNORECASE)
		if not cells:
			row_heights_sum += 17
			continue
			
		cell_heights = []
		for cell in cells:
			br_count = len(re.findall(r'<br\s*/?>', cell, re.IGNORECASE))
			p_count = len(re.findall(r'<p[^>]*>', cell, re.IGNORECASE))
			div_count = len(re.findall(r'<div[^>]*>', cell, re.IGNORECASE))
			li_count = len(re.findall(r'<li[^>]*>', cell, re.IGNORECASE))
			
			lines = max(1, br_count + p_count + div_count + li_count)
			cell_h = lines * 13
			
			# Images in this cell
			img_matches = re.findall(r'<img[^>]*>', cell, re.IGNORECASE)
			for img in img_matches:
				img_h = re.search(r'height:\s*(\d+)px', img)
				if img_h:
					cell_h += int(img_h.group(1))
				else:
					cell_h += 80 # default estimated image height
			cell_heights.append(cell_h)
			
		row_heights_sum += max(17, max(cell_heights))

	# Strip rows from html to find remaining flow text
	remaining_html = html
	for row in rows:
		remaining_html = remaining_html.replace(row, '')
		
	# Estimate height of remaining flow layout
	br_count = len(re.findall(r'<br\s*/?>', remaining_html, re.IGNORECASE))
	p_count = len(re.findall(r'<p[^>]*>', remaining_html, re.IGNORECASE))
	div_count = len(re.findall(r'<div[^>]*>', remaining_html, re.IGNORECASE))
	li_count = len(re.findall(r'<li[^>]*>', remaining_html, re.IGNORECASE))
	
	flow_lines = br_count + p_count + div_count + li_count
	flow_h = flow_lines * 18
	
	# Images in remaining flow layout
	img_matches = re.findall(r'<img[^>]*>', remaining_html, re.IGNORECASE)
	for img in img_matches:
		img_h = re.search(r'height:\s*(\d+)px', img)
		if img_h:
			flow_h += int(img_h.group(1))
		else:
			flow_h += 80
			
	estimated = row_heights_sum + flow_h
	
	final_h = max(explicit_height, estimated)
	return final_h + 10


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

	@frappe.whitelist()
	def run_measurements(self):
		from playwright.sync_api import sync_playwright
		doc = frappe.get_doc("Sales Invoice", "SINV-26-00001")
		pf = frappe.get_doc("Print Format", "sales")
		context = {"doc": doc, "frappe": frappe, "utils": frappe.utils}
		html = frappe.render_template(pf.html, context)
		css = f"<style>{pf.css}</style>"
		full_html = f"<!DOCTYPE html><html><head>{css}</head><body style='margin:0; padding:0;'>{html}</body></html>"
		with open("/home/avasar/frappe-bench/tmp/rendered_test.html", "w", encoding="utf-8") as f:
			f.write(full_html)
		with sync_playwright() as p:
			browser = p.chromium.launch(headless=True)
			page = browser.new_page()
			page.set_content(full_html, wait_until="networkidle")
			measurements = page.evaluate("() => { const page = document.querySelector('.page'); const header = document.querySelector('.page-header'); const body = document.querySelector('.page-body'); const table = document.querySelector('.page-body > table'); const footer = document.querySelector('.page-footer'); return { page_h: page ? page.offsetHeight : 0, header_h: header ? header.offsetHeight : 0, body_h: body ? body.offsetHeight : 0, table_h: table ? table.offsetHeight : 0, footer_h: footer ? footer.offsetHeight : 0 }; }")
			browser.close()
			measurements["items_count"] = len(doc.items)
			return measurements

	@frappe.whitelist()
	def export_jinja_html(self):
		# Create safe filename
		safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', self.name)
		filename = f"compiled_{safe_name}.html"
		
		tmp_dir = os.path.join(frappe.utils.get_bench_path(), "tmp")
		if not os.path.exists(tmp_dir):
			os.makedirs(tmp_dir)
		filepath = os.path.join(tmp_dir, filename)

		# 1. Translate header rules to Jinja conditional block
		header_logic = []
		header_rules = self.get("header_rules") or []
		
		# Specific page rules
		for rule in header_rules:
			if rule.enabled and rule.rule_type == "Specific Page":
				header_logic.append(f"{{% if pg.page_no == {rule.page_number} %}}\n{rule.html_content or ''}")
				
		# First page rule
		first_header_rule = next((r for r in header_rules if r.enabled and r.rule_type == "First Page"), None)
		if first_header_rule:
			if header_logic:
				header_logic.append(f"{{% elif pg.page_no == 1 %}}\n{first_header_rule.html_content or ''}")
			else:
				header_logic.append(f"{{% if pg.page_no == 1 %}}\n{first_header_rule.html_content or ''}")
		else:
			if header_logic:
				header_logic.append(f"{{% elif pg.page_no == 1 %}}\n{self.default_header_html or ''}")
			else:
				header_logic.append(f"{{% if pg.page_no == 1 %}}\n{self.default_header_html or ''}")

		# Last page rule
		last_header_rule = next((r for r in header_rules if r.enabled and r.rule_type == "Last Page"), None)
		if last_header_rule:
			header_logic.append(f"{{% elif pg.is_last %}}\n{last_header_rule.html_content or ''}")
		else:
			if self.repeat_header:
				header_logic.append(f"{{% elif pg.is_last %}}\n{self.default_header_html or ''}")
			else:
				header_logic.append(f"{{% elif pg.is_last %}}\n")

		# Standard/Repeat header
		if self.repeat_header:
			header_logic.append(f"{{% else %}}\n{self.default_header_html or ''}\n{{% endif %}}")
		else:
			header_logic.append(f"{{% else %}}\n\n{{% endif %}}")

		header_jinja_block = "\n".join(header_logic)

		# 2. Translate footer rules to Jinja conditional block
		# 2. Translate footer rules to Jinja conditional block
		footer_logic = []
		footer_rules = self.get("footer_rules") or []

		# Last page rule (must be evaluated first so it takes precedence on 1-page documents)
		last_footer_rule = next((r for r in footer_rules if r.enabled and r.rule_type == "Last Page"), None)
		if last_footer_rule:
			footer_logic.append(f"{{% if pg.is_last %}}\n{last_footer_rule.html_content or ''}")
		else:
			footer_logic.append(f"{{% if pg.is_last %}}\n{self.default_footer_html or ''}")

		# Specific page rules
		for rule in footer_rules:
			if rule.enabled and rule.rule_type == "Specific Page":
				footer_logic.append(f"{{% elif pg.page_no == {rule.page_number} %}}\n{rule.html_content or ''}")

		# First page rule
		first_footer_rule = next((r for r in footer_rules if r.enabled and r.rule_type == "First Page"), None)
		if first_footer_rule:
			footer_logic.append(f"{{% elif pg.page_no == 1 %}}\n{first_footer_rule.html_content or ''}")
		else:
			if self.repeat_footer:
				footer_logic.append(f"{{% elif pg.page_no == 1 %}}\n{self.default_footer_html or ''}")
			else:
				footer_logic.append(f"{{% elif pg.page_no == 1 %}}\n")

		# Standard/Repeat footer
		if self.repeat_footer:
			footer_logic.append(f"{{% else %}}\n{self.default_footer_html or ''}\n{{% endif %}}")
		else:
			footer_logic.append(f"{{% else %}}\n\n{{% endif %}}")

		footer_jinja_block = "\n".join(footer_logic)

		# 3. Parse and rewrite body_html to support slicing, empty rows, and last-page totals wrapper
		body_html = self.body_html or ""
		
		# Find the loop over doc.items or doc.get("items")
		loop_regex = r'\{%\s*for\s+(\w+)\s+in\s+doc\.(items|get\(\s*[\'"]items[\'"]\s*\))\s*%\}'
		match = re.search(loop_regex, body_html)
		if match:
			var_name = match.group(1)
			# Replace the loop start with a sliced items loop
			body_html = re.sub(
				loop_regex,
				f"{{% set end = pg.start + pg.count %}}{{% for {var_name} in doc.items[pg.start:end] %}}",
				body_html,
				count=1
			)
			
			# Estimate column count to populate empty row columns
			tr_match = re.search(r'<tr[^>]*>([\s\S]*?)</tr>', body_html)
			col_count = 1
			if tr_match:
				cols = re.findall(r'<td|<th', tr_match.group(1))
				col_count = len(cols) or 1
				
			empty_tds = "".join(["<td>&nbsp;</td>"] * col_count)
			empty_rows_code = f"""
            {{% if pg.empty_rows and pg.empty_rows > 0 %}}
            {{% for i in range(pg.empty_rows|int) %}}
                <tr>
                    {empty_tds}
                </tr>
            {{% endfor %}}
            {{% endif %}}
"""
			# Insert empty rows right after the loop closes
			body_html = body_html.replace("{% endfor %}", f"{{% endfor %}}\n{empty_rows_code}", 1)

		# Wrap subsequent content (after the items table) in is_last page condition
		parts = re.split(r'</table>', body_html, maxsplit=1)
		if len(parts) > 1:
			body_html = parts[0] + "</table>\n{% if pg.is_last %}\n" + parts[1] + "\n{% endif %}"

		# Determine A4/Letter/Legal dimensions
		page_w = "210mm"
		page_h = "297mm"
		if self.page_size == "Letter":
			page_w = "215.9mm"
			page_h = "279.4mm"
		elif self.page_size == "Legal":
			page_w = "215.9mm"
			page_h = "355.6mm"

		# Estimate heights of headers and footers dynamically
		default_header_h = estimate_html_height(self.default_header_html)
		default_footer_h = estimate_html_height(self.default_footer_html)

		# Header rules mapping
		header_rules = self.get("header_rules") or []
		first_header_rule = next((r for r in header_rules if r.enabled and r.rule_type == "First Page"), None)
		first_header_h = estimate_html_height(first_header_rule.html_content) if first_header_rule else default_header_h

		last_header_rule = next((r for r in header_rules if r.enabled and r.rule_type == "Last Page"), None)
		if last_header_rule:
			last_header_h = estimate_html_height(last_header_rule.html_content)
		else:
			last_header_h = default_header_h if self.repeat_header else 0

		other_header_h = default_header_h if self.repeat_header else 0

		# Specific page headers
		specific_headers_dict = {}
		for rule in header_rules:
			if rule.enabled and rule.rule_type == "Specific Page":
				specific_headers_dict[rule.page_number] = estimate_html_height(rule.html_content)

		# Footer rules mapping
		footer_rules = self.get("footer_rules") or []
		first_footer_rule = next((r for r in footer_rules if r.enabled and r.rule_type == "First Page"), None)
		first_footer_h = estimate_html_height(first_footer_rule.html_content) if first_footer_rule else (default_footer_h if self.repeat_footer else 0)

		last_footer_rule = next((r for r in footer_rules if r.enabled and r.rule_type == "Last Page"), None)
		if last_footer_rule:
			last_footer_h = estimate_html_height(last_footer_rule.html_content)
		else:
			last_footer_h = default_footer_h

		other_footer_h = default_footer_h if self.repeat_footer else 0

		# Specific page footers
		specific_footers_dict = {}
		for rule in footer_rules:
			if rule.enabled and rule.rule_type == "Specific Page":
				specific_footers_dict[rule.page_number] = estimate_html_height(rule.html_content)

		# Calculate page dimensions in mm (excluding 10mm top/bottom browser margins with 0.5mm safety buffer)
		if self.page_size == "Letter":
			page_w = "100%"
			page_h = "258.9mm"
			usable_page_height = 958
		elif self.page_size == "Legal":
			page_w = "100%"
			page_h = "335.1mm"
			usable_page_height = 1246
		else:
			page_w = "100%"
			page_h = "276.5mm"
			usable_page_height = 1025

		# Estimate heights of headers and footers dynamically
		default_header_h = estimate_html_height(self.default_header_html)
		default_footer_h = estimate_html_height(self.default_footer_html)

		# Header rules mapping
		header_rules = self.get("header_rules") or []
		first_header_rule = next((r for r in header_rules if r.enabled and r.rule_type == "First Page"), None)
		first_header_h = estimate_html_height(first_header_rule.html_content) if first_header_rule else default_header_h

		last_header_rule = next((r for r in header_rules if r.enabled and r.rule_type == "Last Page"), None)
		if last_header_rule:
			last_header_h = estimate_html_height(last_header_rule.html_content)
		else:
			last_header_h = default_header_h if self.repeat_header else 0

		other_header_h = default_header_h if self.repeat_header else 0

		# Specific page headers
		specific_headers_dict = {}
		for rule in header_rules:
			if rule.enabled and rule.rule_type == "Specific Page":
				specific_headers_dict[rule.page_number] = estimate_html_height(rule.html_content)

		# Footer rules mapping
		footer_rules = self.get("footer_rules") or []
		first_footer_rule = next((r for r in footer_rules if r.enabled and r.rule_type == "First Page"), None)
		first_footer_h = estimate_html_height(first_footer_rule.html_content) if first_footer_rule else (default_footer_h if self.repeat_footer else 0)

		last_footer_rule = next((r for r in footer_rules if r.enabled and r.rule_type == "Last Page"), None)
		if last_footer_rule:
			last_footer_h = estimate_html_height(last_footer_rule.html_content)
		else:
			last_footer_h = default_footer_h

		other_footer_h = default_footer_h if self.repeat_footer else 0

		# Specific page footers
		specific_footers_dict = {}
		for rule in footer_rules:
			if rule.enabled and rule.rule_type == "Specific Page":
				specific_footers_dict[rule.page_number] = estimate_html_height(rule.html_content)

		specific_headers_str = "{" + ", ".join(f"{k}: {v}" for k, v in specific_headers_dict.items()) + "}"
		specific_footers_str = "{" + ", ".join(f"{k}: {v}" for k, v in specific_footers_dict.items()) + "}"

		# 4. Construct separate CSS and HTML content
		css_content = f"""
/* Reset and override browser/frappe print margins & paddings */
@media print {{
    @page {{
        size: {self.page_size or "A4"} portrait !important;
        margin: 10mm !important; /* Explicit centered margins */
    }}
    html, body {{
        margin: 0 !important;
        padding: 0 !important;
        background: #fff !important;
        width: 100% !important;
    }}
    .print-format-gutter {{
        padding: 0 !important;
        background-color: transparent !important;
    }}
    .print-format {{
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: none !important;
        min-height: 0 !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }}
}}

/* Reset print-format styles to make it transparent & clean */
.print-format-gutter {{
    padding: 0 !important;
    background-color: #fff !important;
}}
.print-format {{
    padding: 0 !important;
    margin: 0 auto !important;
    width: 100% !important;
    max-width: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
}}

*, *:before, *:after {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 0; background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: sans-serif; }}

.page {{
    width: {page_w};
    height: {page_h};
    page-break-after: always;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-start; 
    padding: 10px; /* 10px spacing on all sides */
    background-color: #fff;
    box-sizing: border-box;
}}
.page:last-child {{
    page-break-after: auto;
}}
.page-header {{ 
    width: 100% !important; 
    flex-shrink: 0 !important; 
    margin: 0 !important; 
    padding: 0 !important; 
    border: none !important; 
}}
.page-body {{ 
    width: 100% !important; 
    flex-grow: 1 !important; 
    display: flex !important;
    flex-direction: column !important;
    margin: 0 !important; 
    padding: 0 !important; 
    border: none !important;
    overflow-wrap: break-word !important; 
    word-wrap: break-word !important; 
}}
.page-footer {{ 
    width: 100% !important; 
    flex-shrink: 0 !important; 
    margin: 0 !important; 
    margin-top: auto !important; 
    padding: 0 !important; 
    border: none !important; 
}}

/* Force table formatting inside print-format wrapper */
.print-format table {{
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 0 !important;
    margin-bottom: 0 !important;
    margin-top: 0 !important;
}}
.page-body > table {{
    margin-top: -1px !important;
    flex-grow: 1 !important;
}}
.page-footer > table {{
    margin-top: -1px !important;
}}
.print-format th, .print-format td {{
    border: 1px solid black !important;
    font-size: 10px !important;
    padding: 2px 2px !important;
    margin: 0 !important;
    vertical-align: top !important;
    line-height: 13px !important;
}}

/* User Custom CSS */
{self.custom_css or ""}
"""

		html_content = f"""
{{% set total_page_height = {usable_page_height} %}}
{{% set first_page_header_h = {first_header_h} %}}
{{% set other_page_header_h = {other_header_h} %}}
{{% set last_page_header_h = {last_header_h} %}}

{{% set first_page_footer_h = {first_footer_h} %}}
{{% set other_page_footer_h = {other_footer_h} %}}
{{% set last_page_footer_h = {last_footer_h} %}}

{{% set specific_headers = {specific_headers_str} %}}
{{% set specific_footers = {specific_footers_str} %}}

{{% set table_header_h = 33 %}}
{{% set table_total_line_h = 18 %}}
{{% set row_unit_h = 17 %}}

{{% set row_heights = [] %}}
{{% set total_items = (doc.items|length) %}}
{{% set WRAP_AT_ITEM = 50 %}}
{{% set WRAP_AT_DESC = 66 %}}

{{% for it in doc.items %}}
  {{% set item_txt = (it.item_name or '')|trim %}}
  {{% set description_txt = (it.description or '')|trim %}}

  {{% set d_lines = description_txt and ((description_txt|length + WRAP_AT_ITEM - 1) // WRAP_AT_ITEM) or 0 %}}
  {{% set i_lines = ((item_txt|length + WRAP_AT_DESC - 1) // WRAP_AT_DESC) %}}
  {{% if i_lines < 1 %}}{{% set i_lines = 1 %}}{{% endif %}}

  {{% set lines = (d_lines > i_lines) and d_lines or i_lines %}}
  {{% set row_h = (lines * 13) + 4 %}}
  {{% set _ = row_heights.append({{'idx0': loop.index0, 'h': row_h|int}}) %}}
{{% endfor %}}

{{% set chrome_h = table_header_h + table_total_line_h %}}
{{% set items_sum = namespace(v=0) %}}
{{% for r in row_heights %}}{{% set items_sum.v = items_sum.v + r.h %}}{{% endfor %}}

{{% set total_ideal_height = first_page_header_h + chrome_h + items_sum.v + last_page_footer_h %}}
{{% set pages = [] %}}

{{% if total_ideal_height <= total_page_height %}}
  {{% set remaining = (total_page_height - total_ideal_height) %}}
  {{% set _ = pages.append({{
    'page_no': 1,
    'start': 0,
    'count': total_items,
    'used_table_h': items_sum.v,
    'remaining_table_h': remaining,
    'empty_rows': (remaining // row_unit_h)|int,
    'is_first': 1,
    'is_last': 1
  }}) %}}
{{% else %}}
  {{% set state = namespace(
    current_page_no=1,
    start_idx=0,
    current_used=0,
    current_count=0
  ) %}}
  {{% set done = namespace(val=0) %}}
  {{% set cap_first = total_page_height - first_page_header_h - chrome_h - first_page_footer_h %}}
  {{% set cap_other = total_page_height - other_page_header_h - chrome_h - other_page_footer_h %}}
  {{% if cap_first < 0 %}}{{% set cap_first = 0 %}}{{% endif %}}
  {{% if cap_other < 0 %}}{{% set cap_other = 0 %}}{{% endif %}}

  {{% for i in range(total_items) %}}
    {{% if done.val == 0 %}}
      {{% set remaining_items_h = namespace(v=0) %}}
      {{% for r in row_heights[i:] %}}
        {{% set remaining_items_h.v = remaining_items_h.v + r.h %}}
      {{% endfor %}}

      {{% set header_h = (state.current_page_no == 1) and first_page_header_h or other_page_header_h %}}
      {{% set total_needed = header_h + chrome_h + state.current_used + remaining_items_h.v + last_page_footer_h %}}

      {{% if total_needed <= total_page_height %}}
        {{% set remaining = total_page_height - total_needed %}}
        {{% set _ = pages.append({{
          'page_no': state.current_page_no,
          'start': state.start_idx,
          'count': total_items - state.start_idx,
          'used_table_h': state.current_used + remaining_items_h.v,
          'remaining_table_h': remaining,
          'empty_rows': (remaining // row_unit_h)|int,
          'is_first': (state.current_page_no == 1) and 1 or 0,
          'is_last': 1
        }}) %}}
        {{% set done.val = 1 %}}
      {{% else %}}
        {{% set r = row_heights[i] %}}
        {{% set cap = (state.current_page_no == 1) and cap_first or cap_other %}}

        {{% if state.current_used + r.h > cap and state.current_count > 0 %}}
          {{% set remaining = cap - state.current_used %}}
          {{% set _ = pages.append({{
            'page_no': state.current_page_no,
            'start': state.start_idx,
            'count': state.current_count,
            'used_table_h': state.current_used,
            'remaining_table_h': remaining,
            'empty_rows': (remaining // row_unit_h)|int,
            'is_first': (state.current_page_no == 1) and 1 or 0,
            'is_last': 0
          }}) %}}
          {{% set state.current_page_no = state.current_page_no + 1 %}}
          {{% set state.start_idx = i %}}
          {{% set state.current_used = 0 %}}
          {{% set state.current_count = 0 %}}
        {{% endif %}}

        {{% set state.current_used = state.current_used + r.h %}}
        {{% set state.current_count = state.current_count + 1 %}}
      {{% endif %}}
    {{% endif %}}
  {{% endfor %}}

  {{% if done.val == 0 and state.current_count > 0 %}}
    {{% set header_h = (state.current_page_no == 1) and first_page_header_h or other_page_header_h %}}
    {{% set total_needed = header_h + chrome_h + state.current_used + last_page_footer_h %}}
    {{% if total_needed <= total_page_height %}}
      {{% set remaining = total_page_height - total_needed %}}
      {{% set _ = pages.append({{
        'page_no': state.current_page_no,
        'start': state.start_idx,
        'count': state.current_count,
        'used_table_h': state.current_used,
        'remaining_table_h': remaining,
        'empty_rows': (remaining // row_unit_h)|int,
        'is_first': (state.current_page_no == 1) and 1 or 0,
        'is_last': 1
      }}) %}}
    {{% else %}}
      {{% set cap = (state.current_page_no == 1) and cap_first or cap_other %}}
      {{% set remaining = cap - state.current_used %}}
      {{% set _ = pages.append({{
        'page_no': state.current_page_no,
        'start': state.start_idx,
        'count': state.current_count,
        'used_table_h': state.current_used,
        'remaining_table_h': remaining,
        'empty_rows': (remaining // row_unit_h)|int,
        'is_first': (state.current_page_no == 1) and 1 or 0,
        'is_last': 0
      }}) %}}
      {{% set last_header_h = other_page_header_h %}}
      {{% set last_page_needed = last_header_h + chrome_h + last_page_footer_h %}}
      {{% set remaining_last = total_page_height - last_page_needed %}}
      {{% if remaining_last < 0 %}}{{% set remaining_last = 0 %}}{{% endif %}}
      {{% set _ = pages.append({{
        'page_no': state.current_page_no + 1,
        'start': total_items,
        'count': 0,
        'used_table_h': 0,
        'remaining_table_h': remaining_last,
        'empty_rows': (remaining_last // row_unit_h)|int,
        'is_first': 0,
        'is_last': 1
      }}) %}}
    {{% endif %}}
  {{% endif %}}
{{% endif %}}

{{% set total_pages = pages|length %}}
{{% for pg in pages %}}
    {{% if not loop.first %}}
        <div style="page-break-before: always;"></div>
    {{% endif %}}

    <div class="page" data-page-number="{{{{pg.page_no}}}}">
        <div class="page-header">
            {header_jinja_block}
        </div>
        <div class="page-body">
            {body_html}
        </div>
        <div class="page-footer">
            {footer_jinja_block}
        </div>
    </div>
{{% endfor %}}
"""

		# Construct a fully bundled HTML version for temporary/testing preview
		compiled_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<base href="{{{{ frappe.utils.get_url() }}}}">
<style>
{css_content}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""

		with open(filepath, "w", encoding="utf-8") as f:
			f.write(compiled_html)


		# Upsert Print Format in database
		pf_doc_name = frappe.db.get_value("Print Format", {"custom_advanced_print_format": self.name}, "name")
		pf_name = self.print_format_name or self.name

		if pf_doc_name:
			pf_doc = frappe.get_doc("Print Format", pf_doc_name)
			pf_doc.print_format_name = pf_name
		else:
			# Check if a Print Format with the target name already exists
			if frappe.db.exists("Print Format", pf_name):
				existing_linked = frappe.db.get_value("Print Format", pf_name, "custom_advanced_print_format")
				if existing_linked and existing_linked != self.name:
					frappe.throw(f"Print Format '{pf_name}' is already linked to another Advanced Print Format '{existing_linked}'. Please use a different Print Format Name.")
				pf_doc = frappe.get_doc("Print Format", pf_name)
				pf_doc.custom_advanced_print_format = self.name
			else:
				pf_doc = frappe.new_doc("Print Format")
				pf_doc.name = pf_name
				pf_doc.print_format_name = pf_name
				pf_doc.custom_advanced_print_format = self.name

		pf_doc.html = html_content
		pf_doc.css = css_content
		pf_doc.custom_format = 1
		pf_doc.print_format_type = "Jinja"
		pf_doc.doc_type = self.reference_doctype
		pf_doc.standard = "No"
		pf_doc.save(ignore_permissions=True)

		return filepath

	@frappe.whitelist()
	def test_rules(self):
		header_info = [(r.rule_type, r.enabled, len(r.html_content or '')) for r in self.header_rules]
		footer_info = [(r.rule_type, r.enabled, len(r.html_content or '')) for r in self.footer_rules]
		default_header_len = len(self.default_header_html or '')
		default_footer_len = len(self.default_footer_html or '')
		return {
			"header_info": header_info,
			"footer_info": footer_info,
			"default_header_len": default_header_len,
			"default_footer_len": default_footer_len,
			"estimated_default_header_h": estimate_html_height(self.default_header_html),
		}

