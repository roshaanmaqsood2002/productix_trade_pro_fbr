from frappe.model.document import Document
from productix_trade_pro_fbr.validators import validate_ntn_cnic


class TPFClient(Document):
    def validate(self):
        validate_ntn_cnic(self.ntn_cnic)