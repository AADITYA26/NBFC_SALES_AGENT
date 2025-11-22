# main_orchestrator.py
import os
import json
from google import genai
from google.genai.errors import APIError
import json

# Import worker tools
from worker_agents.verification_agent import verify_customer_identity
from worker_agents.underwriting_agent import evaluate_loan_eligibility

# Mock sanction letter generator
def generate_sanction_letter(customer_name: str, approved_amount: int, emi: float) -> str:
    """
    Tool: Generates a mock PDF sanction letter and provides a link.
    """
    mock_link = f"https://nbfc.com/sanction/letter/{customer_name.replace(' ', '_')}_{approved_amount}.pdf"
    return f"Sanction letter for {customer_name} of ₹{approved_amount} with EMI ₹{emi} has been generated. Download here: {mock_link}"


class LoanMasterAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.chat_history = []
        self.customer_data = {}
        self.loan_request = {}
        self.conversation_stage = "START"

        self.agent_config = {
            "system_instruction": (
                "You are the Master Sales Agent for NBFC Personal Loans, a digital assistant for a large financial company. "
                "Your goal is to complete a loan sale, from conversation to sanction letter. "
                "Maintain a professional, helpful, and empathetic tone. "
                "Manage the flow: 1. Verify (phone), 2. Negotiate (amount/tenure), 3. Underwrite, 4. Sanction."
            )
        }

    def _update_history(self, role, parts):
        """Maintain chat history."""
        self.chat_history.append({"role": role, "parts": parts})

    def process_message(self, user_input: str) -> str:
        """Main loop for handling customer input."""
        self._update_history("user", [{"text": user_input}])
        import json
        # 🔹 Local handling: Simulate instant verification instead of OTP
        if self.conversation_stage == "START" and user_input.isdigit() and len(user_input) == 10:
            print(f"[LOCAL DEBUG] Simulating verification for {user_input}...")
            verification_result = json.loads(verify_customer_identity(user_input))

            if verification_result.get("status") == "success":
                self.customer_data.update(verification_result)
                self.conversation_stage = "NEEDS_ASSESSMENT"
                return (
                    f"Welcome {verification_result['name']}! You are pre-approved for ₹{verification_result['pre_approved_limit']}. "
                    "How much would you like to borrow and for how many months?"
                )
            else:
                return "Sorry, your number could not be verified. Please check and try again."


        # 🔹 Let Gemini handle normal conversation steps
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.chat_history,
                config=self.agent_config
            )
        except APIError as e:
            return f"An API error occurred: {e}"

        # 🔹 Handle model responses
        if hasattr(response, "text") and response.text:
            self._update_history("model", [{"text": response.text}])
            return response.text

        return "I’m processing your request, please wait."

    def _handle_tool_output(self, tool_name: str, result: dict):
        """Update internal state based on tool results."""
        if tool_name == "verify_customer_identity":
            if result.get("status") == "success":
                self.customer_data.update(result)
                self.conversation_stage = "NEEDS_ASSESSMENT"
                print(f"[STATE] Verified → {self.conversation_stage}")
            else:
                self.conversation_stage = "START"

        elif tool_name == "evaluate_loan_eligibility":
            decision = result.get("decision")
            if decision.startswith("APPROVE"):
                self.loan_request.update({
                    "approved_amount": result["approved_amount"],
                    "approved_emi": result["emi"]
                })
                self.conversation_stage = "SANCTION_READY"
                print(f"[STATE] Approved → {self.conversation_stage}")
            elif decision == "NEEDS_SLIP_UPLOAD":
                self.conversation_stage = "AWAITING_SLIP"
                print("[STATE] Needs salary slip.")
            elif decision == "REJECT":
                self.conversation_stage = "CLOSURE"
                print("[STATE] Loan rejected.")

        elif tool_name == "generate_sanction_letter":
            self.conversation_stage = "CLOSURE"
            print("[STATE] Sanction letter generated.")


if __name__ == "__main__":
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("ERROR: Please set the GEMINI_API_KEY environment variable.")
    else:
        agent = LoanMasterAgent(api_key=API_KEY)
        print("--- NBFC Personal Loan Chatbot ---")
        print("Master Agent: Welcome! Please share your registered 10-digit phone number to begin.")
        print("-" * 50)

        while agent.conversation_stage != "CLOSURE":
            try:
                user_input = input("Customer: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Master Agent: Thank you for chatting. Goodbye!")
                    break

                # If waiting for salary slip
                if agent.conversation_stage == "AWAITING_SLIP" and "uploaded" in user_input.lower():
                    print("[DEBUG] Simulating salary slip upload...")
                    tool_args = {
                        "customer_id": agent.customer_data["customer_id"],
                        "requested_amount": agent.loan_request["amount"],
                        "tenure_months": agent.loan_request["tenure"],
                        "pre_approved_limit": agent.customer_data["pre_approved_limit"],
                        "salary": agent.customer_data["salary"],
                        "salary_slip_uploaded": True
                    }
                    underwriting_result = evaluate_loan_eligibility(**tool_args)
                    agent._handle_tool_output("evaluate_loan_eligibility", json.loads(underwriting_result))
                    print("Master Agent: The loan decision has been updated based on your slip.")
                else:
                    response = agent.process_message(user_input)
                    print(f"Master Agent: {response}")

            except Exception as e:
                print(f"[CRITICAL ERROR]: {e}")
                break

        print("-" * 50)
