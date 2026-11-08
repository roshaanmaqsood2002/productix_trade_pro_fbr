import frappe

ROLES = ["TPF Admin", "TPF Operator"]


def before_install():
    for r in ROLES:
        if not frappe.db.exists("Role", r):
            frappe.get_doc({"doctype": "Role", "role_name": r,
                            "desk_access": 1}).insert(ignore_permissions=True)
    frappe.db.commit()