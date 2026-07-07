import frappe
from playwright.sync_api import sync_playwright
import os
import traceback

def screenshot_layout():
	try:
		doc = frappe.get_doc("Sales Invoice", "SINV-26-00001")
		pf = frappe.get_doc("Print Format", "Sales invoice")
		
		context = {
			"doc": doc,
			"frappe": frappe,
			"utils": frappe.utils
		}
		
		html = frappe.render_template(pf.html, context)
		css = f"<style>{pf.css}</style>"
		
		# Wrap in standard HTML structure
		full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css}</head><body style='margin:0; padding:0;'>{html}</body></html>"
		
		tmp_dir = "/home/avasar/frappe-bench/tmp"
		if not os.path.exists(tmp_dir):
			os.makedirs(tmp_dir)
			
		html_path = os.path.join(tmp_dir, "test_30_items.html")
		with open(html_path, "w", encoding="utf-8") as f:
			f.write(full_html)
			
		print("Launching Playwright...")
		with sync_playwright() as p:
			# Launch chromium
			browser = p.chromium.launch(headless=True)
			page = browser.new_page()
			page.set_content(full_html, wait_until="networkidle")
			
			# Select all elements with class .page
			pages = page.query_selector_all(".page")
			print(f"Found {len(pages)} pages in DOM.")
			
			for idx, pg_el in enumerate(pages):
				png_path = os.path.join(tmp_dir, f"page_30_rendered_p{idx+1}.png")
				pg_el.screenshot(path=png_path)
				print(f"Saved screenshot for Page {idx+1} to: {png_path}")
				
			browser.close()
	except Exception as e:
		print("ERROR IN screenshot_layout:")
		traceback.print_exc()


def test_smart_render_time():
	import time
	from advanced_print_engine.renderer.smart_renderer import SmartRenderer
	
	print("Starting SmartRenderer time test...")
	start_time = time.time()
	
	renderer = SmartRenderer("Sales Invoice", "SINV-26-00001", "Sales invoice")
	
	# Test HTML rendering
	html_start = time.time()
	html_content = renderer.render_html()
	html_duration = time.time() - html_start
	print(f"render_html() duration: {html_duration:.4f} seconds (length: {len(html_content)})")
	
	# Test PDF rendering
	pdf_start = time.time()
	pdf_bytes = renderer.render_and_generate_pdf()
	pdf_duration = time.time() - pdf_start
	print(f"render_and_generate_pdf() duration: {pdf_duration:.4f} seconds (length: {len(pdf_bytes)})")
	
	total_duration = time.time() - start_time
	print(f"Total test duration: {total_duration:.4f} seconds")
