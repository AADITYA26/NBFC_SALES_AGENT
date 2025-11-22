# worker_agents/underwriting_agent.py
import json
from mock_services.mock_data_tools import get_credit_score

def calculate_mock_emi(amount: float, tenure_months: int) -> float:
    # Simple EMI calculation for mock purposes (e.g., flat rate approximation)
    # Assuming 12% annual rate for simplicity
    monthly_rate = 0.12 / 12
    emi = amount * (monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1)
    return round(emi, 2)

def evaluate_loan_eligibility(
    customer_id: str, 
    requested_amount: int, 
    tenure_months: int,
    pre_approved_limit: int, 
    salary: int, 
    salary_slip_uploaded: bool = False
) -> str:
    """
    Tool: Evaluates the loan request against NBFC policy rules.
    Handles credit check, eligibility, and requests salary slip if necessary.
    Returns a JSON string with the approval decision and reason.
    """
    credit_score = get_credit_score(customer_id)

    # Policy Rule 1: Credit Score Check
    if credit_score < 700:
        return json.dumps({
            "decision": "REJECT", 
            "reason": f"Credit score ({credit_score}) is below the minimum threshold of 700."
        })

    # Policy Rule 2: Instant Approval
    if requested_amount <= pre_approved_limit:
        emi = calculate_mock_emi(requested_amount, tenure_months)
        return json.dumps({
            "decision": "APPROVE_INSTANT", 
            "approved_amount": requested_amount,
            "emi": emi
        })

    # Policy Rule 3: Conditional Approval (Salary Check Required)
    if requested_amount <= 2 * pre_approved_limit:
        if not salary_slip_uploaded:
            return json.dumps({
                "decision": "NEEDS_SLIP_UPLOAD", 
                "reason": f"Request exceeds pre-approved limit. Please upload salary slip."
            })

        # Check Affordability
        emi = calculate_mock_emi(requested_amount, tenure_months)
        max_emi = 0.50 * salary

        if emi <= max_emi:
            return json.dumps({
                "decision": "APPROVE_CONDITIONAL", 
                "approved_amount": requested_amount,
                "emi": emi
            })
        else:
            return json.dumps({
                "decision": "REJECT", 
                "reason": f"EMI ({emi}) exceeds 50% of your salary ({salary}). Loan cannot be afforded."
            })

    # Policy Rule 4: Over Limit Rejection
    return json.dumps({
        "decision": "REJECT", 
        "reason": f"Requested amount ({requested_amount}) is more than 2x the pre-approved limit."
    })