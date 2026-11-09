import re

import frappe
from frappe import _


def validate_ntn_cnic(value, label="NTN / CNIC"):
    """FBR accepts a 7 or 9 digit NTN, or a 13 digit CNIC. Digits only."""
    if not value:
        return
    cleaned = re.sub(r"[\s-]", "", value)
    if not cleaned.isdigit() or len(cleaned) not in (7, 9, 13):
        frappe.throw(_("{0} is invalid. Use a 7 or 9 digit NTN, or a 13 digit CNIC.").format(label))