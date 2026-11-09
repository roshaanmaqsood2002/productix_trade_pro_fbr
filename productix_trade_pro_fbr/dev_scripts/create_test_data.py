import frappe
from frappe.utils import nowdate

TENANT_A = "Trade Pro FBR"
TENANT_B = "Test Tenant B"
PASSWORD = "Tpf#Test-7391-Qx"

USERS = {
    "opa@test.com": ("TPF Operator", TENANT_A),
    "opb@test.com": ("TPF Operator", TENANT_B),
    "adma@test.com": ("TPF Admin", TENANT_A),
    "nop@test.com": ("TPF Operator", None),   # no company permission at all
}


def ensure_company(name, abbr):
    if not frappe.db.exists("Company", name):
        frappe.get_doc({"doctype": "Company", "company_name": name, "abbr": abbr,
                        "default_currency": "PKR", "country": "Pakistan"}).insert(ignore_permissions=True)


def ensure_user(email, role, company):
    if not frappe.db.exists("User", email):
        frappe.get_doc({"doctype": "User", "email": email, "first_name": email.split("@")[0],
                        "enabled": 1, "user_type": "System User", "send_welcome_email": 0,
                        "new_password": PASSWORD, "roles": [{"role": role}]}).insert(ignore_permissions=True)
    if company and not frappe.db.exists("User Permission", {"user": email, "allow": "Company", "for_value": company}):
        frappe.get_doc({"doctype": "User Permission", "user": email, "allow": "Company",
                        "for_value": company}).insert(ignore_permissions=True)


def ensure(doctype, filters, doc):
    name = frappe.db.get_value(doctype, filters)
    return name or frappe.get_doc(doc).insert(ignore_permissions=True).name


def seed(company, label, ntn):
    client = ensure("TPF Client", {"company": company, "client_name": f"{label} Client"},
                    {"doctype": "TPF Client", "company": company, "client_name": f"{label} Client",
                     "ntn_cnic": ntn, "registration_type": "Registered", "province": "Punjab", "is_active": 1})
    buyer = ensure("TPF Buyer", {"client": client, "buyer_name": f"{label} Buyer"},
                   {"doctype": "TPF Buyer", "client": client, "buyer_name": f"{label} Buyer",
                    "ntn_cnic": "3333333", "registration_type": "Registered", "province": "Punjab"})
    product = ensure("TPF Product", {"client": client, "product_name": f"{label} Item"},
                     {"doctype": "TPF Product", "client": client, "product_name": f"{label} Item",
                      "hs_code": "1234.5678", "uom": "Pcs", "default_tax_rate": 18})
    ensure("TPF Invoice", {"client": client},
           {"doctype": "TPF Invoice", "client": client, "buyer": buyer, "invoice_date": nowdate(),
            "items": [{"product": product, "description": f"{label} Item", "hs_code": "1234.5678",
                       "uom": "Pcs", "quantity": 2, "rate": 500, "tax_rate": 18}]})


def run():
    frappe.set_user("Administrator")
    ensure_company(TENANT_B, "TTB")
    for email, (role, company) in USERS.items():
        ensure_user(email, role, company)
    seed(TENANT_A, "Tenant A", "1111111")
    seed(TENANT_B, "Tenant B", "2222222")
    frappe.db.commit()
    print("test data ready")