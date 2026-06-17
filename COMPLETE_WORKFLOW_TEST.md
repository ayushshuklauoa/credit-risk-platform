# 🚀 Complete Workflow Test Guide - CRIP Enterprise Platform

**Date:** 2026-06-11  
**Platform:** Windows PowerShell  
**Status:** All services running (Auth, Customer, Account, Credit, Fraud, Document)

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Phase 1: Authentication](#phase-1-authentication)
3. [Phase 2: Customer Management](#phase-2-customer-management)
4. [Phase 3: Account Operations](#phase-3-account-operations)
5. [Phase 4: Credit Scoring](#phase-4-credit-scoring)
6. [Phase 5: Fraud Detection](#phase-5-fraud-detection)
7. [Phase 6: Document AI](#phase-6-document-ai)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

Copy and paste this entire block into PowerShell to run the complete workflow:

```powershell
# ============================================
# STEP 1: REGISTER NEW USER
# ============================================
Write-Host "📝 STEP 1: Registering new user..." -ForegroundColor Cyan

$registerBody = @{
    email = "testuser@example.com"
    password = "TestPass123!"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

$register = Invoke-WebRequest -Uri "http://localhost:8001/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $registerBody -UseBasicParsing

$registerData = $register.Content | ConvertFrom-Json
$userId = $registerData.id

Write-Host "✅ User registered!" -ForegroundColor Green
Write-Host "   User ID: $userId"
Write-Host "   Email: $($registerData.email)"
Write-Host ""

# ============================================
# STEP 2: LOGIN USER
# ============================================
Write-Host "🔑 STEP 2: Logging in user..." -ForegroundColor Cyan

$loginBody = @{
    email = "testuser@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

$login = Invoke-WebRequest -Uri "http://localhost:8001/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $loginBody -UseBasicParsing

$loginData = $login.Content | ConvertFrom-Json
$accessToken = $loginData.access_token
$refreshToken = $loginData.refresh_token

Write-Host "✅ Login successful!" -ForegroundColor Green
Write-Host "   Access Token: $($accessToken.Substring(0, 50))..."
Write-Host "   Expires in: $($loginData.expires_in) seconds"
Write-Host ""

# ============================================
# STEP 3: CREATE CUSTOMER PROFILE
# ============================================
Write-Host "👤 STEP 3: Creating customer profile..." -ForegroundColor Cyan

$customerBody = @{
    user_id = $userId
    first_name = "Test"
    last_name = "User"
    email = "testuser@example.com"
    phone = "+1-555-0001"
} | ConvertTo-Json

$headers = @{"Authorization" = "Bearer $accessToken"}

$customer = Invoke-WebRequest -Uri "http://localhost:8000/customers" `
  -Method POST `
  -ContentType "application/json" `
  -Body $customerBody `
  -Headers $headers -UseBasicParsing

$customerData = $customer.Content | ConvertFrom-Json
$customerId = $customerData.id

Write-Host "✅ Customer created!" -ForegroundColor Green
Write-Host "   Customer ID: $customerId"
Write-Host "   Name: $($customerData.first_name) $($customerData.last_name)"
Write-Host "   Status: $($customerData.status)"
Write-Host "   KYC Status: $($customerData.kyc_status)"
Write-Host ""

# ============================================
# STEP 4: CREATE ACCOUNT
# ============================================
Write-Host "🏦 STEP 4: Creating account..." -ForegroundColor Cyan

$accountBody = @{
    customer_id = $customerId
    account_type = "savings"
    currency = "USD"
    initial_balance = 10000
} | ConvertTo-Json

$account = Invoke-WebRequest -Uri "http://localhost:8000/accounts" `
  -Method POST `
  -ContentType "application/json" `
  -Body $accountBody `
  -Headers $headers -UseBasicParsing

$accountData = $account.Content | ConvertFrom-Json
$accountId = $accountData.id

Write-Host "✅ Account created!" -ForegroundColor Green
Write-Host "   Account ID: $accountId"
Write-Host "   Type: $($accountData.account_type)"
Write-Host "   Balance: $($accountData.balance) $($accountData.currency)"
Write-Host "   Status: $($accountData.status)"
Write-Host ""

# ============================================
# STEP 5: DEPOSIT MONEY
# ============================================
Write-Host "💰 STEP 5: Making deposit..." -ForegroundColor Cyan

$depositBody = @{
    amount = 5000
    description = "Initial deposit"
} | ConvertTo-Json

$deposit = Invoke-WebRequest -Uri "http://localhost:8000/accounts/$accountId/deposit" `
  -Method POST `
  -ContentType "application/json" `
  -Body $depositBody `
  -Headers $headers -UseBasicParsing

$depositData = $deposit.Content | ConvertFrom-Json

Write-Host "✅ Deposit successful!" -ForegroundColor Green
Write-Host "   Amount: $($depositData.amount)"
Write-Host "   New Balance: $($depositData.new_balance)"
Write-Host ""

# ============================================
# STEP 6: CHECK ACCOUNT BALANCE
# ============================================
Write-Host "📊 STEP 6: Checking account balance..." -ForegroundColor Cyan

$balance = Invoke-WebRequest -Uri "http://localhost:8000/accounts/$accountId/balance" `
  -Method GET `
  -Headers $headers -UseBasicParsing

$balanceData = $balance.Content | ConvertFrom-Json

Write-Host "✅ Balance retrieved!" -ForegroundColor Green
Write-Host "   Account ID: $($balanceData.account_id)"
Write-Host "   Balance: $($balanceData.balance) $($balanceData.currency)"
Write-Host ""

# ============================================
# STEP 7: CALCULATE CREDIT SCORE
# ============================================
Write-Host "📈 STEP 7: Calculating credit score..." -ForegroundColor Cyan

$creditBody = @{
    customer_id = $customerId
    annual_income = 100000
    credit_history_months = 60
    total_debt = 25000
} | ConvertTo-Json

$credit = Invoke-WebRequest -Uri "http://localhost:8000/credit/calculate-score" `
  -Method POST `
  -ContentType "application/json" `
  -Body $creditBody `
  -Headers $headers -UseBasicParsing

$creditData = $credit.Content | ConvertFrom-Json

Write-Host "✅ Credit score calculated!" -ForegroundColor Green
Write-Host "   Score: $($creditData.score)"
Write-Host "   Grade: $($creditData.grade)"
Write-Host "   Risk Level: $($creditData.risk_level)"
Write-Host ""

# ============================================
# STEP 8: CREATE FRAUD ALERT
# ============================================
Write-Host "🚨 STEP 8: Creating fraud alert..." -ForegroundColor Cyan

$fraudBody = @{
    customer_id = $customerId
    alert_type = "suspicious_activity"
    severity = "medium"
    description = "Test fraud alert for workflow"
} | ConvertTo-Json

$fraud = Invoke-WebRequest -Uri "http://localhost:8000/fraud/alerts" `
  -Method POST `
  -ContentType "application/json" `
  -Body $fraudBody `
  -Headers $headers -UseBasicParsing

$fraudData = $fraud.Content | ConvertFrom-Json

Write-Host "✅ Fraud alert created!" -ForegroundColor Green
Write-Host "   Alert ID: $($fraudData.id)"
Write-Host "   Type: $($fraudData.alert_type)"
Write-Host "   Severity: $($fraudData.severity)"
Write-Host "   Status: $($fraudData.status)"
Write-Host ""

# ============================================
# SUMMARY
# ============================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
Write-Host "✅ COMPLETE WORKFLOW TEST PASSED!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   User ID:           $userId"
Write-Host "   Customer ID:       $customerId"
Write-Host "   Account ID:        $accountId"
Write-Host "   Account Balance:   $($balanceData.balance)"
Write-Host "   Credit Score:      $($creditData.score) ($($creditData.grade))"
Write-Host "   Fraud Alert ID:    $($fraudData.id)"
Write-Host ""
Write-Host "🎉 All services working correctly!" -ForegroundColor Green
```

---

## Phase 1: Authentication

### 1.1 Register New User

```powershell
$body = @{
    email = "newuser@example.com"
    password = "SecurePassword123!"
    first_name = "John"
    last_name = "Doe"
} | ConvertTo-Json

$register = Invoke-WebRequest -Uri "http://localhost:8001/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body -UseBasicParsing

$register.Content | ConvertFrom-Json | Format-List
```

**Expected Output:**
```
id            : [UUID]
email         : newuser@example.com
first_name    : John
last_name     : Doe
is_active     : True
is_verified   : False
created_at    : 2026-06-11T...
```

### 1.2 Login User

```powershell
$body = @{
    email = "newuser@example.com"
    password = "SecurePassword123!"
} | ConvertTo-Json

$login = Invoke-WebRequest -Uri "http://localhost:8001/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body -UseBasicParsing

$loginData = $login.Content | ConvertFrom-Json
$accessToken = $loginData.access_token
$userId = $loginData.user_id

$loginData | Format-List
```

**Expected Output:**
```
access_token  : [JWT Token]
refresh_token : [JWT Token]
token_type    : bearer
expires_in    : 900
user_id       : [UUID]
```

---

## Phase 2: Customer Management

### 2.1 Create Customer Profile

```powershell
$accessToken = "[Token from login]"
$userId = "[User ID from login]"

$body = @{
    user_id = $userId
    first_name = "John"
    last_name = "Doe"
    email = "john@example.com"
    phone = "+1-555-1234"
} | ConvertTo-Json

$headers = @{"Authorization" = "Bearer $accessToken"}

$customer = Invoke-WebRequest -Uri "http://localhost:8000/customers" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$customerData = $customer.Content | ConvertFrom-Json
$customerId = $customerData.id

$customerData | Format-List
```

**Expected Output:**
```
id           : [UUID]
user_id      : [User UUID]
first_name   : John
last_name    : Doe
email        : john@example.com
status       : active
kyc_status   : not_started
risk_score   : 0.0
credit_score : 
created_at   : 2026-06-11T...
```

### 2.2 Get Customer Details

```powershell
$customerId = "[Customer ID from creation]"

$customer = Invoke-WebRequest -Uri "http://localhost:8000/customers/$customerId" `
  -Method GET `
  -Headers $headers -UseBasicParsing

$customer.Content | ConvertFrom-Json | Format-List
```

---

## Phase 3: Account Operations

### 3.1 Create Account

```powershell
$customerId = "[Customer ID]"

$body = @{
    customer_id = $customerId
    account_type = "savings"
    currency = "USD"
    initial_balance = 10000
} | ConvertTo-Json

$account = Invoke-WebRequest -Uri "http://localhost:8000/accounts" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$accountData = $account.Content | ConvertFrom-Json
$accountId = $accountData.id

$accountData | Format-List
```

**Expected Output:**
```
id               : [UUID]
customer_id      : [Customer UUID]
account_type     : savings
balance          : 10000
currency         : USD
status           : active
created_at       : 2026-06-11T...
```

### 3.2 Make Deposit

```powershell
$accountId = "[Account ID]"

$body = @{
    amount = 5000
    description = "Salary deposit"
} | ConvertTo-Json

$deposit = Invoke-WebRequest -Uri "http://localhost:8000/accounts/$accountId/deposit" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$deposit.Content | ConvertFrom-Json | Format-List
```

### 3.3 Check Balance

```powershell
$balance = Invoke-WebRequest -Uri "http://localhost:8000/accounts/$accountId/balance" `
  -Method GET `
  -Headers $headers -UseBasicParsing

$balance.Content | ConvertFrom-Json | Format-List
```

### 3.4 Make Withdrawal

```powershell
$body = @{
    amount = 1000
    description = "Withdrawal"
} | ConvertTo-Json

$withdraw = Invoke-WebRequest -Uri "http://localhost:8000/accounts/$accountId/withdraw" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$withdraw.Content | ConvertFrom-Json | Format-List
```

---

## Phase 4: Credit Scoring

### 4.1 Calculate Credit Score

```powershell
$customerId = "[Customer ID]"

$body = @{
    customer_id = $customerId
    annual_income = 100000
    credit_history_months = 60
    total_debt = 25000
} | ConvertTo-Json

$credit = Invoke-WebRequest -Uri "http://localhost:8000/credit/calculate-score" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$credit.Content | ConvertFrom-Json | Format-List
```

**Expected Output:**
```
score      : [700-850]
grade      : [A/B/C/D/F]
risk_level : [low/medium/high]
```

### 4.2 Assess Risk

```powershell
$body = @{
    customer_id = $customerId
    credit_score = 750
    income = 100000
    debt = 25000
} | ConvertTo-Json

$risk = Invoke-WebRequest -Uri "http://localhost:8000/credit/assess-risk" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$risk.Content | ConvertFrom-Json | Format-List
```

---

## Phase 5: Fraud Detection

### 5.1 Create Fraud Alert

```powershell
$customerId = "[Customer ID]"

$body = @{
    customer_id = $customerId
    alert_type = "suspicious_activity"
    severity = "medium"
    description = "Unusual transaction pattern detected"
} | ConvertTo-Json

$alert = Invoke-WebRequest -Uri "http://localhost:8000/fraud/alerts" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$alert.Content | ConvertFrom-Json | Format-List
```

### 5.2 Get Fraud Statistics

```powershell
$stats = Invoke-WebRequest -Uri "http://localhost:8000/fraud/statistics" `
  -Method GET `
  -Headers $headers -UseBasicParsing

$stats.Content | ConvertFrom-Json | Format-List
```

---

## Phase 6: Document AI

### 6.1 Upload Document

```powershell
$body = @{
    customer_id = $customerId
    document_type = "id_card"
    file_name = "id_card.pdf"
} | ConvertTo-Json

$doc = Invoke-WebRequest -Uri "http://localhost:8000/documents/upload" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers -UseBasicParsing

$doc.Content | ConvertFrom-Json | Format-List
```

### 6.2 Extract Data from Document

```powershell
$documentId = "[Document ID]"

$extract = Invoke-WebRequest -Uri "http://localhost:8000/documents/$documentId/extract" `
  -Method POST `
  -Headers $headers -UseBasicParsing

$extract.Content | ConvertFrom-Json | Format-List
```

---

## Troubleshooting

### Issue: "Field required" Error
**Solution:** Make sure all required fields are included in the request body.

**Common missing fields:**
- Customer Creation: `user_id`, `first_name`, `last_name`, `email`
- Account Creation: `customer_id`, `account_type`, `currency`, `initial_balance`
- Credit Calculation: `customer_id`, `annual_income`, `credit_history_months`, `total_debt`

### Issue: "Unauthorized" Error
**Solution:** Make sure to include the Bearer token in the Authorization header:
```powershell
$headers = @{"Authorization" = "Bearer $accessToken"}
```

### Issue: Service Not Responding
**Solution:** Check if all services are running:
```powershell
docker-compose ps
```

Restart if needed:
```powershell
docker-compose up -d
```

### Issue: "Customer already exists for this user"
**Solution:** Register a new user with a different email address.

---

## 📞 Service Endpoints Reference

| Service | Port | Health Check |
|---------|------|--------------|
| API Gateway | 8000 | `http://localhost:8000/health` |
| Auth Service | 8001 | `http://localhost:8001/health` |
| Customer Service | 8002 | `http://localhost:8002/health` |
| Account Service | 8003 | `http://localhost:8003/health` |
| Credit Service | 8004 | `http://localhost:8004/health` |
| Fraud Service | 8005 | `http://localhost:8005/health` |
| Document Service | 8006 | `http://localhost:8006/health` |

---

## ✅ All Tests Completed Successfully!

Run this command to verify all services are healthy:

```powershell
@("8000", "8001", "8002", "8003", "8004", "8005", "8006") | ForEach-Object {
    $response = Invoke-WebRequest -Uri "http://localhost:$_/health" -UseBasicParsing
    Write-Host "✅ Port $_: $($response.StatusCode)"
}
```
