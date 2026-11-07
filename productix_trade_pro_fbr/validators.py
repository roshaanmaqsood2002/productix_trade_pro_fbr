import re
import frappe
from frappe import _


def validate_ntn_cnic(value, label="NTN / CNIC"):
    """Accept NTN (7 digits, optional -check digit) or 13-digit CNIC.
    Adjust to FBR's exact rules once confirmed."""
    if not value:
        return
    digits = re.sub(r"[\s-]", "", value)
    if not digits.isdigit() or len(digits) not in (7, 8, 13):
        frappe.throw(_("{0} is invalid. Use a 7-digit NTN (optionally with check digit) or a 13-digit CNIC.").format(label))