import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions

TPF_DOCTYPES = ["TPF Client", "TPF Buyer", "TPF Product", "TPF Invoice", "TPF FBR Log"]


def _is_super(user):
    return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def _allowed_companies(user):
    perms = get_user_permissions(user) or {}
    return [p.get("doc") for p in perms.get("Company", [])]


def _condition(doctype, user=None):
    user = user or frappe.session.user
    if _is_super(user):
        return ""
    companies = _allowed_companies(user)
    if not companies:
        return "1=0"
    values = ", ".join(frappe.db.escape(c) for c in companies)
    return f"`tab{doctype}`.`company` in ({values})"


def client_conditions(user=None):  return _condition("TPF Client", user)
def buyer_conditions(user=None):   return _condition("TPF Buyer", user)
def product_conditions(user=None): return _condition("TPF Product", user)
def invoice_conditions(user=None): return _condition("TPF Invoice", user)
def log_conditions(user=None):     return _condition("TPF FBR Log", user)


def has_company_access(doc, user=None, ptype=None, **kwargs):
    user = user or frappe.session.user
    if _is_super(user):
        return True
    company = doc.get("company")
    if not company and doc.get("client"):
        company = frappe.db.get_value("TPF Client", doc.get("client"), "company")
    return bool(company) and company in _allowed_companies(user)


def assert_client_access(client_name):
    """Raise unless the current user may use this TPF Client's company."""
    if not client_name:
        return
    user = frappe.session.user
    if _is_super(user):
        return
    company = frappe.db.get_value("TPF Client", client_name, "company")
    if company not in _allowed_companies(user):
        frappe.throw(_("You are not permitted to use this client."), frappe.PermissionError)