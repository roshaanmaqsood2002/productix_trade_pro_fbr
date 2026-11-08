import frappe

APP = "productix_trade_pro_fbr"


def run():
    if frappe.db.exists("Page", "tpf-dashboard"):
        print("skip page (exists)")
        return
    frappe.get_doc({
        "doctype": "Page", "page_name": "tpf-dashboard", "title": "Trade Pro FBR Dashboard",
        "module": frappe.get_module_list(APP)[0], "standard": "Yes", "icon": "chart",
        "roles": [{"role": "System Manager"}, {"role": "TPF Admin"}, {"role": "TPF Operator"}],
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("created page")