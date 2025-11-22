# worker_agents/verification_agent.py
from mock_services.mock_data_tools import get_customer_data
import json
def verify_customer_identity(phone_number: str) -> str:
    """
    Tool: Verifies customer identity and fetches pre-approved limit from CRM.
    The Master Agent MUST call this first to qualify the customer.
    Returns a JSON string of the verification result.
    """
    result = get_customer_data(phone_number)
    return json.dumps(result)