import frappe


def generate_demo_data():
	# Ensure Company exists safely
	company = frappe.db.get_value("Company", {})
	if not company:
		company_doc = frappe.get_doc(
			{"doctype": "Company", "company_name": "Demo Company", "default_currency": "USD"}
		)
		company_doc.insert(ignore_permissions=True)
		company = company_doc.name

	# Ensure Customer exists safely
	customer = frappe.db.get_value("Customer", {})
	if not customer:
		customer_doc = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": "Demo Customer",
			"customer_type": "Company",
			"customer_group": "Commercial"
		})
		customer_doc.insert(ignore_permissions=True)
		customer = customer_doc.name

	# Ensure Item exists safely
	item_code = frappe.db.get_value("Item", {})
	if not item_code:
		item_group = frappe.db.get_value("Item Group", {})
		if not item_group:
			ig = frappe.get_doc({
				"doctype": "Item Group",
				"item_group_name": "Products",
				"is_group": 0
			}).insert(ignore_permissions=True)
			item_group = ig.name

		item_doc = frappe.get_doc({
			"doctype": "Item",
			"item_code": "DEMO-ITEM-001",
			"item_name": "Demo Multi-Page Item",
			"item_group": item_group,
			"is_stock_item": 0
		})
		item_doc.insert(ignore_permissions=True)
		item_code = item_doc.name

	# Create Sales Order with 55 line items
	so = frappe.new_doc("Sales Order")
	so.customer = customer
	so.company = company
	so.delivery_date = frappe.utils.add_days(frappe.utils.nowdate(), 7)

	for i in range(1, 56):
		desc = f"Premium Custom Line Item #{i}\nThis item incorporates advanced dynamic row features and multi-line descriptions to rigorously verify automatic dynamic page height calculation logic."
		so.append(
			"items",
			{
				"item_code": item_code,
				"qty": 1,
				"rate": 100 + i,
				"description": desc,
				"delivery_date": so.delivery_date
			}
		)

	so.insert(ignore_permissions=True)
	print(f"Created demo Sales Order: {so.name}")

	# Create Advanced Print Format template for Sales Order
	template_name = "Premium Sales Order Multi-Page Template"
	if not frappe.db.exists("Advanced Print Format", {"print_format_name": template_name}):
		template = frappe.get_doc({
			"doctype": "Advanced Print Format",
			"print_format_name": template_name,
			"reference_doctype": "Sales Order",
			"page_size": "A4",
			"orientation": "Portrait",
			"repeat_header": 1,
			"repeat_footer": 1,
			"default_header_html": """
            <div style="border-bottom: 2px solid #4f46e5; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin: 0; color: #111827; font-weight: 800; font-size: 24px;">{{ doc.company }}</h2>
                    <span style="color: #6b7280; font-size: 12px;">Sales Order Template</span>
                </div>
                <div style="text-align: right;">
                    <h3 style="margin: 0; color: #4f46e5; font-size: 18px;">{{ doc.name }}</h3>
                    <span style="color: #6b7280; font-size: 12px;">Date: {{ frappe.utils.formatdate(doc.transaction_date) }}</span>
                </div>
            </div>
            """,
			"default_footer_html": """
            <div style="border-top: 1px solid #e5e7eb; padding-top: 10px; display: flex; justify-content: space-between; font-size: 11px; color: #9ca3af;">
                <span>Authorized Signature ___________________</span>
                <span>Page rendered via Advanced Print Engine</span>
            </div>
            """,
			"body_html": """
            <div style="margin-bottom: 25px; display: flex; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0 0 5px 0; color: #374151; font-size: 12px; text-transform: uppercase;">Customer Details:</h4>
                    <strong style="color: #111827; font-size: 14px;">{{ doc.customer }}</strong>
                </div>
                <div style="text-align: right;">
                    <span style="display: block; font-size: 12px; color: #4b5563;">Status: <strong style="color: #059669;">{{ doc.status }}</strong></span>
                </div>
            </div>

            <table class="so-items-table">
                <thead>
                    <tr style="background-color: #f3f4f6; border-bottom: 2px solid #d1d5db;">
                        <th style="width: 8%; text-align: center; font-size: 11px; color: #374151; text-transform: uppercase;">Sr</th>
                        <th style="width: 52%; font-size: 11px; color: #374151; text-transform: uppercase;">Description</th>
                        <th style="width: 15%; text-align: right; font-size: 11px; color: #374151; text-transform: uppercase;">Qty</th>
                        <th style="width: 25%; text-align: right; font-size: 11px; color: #374151; text-transform: uppercase;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in doc.items %}
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="text-align: center; font-size: 11px; color: #6b7280; vertical-align: top; padding-top: 10px;">{{ loop.index }}</td>
                        <td style="font-size: 12px; color: #1f2937; vertical-align: top; padding-top: 10px;">
                            <strong>{{ item.item_code }}</strong><br>
                            <span style="color: #4b5563; font-size: 11px; white-space: pre-line;">{{ item.description }}</span>
                        </td>
                        <td style="text-align: right; font-size: 12px; color: #111827; vertical-align: top; padding-top: 10px;">{{ item.qty }}</td>
                        <td style="text-align: right; font-size: 12px; color: #111827; font-weight: 600; vertical-align: top; padding-top: 10px;">{{ item.amount }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            """,
			"custom_css": """
            .so-items-table th, .so-items-table td {
                padding: 10px 12px;
            }
            """,
			"header_rules": [
				{
					"rule_type": "First Page",
					"html_content": """
                    <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: #fff; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                        <h1 style="margin: 0; font-size: 28px; font-weight: 900; letter-spacing: -0.5px;">SALES ORDER</h1>
                        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 13px;">{{ doc.company }} — Master Agreement</p>
                    </div>
                    """
				},
				{
					"rule_type": "Specific Page",
					"page_number": 2,
					"html_content": """
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #92400e; font-size: 12px; font-weight: 700;">Page 2 Specific Header Override</span>
                        <strong style="color: #b45309; font-size: 12px;">{{ doc.name }}</strong>
                    </div>
                    """
				}
			],
			"footer_rules": [
				{
					"rule_type": "Last Page",
					"html_content": """
                    <div style="border-top: 2px solid #111827; padding-top: 15px; margin-top: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div style="width: 60%;">
                                <h5 style="margin: 0 0 5px 0; color: #111827; font-size: 11px; text-transform: uppercase;">Terms & Conditions:</h5>
                                <p style="margin: 0; font-size: 10px; color: #6b7280; line-height: 1.4;">1. Goods once sold will not be taken back.<br>2. Interest @ 18% p.a. will be charged if payment is delayed.</p>
                            </div>
                            <div style="width: 35%; text-align: right; background-color: #f9fafb; padding: 10px; border-radius: 6px;">
                                <span style="display: block; font-size: 11px; color: #6b7280;">Total Value:</span>
                                <strong style="font-size: 18px; color: #4f46e5; font-weight: 800;">{{ doc.base_grand_total }}</strong>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 15px; font-size: 10px; color: #9ca3af;">
                            <span>*** End of Document ***</span>
                        </div>
                    </div>
                    """
				}
			]
		})
		template.insert(ignore_permissions=True)
		print(f"Created Advanced Print Format Template: {template.print_format_name}")
