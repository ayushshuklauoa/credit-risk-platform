# Demo Flow: Register/Login → Create Customer → Deposit/Withdraw → Credit Score

This demo flow runs against the **direct microservice ports** (not the API gateway).

## Prerequisites
- `docker-compose up -d`
- services running:
  - Auth: `8001`
  - Customer: `8002`
  - Account: `8003`
  - Credit scoring: `8004`

## Run
```bash
python scripts/demo_flow.py
```

## What it does
1. `POST /auth/register` with a random email
2. `POST /auth/login` to obtain `access_token` and `refresh_token`
3. Creates a customer: `POST /customers`
4. Creates an account: `POST /accounts`
5. Deposits money: `POST /accounts/{account_id}/deposit`
6. Withdraws money: `POST /accounts/{account_id}/withdraw`
7. Calculates credit score: `POST /credit/calculate-score`
8. Assesses risk: `POST /credit/assess-risk`
9. Fetches summary: `GET /credit/summary/{customer_id}`

## Environment overrides
By default the script uses localhost ports:
- AUTH_BASE=http://localhost:8001
- CUSTOMER_BASE=http://localhost:8002
- ACCOUNT_BASE=http://localhost:8003
- CREDIT_BASE=http://localhost:8004

You can override:
```bash
set AUTH_BASE=http://localhost:8001
python scripts/demo_flow.py
```

## Notes
- The script assumes your services accept these endpoints as implemented in `services/*/app/routes.py`.
- If you later want the demo to run through the API gateway (including JWT middleware), switch the script URLs to `http://localhost:8000/...` and include `Authorization: Bearer <token>`.

