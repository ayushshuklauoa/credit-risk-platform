"""Validation flow: register user -> login -> create customer -> create account -> deposit/withdraw -> get credit score/risk/summary through API Gateway.

Runs against the API Gateway and asserts key values for a full end-to-end validation test.

USAGE:
  python scripts/demo_flow.py

ENV (optional):
  AUTH_BASE=http://localhost:8001  (Direct to Auth Service)
  GATEWAY_BASE=http://localhost:8000 (All other services)

NOTE:
- This script uses the API Gateway for all business logic endpoints.
- Auth calls (register/login) go directly to the Auth service.
- All subsequent calls are authenticated with a JWT token.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass

import httpx


AUTH_BASE = os.getenv("AUTH_BASE", "http://localhost:8001")
GATEWAY_BASE = os.getenv("GATEWAY_BASE", "http://localhost:8000")

@dataclass
class AuthResponse:
    access_token: str
    refresh_token: str
    user_id: str


def _rand_email() -> str:
    return f"demo-{uuid.uuid4().hex[:10]}@example.com"


async def register_user(client: httpx.AsyncClient, email: str) -> None:
    payload = {
        "email": email,
        "password": "testpass123",
        "first_name": "Demo",
        "last_name": "User",
    }
    r = await client.post(f"{AUTH_BASE}/auth/register", json=payload)
    r.raise_for_status()


async def login_user(client: httpx.AsyncClient, email: str) -> AuthResponse:
    payload = {"email": email, "password": "testpass123"}
    r = await client.post(f"{AUTH_BASE}/auth/login", json=payload)
    r.raise_for_status()
    data = r.json()
    return AuthResponse(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        user_id=data["user_id"],
    )


async def create_customer(client: httpx.AsyncClient, user_id: str, headers: dict) -> dict:
    payload = {
        "user_id": user_id,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
    }
    r = await client.post(f"{GATEWAY_BASE}/customers", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


async def create_account(client: httpx.AsyncClient, customer_id: str, headers: dict) -> dict:
    payload = {
        "customer_id": customer_id,
        "account_type": "checking",
        "initial_balance": 1000.0,
    }
    r = await client.post(f"{GATEWAY_BASE}/accounts", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


async def deposit(client: httpx.AsyncClient, account_id: str, amount: float, headers: dict) -> dict:
    payload = {"amount": amount, "description": "Demo deposit"}
    r = await client.post(f"{GATEWAY_BASE}/accounts/{account_id}/deposit", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


async def withdraw(client: httpx.AsyncClient, account_id: str, amount: float, headers: dict) -> dict:
    payload = {"amount": amount, "description": "Demo withdrawal"}
    r = await client.post(f"{GATEWAY_BASE}/accounts/{account_id}/withdraw", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


async def get_account_balance(client: httpx.AsyncClient, account_id: str, headers: dict) -> dict:
    """Fetches the current balance for a given account."""
    r = await client.get(f"{GATEWAY_BASE}/accounts/{account_id}/balance", headers=headers)
    r.raise_for_status()
    return r.json()


async def calculate_credit(client: httpx.AsyncClient, customer_id: str, headers: dict) -> dict:
    payload = {"customer_id": customer_id, "include_historical": True}
    r = await client.post(f"{GATEWAY_BASE}/credit/calculate-score", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


async def assess_risk(client: httpx.AsyncClient, customer_id: str, headers: dict) -> dict:
    payload = {"customer_id": customer_id, "assessment_method": "automated"}
    r = await client.post(f"{GATEWAY_BASE}/credit/assess-risk", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


async def credit_summary(client: httpx.AsyncClient, customer_id: str, headers: dict) -> dict:
    r = await client.get(f"{GATEWAY_BASE}/credit/summary/{customer_id}", headers=headers)
    r.raise_for_status()
    return r.json()


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        email = _rand_email()

        print("1) Register user...")
        try:
            await register_user(client, email)
            print(f"   - User {email} registered successfully.")
        except httpx.HTTPStatusError as e:
            # If user exists (409 Conflict), continue with login
            if e.response.status_code == 409:
                print(f"   - User {email} already exists, continuing with login.")
            else:
                raise

        print("2) Login...")
        auth_response = await login_user(client, email)
        user_id = auth_response.user_id
        headers = {"Authorization": f"Bearer {auth_response.access_token}"}
        print(f"   - Login successful. Token acquired.")
        print(f"3) Resolved user_id: {user_id}")

        print("4) Create customer...")
        customer = await create_customer(client, user_id=user_id, headers=headers)
        customer_id = customer["id"]
        print(f"   - customer_id: {customer_id}")

        print("5) Create account...")
        account = await create_account(client, customer_id=customer_id, headers=headers)
        account_id = account["id"]
        print(f"   - account_id: {account_id}")


        print("6) Deposit...")
        dep = await deposit(client, account_id=account_id, amount=250.0, headers=headers)
        initial_balance = 1000.0
        expected_balance_after_deposit = initial_balance + 250.0
        print(f"   - deposit txn id: {dep['id']}")
        balance_after_deposit = await get_account_balance(client, account_id, headers=headers)
        actual_balance_after_deposit = balance_after_deposit['current_balance']
        print(f"   - Balance after deposit: {actual_balance_after_deposit} (Expected: {expected_balance_after_deposit})")
        assert actual_balance_after_deposit == expected_balance_after_deposit, \
            f"Balance after deposit is incorrect! Expected {expected_balance_after_deposit}, got {actual_balance_after_deposit}"

        print("7) Withdraw...")
        wd = await withdraw(client, account_id=account_id, amount=100.0, headers=headers)
        expected_balance_after_withdrawal = expected_balance_after_deposit - 100.0
        print(f"   - withdrawal txn id: {wd['id']}")
        balance_after_withdrawal = await get_account_balance(client, account_id, headers=headers)
        actual_final_balance = balance_after_withdrawal['current_balance']
        print(f"   - Final balance: {actual_final_balance} (Expected: {expected_balance_after_withdrawal})")
        assert actual_final_balance == expected_balance_after_withdrawal, \
            f"Final balance is incorrect! Expected {expected_balance_after_withdrawal}, got {actual_final_balance}"

        print("8) Calculate credit score...")
        score = await calculate_credit(client, customer_id=customer_id, headers=headers)
        print(f"   - internal_score: {score['internal_score']}")

        print("9) Assess risk...")
        risk = await assess_risk(client, customer_id=customer_id, headers=headers)
        print(f"   - overall_risk_level: {risk['overall_risk_level']}")

        print("10) Get credit summary...")
        summary = await credit_summary(client, customer_id=customer_id, headers=headers)
        print(f"   - summary.risk_score: {summary['risk_score']}")

        print("\n✅ Demo flow complete.")
        print("\n--- SUMMARY SNAPSHOT ---")
        print({
            "email": email,
            "user_id": user_id,
            "customer_id": customer_id,
            "account_id": account_id,
            "deposit_transaction_id": dep.get("id"),
            "withdraw_transaction_id": wd.get("id"),
            "final_balance": actual_final_balance,
            "internal_score": score.get("internal_score"),
            "risk_level": risk.get("overall_risk_level"),
        })


if __name__ == "__main__":
    asyncio.run(main())
