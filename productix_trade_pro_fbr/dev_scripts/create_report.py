import frappe

APP = "productix_trade_pro_fbr"
NAME = "TPF Sales by Client"


def run():
    if frappe.db.exists("Report", NAME):
        print(f"skip {NAME} (exists)")
        return
    module = frappe.get_module_list(APP)[0]
    frappe.get_doc({
        "doctype": "Report",
        "report_name": NAME,
        "ref_doctype": "TPF Invoice",
        "report_type": "Script Report",
        "is_standard": "Yes",
        "module": module,
        "roles": [
            {"role": "System Manager"},
            {"role": "TPF Admin"},
            {"role": "TPF Operator"},
        ],
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"created {NAME} in module {module}")