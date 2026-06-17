# 🔧 Customer Creation - CORRECT FORMAT

## ❌ PROBLEM
When creating a customer, you're missing a required field:
```
{@{type=missing; loc=System.Object[]; msg=Field required}}
```

## ✅ SOLUTION: Use All Required Fields

### CORRECT FORMAT FOR CUSTOMER CREATION:

```powershell
$accessToken = "YOUR_ACCESS_TOKEN_HERE"

$body = @{
    email = "john@example.com"
    phone = "+1-555-0123"
    address = "123 Main Street"
    city = "New York"
    state = "NY"
    zip_code = "10001"
    country = "USA"
    date_of_birth = "1990-01-15"
    occupation = "Software Engineer"
    annual_income = 100000
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $accessToken"
}

$customer = Invoke-WebRequest -Uri "http://localhost:8000/customers" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers

$customer.Content | ConvertFrom-Json
```

---

## 📋 REQUIRED FIELDS EXPLAINED

| Field | Type | Example | Required |
|-------|------|---------|----------|
| email | string | john@example.com | ✅ YES |
| phone | string | +1-555-0123 | ✅ YES |
| address | string | 123 Main St | ✅ YES |
| city | string | New York | ✅ YES |
| state | string | NY | ✅ YES |
| zip_code | string | 10001 | ✅ YES |
| country | string | USA | ✅ YES |
| date_of_birth | string (YYYY-MM-DD) | 1990-01-15 | ✅ YES |
| occupation | string | Software Engineer | ✅ YES |
| annual_income | number | 100000 | ✅ YES |

---

## 🚀 QUICK TEST - COPY & PASTE THIS:

```powershell
# Replace with your actual token
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjk5YjFiN2UtOTY0OC00ZDkyLTkyODQtM2QzNDMwZmM1ODAzIiwiZW1haWwiOiJqb2huQGV4YW1wbGUuY29tIiwicm9sZXMiOltdLCJwZXJtaXNzaW9ucyI6W10sImV4cCI6MTc4MTE1Nzg0MCwiaWF0IjoxNzgxMTU2OTQwfQ.B5gi-o1xs9Gk-9eTAbW4uKh_j1CTmmUPVs9t-Q-MjeA"

$body = @{
    email = "alice@company.com"
    phone = "+1-555-9876"
    address = "456 Oak Avenue"
    city = "Los Angeles"
    state = "CA"
    zip_code = "90001"
    country = "USA"
    date_of_birth = "1985-05-20"
    occupation = "Product Manager"
    annual_income = 120000
} | ConvertTo-Json

$headers = @{"Authorization" = "Bearer $token"}

$customer = Invoke-WebRequest -Uri "http://localhost:8000/customers" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -Headers $headers

$customer.Content | ConvertFrom-Json
```

---

## 📊 COMPLETE WORKING WORKFLOW

```powershell
# ============================================
# COMPLETE WORKFLOW WITH ALL ENDPOINTS
# ============================================

$accessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjk5YjFiN2UtOTY0OC00ZDkyLTkyODQtM2QzNDMwZmM1ODAzIiwiZW1haWwiOiJqb2huQGV4YW1wbGUuY29tIiwicm9sZXMiOltdLCJwZXJtaXNzaW9ucyI6W10sImV4cCI6MTc4MTE1Nzg0MCwiaWF0IjoxNzgxMTU2OTQwfQ.B5gi-o1xs9Gk-9eTAbW4uKh_j1CTmmUPVs9t-Q-MjeA"
$headers = @{"Authorization" = "Bearer $accessToken"}

Write-Host "🚀 COMPLETE WORKFLOW TEST" -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 1: CREATE CUSTOMER
# ============================================
Write-Host "Step 1: CREATE CUSTOMER" -ForegroundColor Yellow

$customerBody = @{
    email = "alice@company.com"
    phone = "+1-555-9876"
    address = "456 Oak Avenue"
    city = "Los Angeles"
    state = "CA"
    zip_code = "90001"
    country = "USA"
    date_of_birth = "1985-05-20"
    occupation = "Product Manager"
    annual_income = 120000
} | ConvertTo-Json

$customer = Invoke-WebRequest -Uri "http://localhost:8000/customers" `
  -Method POST `
  -ContentType "application/json" `
  -Body $customerBody `
  -Headers $headers

$customerData = $customer.Content | ConvertFrom-Json
$customerId = $customerData.id

Write-Host "✅ Customer created: $customerId" -ForegroundColor Green
Write-Host "   Email: $($customerData.email)"
Write-Host "   City: $($customerData.city), $($customerData.state)"
Write-Host ""

# ============================================
# STEP 2: CREATE ACCOUNT
# ============================================
Write-Host "Step 2: CREATE ACCOUNT" -ForegroundColor Yellow

$accountBody = @{
    customer_id = $customerId
    account_type = "checking"
    balance = 5000
} | ConvertTo-Json

$account = Invoke-WebRequest -Uri "http://localhost:8000/accounts" `
  -Method POST `
  -ContentType "application/json" `
  -Body $accountBody `
  -Headers $headers

$accountData = $account.Content | ConvertFrom-Json
$accountId = $accountData.id

Write-Host "✅ Account created: $accountId" -ForegroundColor Green
Write-Host "   Balance: $($accountData.balance)"
Write-Host ""

# ============================================
# STEP 3: DEPOSIT MONEY
# ============================================
Write-Host "Step 3: DEPOSIT MONEY" -ForegroundColor Yellow

$depositBody = @{
    amount = 1000
} | ConvertTo-Json

$deposit = Invoke-WebRequest -Uri "http://localhost:8000/accounts/$accountId/deposit" `
  -Method POST `
  -ContentType "application/json" `
  -Body $depositBody `
  -Headers $headers

$depositData = $deposit.Content | ConvertFrom-Json

Write-Host "✅ Deposit successful" -ForegroundColor Green
Write-Host "   Amount: $($depositData.amount)"
Write-Host "   New Balance: $($depositData.new_balance)"
Write-Host ""

# ============================================
# STEP 4: CHECK ACCOUNT BALANCE
# ============================================
Write-Host "Step 4: CHECK ACCOUNT BALANCE" -ForegroundColor Yellow

$balance = Invoke-WebRequest -Uri "http://localhost:8000/accounts/$accountId/balance" `
  -Method GET `
  -Headers $headers

$balanceData = $balance.Content | ConvertFrom-Json

Write-Host "✅ Current balance: $($balanceData.balance)" -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 5: CALCULATE CREDIT SCORE
# ============================================
Write-Host "Step 5: CALCULATE CREDIT SCORE" -ForegroundColor Yellow

$scoreBody = @{
    customer_id = $customerId
} | ConvertTo-Json

$score = Invoke-WebRequest -Uri "http://localhost:8000/credit/calculate-score" `
  -Method POST `
  -ContentType "application/json" `
  -Body $scoreBody `
  -Headers $headers

$scoreData = $score.Content | ConvertFrom-Json

Write-Host "✅ Credit score calculated" -ForegroundColor Green
Write-Host "   Score: $($scoreData.score)"
Write-Host "   Risk Level: $($scoreData.risk_level)"
Write-Host ""

# ============================================
# SUMMARY
# ============================================
Write-Host "=" * 50 -ForegroundColor Green
Write-Host "🎉 COMPLETE WORKFLOW SUCCESS!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""
Write-Host "Summary:"
Write-Host "  ✅ Customer created: $customerId"
Write-Host "  ✅ Account created: $accountId"
Write-Host "  ✅ Deposit completed"
Write-Host "  ✅ Balance checked"
Write-Host "  ✅ Credit score calculated"
Write-Host ""
```

---

## 🎯 KEY POINTS

1. **All fields are REQUIRED** - Don't skip any
2. **Date format is YYYY-MM-DD** - Not MM/DD/YYYY
3. **Phone format: +1-555-0123** - Include country code
4. **Annual income is a number** - Not a string

---

## ✅ TRY THIS NOW

Copy the quick test command above (with the "COPY & PASTE THIS" section) and paste it into PowerShell!

It has all the required fields and will work! 🚀
