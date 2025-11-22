# mock_services/mock_data_tools.py
import json
import os
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'customer_data.json')

import os
import json

def get_customer_data(phone_number: str) -> dict:
    """
    Looks up customer details and pre-approved limit from the mock CRM.
    If the phone number isn't found, returns a default mock verified customer.
    """

    # ✅ Always resolve path from project root
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_PATH = os.path.join(BASE_DIR, "customer_data.json")

    try:
        with open(DATA_PATH, "r") as f:
            customers = json.load(f)
    except FileNotFoundError:
        return {"error": f"Customer data file not found at {DATA_PATH}"}

    # ✅ Match phone number exactly as stored in JSON
    customer = next((c for c in customers if str(c["phone"]) == str(phone_number)), None)

    if customer:
        # Found → return their stored info
        return {
            "status": "success",
            "customer_id": customer["customer_id"],
            "name": customer["name"],
            "pre_approved_limit": customer["pre_approved_limit"],
            "salary": customer["salary"],
        }

    # Not found → fallback user
    return {
        "status": "success",
        "customer_id": "CUST999",
        "name": "Test User",
        "phone": phone_number,
        "pre_approved_limit": 150000,
        "salary": 50000,
    }



def get_credit_score(customer_id: str) -> int:
    """Fetches the credit score from the mock Credit Bureau API."""
    try:
        with open(DATA_PATH, 'r') as f:
            customers = json.load(f)
    except:
         return 0 # Default low score on error

    # Simulate Credit Bureau API call
    customer = next((c for c in customers if c['customer_id'] == customer_id), None)

    return customer['credit_score'] if customer else 0

def get_standard_loan_rates() -> dict:
    """Fetches standard interest rates from the mock Offer Mart Server."""
    return {
        "rate_base": 0.12, # 12%
        "rate_premium": 0.10, # 10%
        "rate_high_risk": 0.15 # 15%
    }