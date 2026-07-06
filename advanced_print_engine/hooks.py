app_name = "advanced_print_engine"
app_title = "Advanced Print Engine"
app_publisher = "Developer"
app_description = "Advanced PDF print rendering engine using Playwright"
app_email = "dev@example.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "advanced_print_engine",
# 		"logo": "/assets/advanced_print_engine/logo.png",
# 		"title": "Advanced Print Engine",
# 		"route": "/advanced_print_engine",
# 		"has_permission": "advanced_print_engine.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/advanced_print_engine/css/advanced_print_engine.css"
app_include_js = "advanced_print_engine.bundle.js"

# include js, css files in header of web template
# web_include_css = "/assets/advanced_print_engine/css/advanced_print_engine.css"
# web_include_js = "/assets/advanced_print_engine/js/advanced_print_engine.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "advanced_print_engine/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "advanced_print_engine/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "advanced_print_engine.utils.jinja_methods",
# 	"filters": "advanced_print_engine.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "advanced_print_engine.install.before_install"
# after_install = "advanced_print_engine.install.after_install"
after_migrate = "advanced_print_engine.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "advanced_print_engine.uninstall.before_uninstall"
# after_uninstall = "advanced_print_engine.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "advanced_print_engine.utils.before_app_install"
# after_app_install = "advanced_print_engine.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "advanced_print_engine.utils.before_app_uninstall"
# after_app_uninstall = "advanced_print_engine.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "advanced_print_engine.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Print Format": {
		"on_trash": "advanced_print_engine.api.print_format.on_print_format_trash",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"advanced_print_engine.tasks.all"
# 	],
# 	"daily": [
# 		"advanced_print_engine.tasks.daily"
# 	],
# 	"hourly": [
# 		"advanced_print_engine.tasks.hourly"
# 	],
# 	"weekly": [
# 		"advanced_print_engine.tasks.weekly"
# 	],
# 	"monthly": [
# 		"advanced_print_engine.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "advanced_print_engine.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "advanced_print_engine.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "advanced_print_engine.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["advanced_print_engine.utils.before_request"]
# after_request = ["advanced_print_engine.utils.after_request"]

# Job Events
# ----------
# before_job = ["advanced_print_engine.utils.before_job"]
# after_job = ["advanced_print_engine.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"advanced_print_engine.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

