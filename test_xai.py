import httpx
import asyncio
import uuid
import os
import sys
import textwrap
import logging


# --- Configuration and Setup ---
BASE_URL = "http://localhost:8000"
AUTH_URL = "http://localhost:8001"

# Enable terminal colors on Windows if in a TTY
if sys.platform == "win32" and sys.stdout.isatty():
    os.system("color")

# Color constants
IS_TTY = sys.stdout.isatty()
CYAN = "\033[96m" if IS_TTY else ""
GREEN = "\033[92m" if IS_TTY else ""
YELLOW = "\033[93m" if IS_TTY else ""
RED = "\033[91m" if IS_TTY else ""
GRAY = "\033[90m" if IS_TTY else ""
RESET = "\033[0m" if IS_TTY else ""

def print_error(message, details=None):
    """Prints a formatted error message."""
    print(f"\n{RED}❌ ERROR: {message}{RESET}")
    if details:
        print(f"{GRAY}{details}{RESET}")

def get_numeric_input(prompt, type_func):
    """Helper to get and validate numeric input from the user."""
    while True:
        try:
            value = input(prompt)
            return type_func(value)
        except (ValueError, TypeError):
            print(f"{RED}Invalid input. Please enter a valid number.{RESET}")

def print_professional_report(user, financials, analysis):
    """Prints a professional, formatted report to the console."""
    risk_level = analysis.get('overall_risk_level', 'N/A').upper()
    risk_color = RED if risk_level in ["HIGH", "VERY_HIGH"] else (YELLOW if risk_level == "MEDIUM" else GREEN)

    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    income_str = f"${financials.get('income', 0):,.2f}"
    debt_str = f"${financials.get('debt', 0):,.2f}"
    prob_str = f"{analysis.get('default_probability', 0):.2%}"
    dti_str = f"{analysis.get('debt_to_income_ratio', 0):.2%}"

    wrapper = textwrap.TextWrapper(width=63)
    recommendations = wrapper.wrap(analysis.get('recommended_actions', 'N/A'))

    print(f"\n┌{'─'*67}┐")
    print(f"│ {CYAN}{'AI-POWERED CREDIT RISK ASSESSMENT REPORT':^65}{RESET} │")
    print(f"├{'─'*67}┤")

    print(f"│ {YELLOW}{'CUSTOMER DETAILS':<65}{RESET} │")
    print(f"│   - Name:         {full_name:<47} │")
    print(f"│   - Email:        {user.get('email', ''):<47} │")
    print(f"│   - Customer ID:  {str(user.get('customer_id', '')):<47} │")

    print(f"├{'─'*67}┤")
    print(f"│ {YELLOW}{'FINANCIAL PROFILE':<65}{RESET} │")
    print(f"│   - Annual Income:      {income_str:<42} │")
    print(f"│   - Total Debt:         {debt_str:<42} │")
    print(f"│   - Credit Score:       {financials.get('credit_score', 0):<42} │")

    print(f"├{'─'*67}┤")
    print(f"│ {YELLOW}{'AI ANALYSIS':<65}{RESET} │")
    print(f"│   - Overall Risk:       {risk_color}{risk_level:<42}{RESET} │")
    print(f"│   - Default Probability:{risk_color}{prob_str:<42}{RESET} │")
    print(f"│   - Debt-to-Income:     {risk_color}{dti_str:<42}{RESET} │")

    print(f"├{'─'*67}┤")
    print(f"│ {YELLOW}{'XAI INSIGHT & RECOMMENDATION':<65}{RESET} │")
    for line in recommendations:
        print(f"│   {risk_color}{line:<63}{RESET} │")

    print(f"├{'─'*67}┤")
    model_version = analysis.get('model_version', 'N/A')
    print(f"│ {GRAY}Model Version: {model_version:<50}{RESET} │")
    print(f"└{'─'*67}┘")

async def run_xai_test():
    """Runs a full end-to-end test of the XAI credit assessment workflow."""
    print(f"\n{CYAN}{'='*60}")
    print("   🤖 CRIP EXPLAINABLE AI (XAI) - PYTHON TEST SUITE")
    print(f"{'='*60}{RESET}\n")

    # --- Interactive User Input ---
    print(f"{YELLOW}--- Phase 1: User & Financial Profile Setup ---{RESET}")
    email = input(f"  Enter email (or press Enter for a random one): ")
    if not email:
        email = f"ai_python_{uuid.uuid4().hex[:8]}@example.com"
        print(f"    {GRAY}Using random email: {email}{RESET}")
    
    password = input("  Enter password (e.g., SecurePass2026!): ")
    first_name = input("  Enter first name (e.g., AI): ")
    last_name = input("  Enter last name (e.g., Tester): ")
    
    print(f"\n{GRAY}  Please provide the financial details for the assessment:{RESET}")
    annual_income = get_numeric_input("  ▶ Enter Annual Income (e.g., 1200000): ", float)
    total_debt = get_numeric_input("  ▶ Enter Total Outstanding Debt (e.g., 50000): ", float)
    credit_score = get_numeric_input("  ▶ Enter Credit Score (300-850): ", int)

    print(f"\n{GREEN}--- Profile complete. Initiating secure workflow... ---{RESET}\n")

    user_data = {'email': email, 'first_name': first_name, 'last_name': last_name}
    financial_data = {'income': annual_income, 'debt': total_debt, 'credit_score': credit_score}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            # --- 1. SETUP PHASE ---
            print(f"{YELLOW}[WORKFLOW] 1/4: Registering user profile...{RESET}")

            # Register
            reg_res = await client.post(f"{AUTH_URL}/auth/register", json={
                "email": email, "password": password, "first_name": first_name, "last_name": last_name
            })
            reg_res.raise_for_status()
            reg_data = reg_res.json()
            user_id = reg_data.get("id") or reg_data.get("user_id")
            if not user_id: raise ValueError("User ID not found in registration response.")
            user_data['user_id'] = user_id
            print(f"{GREEN}[SUCCESS] User registered with ID: {user_id}{RESET}\n")

            print(f"{YELLOW}[WORKFLOW] 2/4: Authenticating and generating token...{RESET}")
            login_res = await client.post(f"{AUTH_URL}/auth/login", json={
                "email": email, "password": password
            })
            login_res.raise_for_status()
            login_data = login_res.json()
            token = login_data.get("access_token")
            if not token: raise ValueError("Access Token not found in login response.")
            headers = {"Authorization": f"Bearer {token}"}
            print(f"{GREEN}[SUCCESS] Authentication complete.{RESET}\n")

            print(f"{YELLOW}[WORKFLOW] 3/4: Creating customer record...{RESET}")
            cust_res = await client.post(f"{BASE_URL}/customers", json={
                "user_id": user_id, "first_name": first_name, "last_name": last_name,
                "email": email, "phone": "1234567890"
            }, headers=headers)
            cust_res.raise_for_status()
            customer_id = cust_res.json().get("id")
            if not customer_id: raise ValueError("Customer ID not found in customer creation response.")
            user_data['customer_id'] = customer_id
            print(f"{GREEN}[SUCCESS] Customer record created: {customer_id}{RESET}\n")

            # --- 2. AI EVALUATION ---
            print(f"{YELLOW}[WORKFLOW] 4/4: Running real-time machine learning evaluation...{RESET}")

            # Call the assessment endpoint with user-provided data
            assessment_res = await client.post(f"{BASE_URL}/credit/assess-risk", json={
                "customer_id": customer_id,
                "credit_score": credit_score,
                "income": annual_income,
                "debt": total_debt
            }, headers=headers)
            assessment_res.raise_for_status()
            data = assessment_res.json()

            print(f"{GREEN}[SUCCESS] AI analysis complete.{RESET}")

            print_professional_report(user_data, financial_data, data)
            print(f"\n{GREEN}✅ Simulation Completed Successfully.{RESET}\n")

        except httpx.HTTPStatusError as e:
            print_error(f"A service returned an error (Status: {e.response.status_code})", f"URL: {e.request.url}\nResponse: {e.response.text}")
        except httpx.RequestError as e:
            print_error("Could not connect to a service.", f"Please ensure all services are running via 'docker-compose up'.\nURL: {e.request.url}")
        except (KeyError, ValueError, TypeError) as e:
            print_error("Received unexpected data from the API.", f"Error: {e}")
        except Exception as e:
            print_error("An unexpected error occurred.", str(e))

if __name__ == "__main__":
    # Silence httpx internal logs to keep the dashboard clean
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    asyncio.run(run_xai_test())