permission_query_conditions = {
    "TPF Client": "productix_trade_pro_fbr.permissions.client_conditions",
    "TPF Buyer": "productix_trade_pro_fbr.permissions.buyer_conditions",
    "TPF Product": "productix_trade_pro_fbr.permissions.product_conditions",
    "TPF Invoice": "productix_trade_pro_fbr.permissions.invoice_conditions",
    "TPF FBR Log": "productix_trade_pro_fbr.permissions.log_conditions",
}

has_permission = {
    dt: "productix_trade_pro_fbr.permissions.has_company_access"
    for dt in ["TPF Client", "TPF Buyer", "TPF Product", "TPF Invoice", "TPF FBR Log"]
}

app_name = "productix_trade_pro_fbr"
app_title = "ProductiX Trade Pro FBR"
app_publisher = "TechoHub"
app_description = "FBR digital invoicing for multi-client tenants"
app_email = "roshaanmaqsood2002@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "productix_trade_pro_fbr",
# 		"logo": "/assets/productix_trade_pro_fbr/logo.png",
# 		"title": "ProductiX Trade Pro FBR",
# 		"route": "/productix_trade_pro_fbr",
# 		"has_permission": "productix_trade_pro_fbr.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/productix_trade_pro_fbr/css/productix_trade_pro_fbr.css"
# app_include_js = "/assets/productix_trade_pro_fbr/js/productix_trade_pro_fbr.js"

# include js, css files in header of web template
# web_include_css = "/assets/productix_trade_pro_fbr/css/productix_trade_pro_fbr.css"
# web_include_js = "/assets/productix_trade_pro_fbr/js/productix_trade_pro_fbr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "productix_trade_pro_fbr/public/scss/website"

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
# app_include_icons = "productix_trade_pro_fbr/public/icons.svg"

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
# 	"methods": "productix_trade_pro_fbr.utils.jinja_methods",
# 	"filters": "productix_trade_pro_fbr.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "productix_trade_pro_fbr.install.before_install"
# after_install = "productix_trade_pro_fbr.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "productix_trade_pro_fbr.uninstall.before_uninstall"
# after_uninstall = "productix_trade_pro_fbr.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "productix_trade_pro_fbr.utils.before_app_install"
# after_app_install = "productix_trade_pro_fbr.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "productix_trade_pro_fbr.utils.before_app_uninstall"
# after_app_uninstall = "productix_trade_pro_fbr.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "productix_trade_pro_fbr.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "productix_trade_pro_fbr.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "productix_trade_pro_fbr.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["productix_trade_pro_fbr.search.awesomebar_results"]

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"productix_trade_pro_fbr.tasks.all"
# 	],
# 	"daily": [
# 		"productix_trade_pro_fbr.tasks.daily"
# 	],
# 	"hourly": [
# 		"productix_trade_pro_fbr.tasks.hourly"
# 	],
# 	"weekly": [
# 		"productix_trade_pro_fbr.tasks.weekly"
# 	],
# 	"monthly": [
# 		"productix_trade_pro_fbr.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "productix_trade_pro_fbr.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "productix_trade_pro_fbr.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "productix_trade_pro_fbr.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["productix_trade_pro_fbr.utils.before_request"]
# after_request = ["productix_trade_pro_fbr.utils.after_request"]

# Job Events
# ----------
# before_job = ["productix_trade_pro_fbr.utils.before_job"]
# after_job = ["productix_trade_pro_fbr.utils.after_job"]

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
# 	"productix_trade_pro_fbr.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

