import frappe
from frappe.model.document import Document


class TPFProduct(Document):
    def validate(self):
        self.company = frappe.db.get_value("TPF Client", self.client, "company")