import frappe
from frappe import _
from frappe.model.document import Document
from productix_trade_pro_fbr.validators import validate_ntn_cnic


class TPFBuyer(Document):
    def validate(self):
        if self.registration_type == "Registered" and not self.ntn_cnic:
            frappe.throw(_("NTN / CNIC is required for registered buyers."))
        validate_ntn_cnic(self.ntn_cnic)
        self.company = frappe.db.get_value("TPF Client", self.client, "company")