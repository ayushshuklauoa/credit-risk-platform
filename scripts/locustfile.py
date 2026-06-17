"""
Locust Performance Test for CRIP Enterprise Platform

This script simulates user behavior to load test the API Gateway and underlying services.
It covers a realistic workflow: registration, login, customer/account creation,
and then a mix of read-heavy (balance check) and write-heavy (transactions, risk assessment) tasks.

INSTALLATION:
  pip install locust

HOW TO RUN:
1. Make sure your CRIP platform is running: `docker-compose up -d`
2. Run Locust from the project root directory:
   locust -f scripts/locustfile.py

3. Open your browser to http://localhost:8089 and start a new test.
   - Number of users: Start with 100
   - Spawn rate: 10 (users per second)

This will give you real-time metrics on response times, requests per second (RPS), and failures.
"""

import uuid
import random
from locust import HttpUser, task, between

# Locust web UI will show ports/RPS; if `host` is wrong/empty it can break metrics.
# Ensure we always have a valid gateway host.
DEFAULT_GATEWAY_HOST = "http://localhost:8000"

class CripUser(HttpUser):
    # Set a realistic think time between tasks for a user
    wait_time = between(0.8, 1.2)
    # Set a longer network timeout to accommodate potentially slow setup tasks
    # like registration and login, preventing premature test failures.
    network_timeout = 30.0
    host = DEFAULT_GATEWAY_HOST

    def on_start(self):
        """
        Called when a Locust user starts. This function simulates the initial setup for a user.
        If any critical setup step fails, the user stops to avoid polluting test results.
        """
        self.email = f"locust-{uuid.uuid4().hex[:10]}@crip.io"
        self.password = "locustPass123!"
        self.first_name = f"User{random.randint(1000, 9999)}"
        self.last_name = f"Test{random.randint(1000, 9999)}"
        self.auth_headers = {}
        self.customer_id = None
        self.account_id = None
        user_id = None

        # 1. Register user. A 409 Conflict (user exists) is okay; login is the real check.
        # Auth calls go directly to the auth service, not through the gateway.
        with self.client.post(
            "http://localhost:8001/auth/register",
            json={"email": self.email, "password": self.password, "first_name": self.first_name, "last_name": self.last_name},
            name="/auth/register [setup]",
            catch_response=True,
        ) as response:
            if not response.ok and response.status_code != 409:
                response.failure(f"Registration failed: {response.status_code} {response.text}")
                self.stop()
                return
            else:
                response.success()

        # 2. Login to get token. This is a critical step.
        # Use a lenient-but-real check to reduce failures from transient 5xx.
        with self.client.post(
            "http://localhost:8001/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login [setup]",
            catch_response=True,
        ) as response:
            if not response.ok:
                response.failure(f"Could not log in user {self.email}. Status: {response.status_code}, Response: {response.text}")
                self.stop()  # Stop this virtual user if login fails
                return
            try:
                data = response.json()
                self.auth_headers = {"Authorization": f"Bearer {data['access_token']}"}
                user_id = data["user_id"]
            except Exception as e:
                response.failure(f"Failed to parse login response. Error: {e}, Response: {response.text}")
                self.stop()
                return

        # 3. Create a Customer record. Also critical.
        with self.client.post(
            "/customers",  # This will be prefixed with the host (http://localhost:8000)
            headers=self.auth_headers,
            json={"user_id": user_id, "first_name": self.first_name, "last_name": self.last_name, "email": self.email},
            name="/customers [setup]",
            catch_response=True,
        ) as response:
            if not response.ok:
                response.failure(f"Could not create customer for user {user_id}. Status: {response.status_code}, Response: {response.text}")
                self.stop()
                return
            try:
                self.customer_id = response.json().get("id")
            except Exception as e:
                response.failure(f"Failed to parse customer creation response. Error: {e}, Response: {response.text}")
                self.stop()
                return

        # 4. Create an Account for the customer. Also critical.
        with self.client.post(
            "/accounts",
            headers=self.auth_headers,
            json={"customer_id": self.customer_id, "account_type": "checking", "initial_balance": 5000},
            name="/accounts [setup]",
            catch_response=True,
        ) as response:
            if not response.ok:
                response.failure(f"Could not create account for customer {self.customer_id}. Status: {response.status_code}, Response: {response.text}")
                self.stop()
                return
            try:
                self.account_id = response.json().get("id")
            except Exception as e:
                response.failure(f"Failed to parse account creation response. Error: {e}, Response: {response.text}")
                self.stop()
                return

    @task(10)
    def get_account_balance(self):
        """High-frequency task: Check account balance (read-only)."""
        if self.account_id:
            self.client.get(
                f"/accounts/{self.account_id}/balance",
                headers=self.auth_headers,
                name="/accounts/[id]/balance",
            )

    @task(5)
    def get_customer_details(self):
        """Medium-frequency task: Check customer details (read-only)."""
        if self.customer_id:
            self.client.get(
                f"/customers/{self.customer_id}",
                headers=self.auth_headers,
                name="/customers/[id]",
            )

    @task(3)
    def make_deposit(self):
        """Medium-frequency task: Make a deposit (write operation)."""
        if self.account_id:
            self.client.post(
                f"/accounts/{self.account_id}/deposit",
                headers=self.auth_headers,
                json={"amount": 100.0, "description": "Locust deposit"},
                name="/accounts/[id]/deposit",
            )

    @task(2)
    def make_withdrawal(self):
        """Medium-frequency task: Make a withdrawal (write operation)."""
        if self.account_id:
            self.client.post(
                f"/accounts/{self.account_id}/withdraw",
                headers=self.auth_headers,
                json={"amount": 50.0, "description": "Locust withdrawal"},
                name="/accounts/[id]/withdraw",
            )

    @task(1)
    def assess_risk(self):
        """Low-frequency task: Run a credit risk assessment (complex operation)."""
        if self.customer_id:
            self.client.post(
                "/credit/assess-risk",
                headers=self.auth_headers,
                json={"customer_id": self.customer_id, "assessment_method": "automated"},
                name="/credit/assess-risk",
            )