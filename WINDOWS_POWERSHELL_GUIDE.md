# 🪟 WINDOWS POWERSHELL - Auth Testing Guide

## ⚠️ IMPORTANT: Use PowerShell Commands, NOT curl!

**curl** = Linux/Mac command (doesn't work in PowerShell)
**PowerShell** = Windows command (use this instead!)

---

## ✅ STEP 1: START SERVICES

Open PowerShell and run:

```powershell
cd c:\Users\asdha\credit-risk-platform
docker-compose up -d
```

Wait 10 seconds, then verify services are running:

```powershell
curl http://localhost:8001/health
```

Expected: `{"status":"healthy"}`

---

## ✅ STEP 2: REGISTER A USER

Copy and paste **the entire block** into PowerShell:

```powershell
$body = @{
    email = "john@example.com"
    password = "Password2024!"
    first_name = "John"
    last_name = "Doe"
} | ConvertTo-Json

$register = Invoke-WebRequest -Uri "http://localhost:8001/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

$register.Content | ConvertFrom-Json
```

**You'll see:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active"
}
```

**✅ Save the user_id - you'll need it later!**

---

## ✅ STEP 3: LOGIN & GET TOKEN

Copy and paste **the entire block** into PowerShell:

```powershell
$body = @{
    email = "john@example.com"
    password = "Password2024!"
} | ConvertTo-Json

$login = Invoke-WebRequest -Uri "http://localhost:8001/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

$tokenData = $login.Content | ConvertFrom-Json
$tokenData
```

**You'll see:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**✅ Copy the access_token - you need this for the next step!**

---

## ✅ STEP 4: USE TOKEN TO GET USER INFO

Replace `YOUR_USER_ID` and `YOUR_TOKEN` with values from steps 2 and 3:

```powershell
$userId = "550e8400-e29b-41d4-a716-446655440000"  # From Step 2
$token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."  # From Step 3

$headers = @{
    "Authorization" = "Bearer $token"
}

$userInfo = Invoke-WebRequest -Uri "http://localhost:8001/auth/users/$userId" `
  -Method GET `
  -Headers $headers

$userInfo.Content | ConvertFrom-Json
```

**You'll see your user info:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active"
}
```

**✅ Success! Your token works!**

---

## 🚀 AUTOMATED TEST (Optional)

Run this script to test everything automatically:

```powershell
.\auth-test.ps1
```

It will:
1. Register a user
2. Login
3. Verify token
4. Refresh token

---

## 🔄 REFRESH TOKEN (After 1 Hour)

When your access_token expires (after 3600 seconds), refresh it:

```powershell
$refreshBody = @{
    refresh_token = "YOUR_REFRESH_TOKEN_HERE"  # From login
} | ConvertTo-Json

$refresh = Invoke-WebRequest -Uri "http://localhost:8001/auth/refresh" `
  -Method POST `
  -ContentType "application/json" `
  -Body $refreshBody

$newToken = $refresh.Content | ConvertFrom-Json
$newToken
```

**You'll get a new access_token to use!**

---

## 📊 COMPLETE POWERSHELL WORKFLOW

Save this as `auth-workflow.ps1` and run it:

```powershell
# ========== CONFIGURATION ==========
$email = "demo@test.com"
$password = "Demo2024!"
$firstName = "Demo"
$lastName = "User"
$apiUrl = "http://localhost:8001"

# ========== REGISTER ==========
Write-Host "📝 Registering user..." -ForegroundColor Green

$registerBody = @{
    email = $email
    password = $password
    first_name = $firstName
    last_name = $lastName
} | ConvertTo-Json

$register = Invoke-WebRequest -Uri "$apiUrl/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $registerBody

$userId = ($register.Content | ConvertFrom-Json).user_id
Write-Host "✅ User registered! ID: $userId" -ForegroundColor Green

# ========== LOGIN ==========
Write-Host "🔐 Logging in..." -ForegroundColor Green

$loginBody = @{
    email = $email
    password = $password
} | ConvertTo-Json

$login = Invoke-WebRequest -Uri "$apiUrl/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $loginBody

$tokenData = $login.Content | ConvertFrom-Json
$accessToken = $tokenData.access_token
$refreshToken = $tokenData.refresh_token

Write-Host "✅ Login successful!" -ForegroundColor Green
Write-Host "Access Token: $($accessToken.Substring(0, 30))..." -ForegroundColor Cyan

# ========== GET USER INFO ==========
Write-Host "📋 Getting user info..." -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $accessToken"
}

$userInfo = Invoke-WebRequest -Uri "$apiUrl/auth/users/$userId" `
  -Method GET `
  -Headers $headers

$user = $userInfo.Content | ConvertFrom-Json
Write-Host "✅ User Info Retrieved:" -ForegroundColor Green
Write-Host "   Email: $($user.email)"
Write-Host "   Name: $($user.first_name) $($user.last_name)"
Write-Host "   Status: $($user.status)"

# ========== REFRESH TOKEN ==========
Write-Host "🔄 Refreshing token..." -ForegroundColor Green

$refreshBody = @{
    refresh_token = $refreshToken
} | ConvertTo-Json

$refresh = Invoke-WebRequest -Uri "$apiUrl/auth/refresh" `
  -Method POST `
  -ContentType "application/json" `
  -Body $refreshBody

$newTokenData = $refresh.Content | ConvertFrom-Json
Write-Host "✅ Token refreshed!" -ForegroundColor Green
Write-Host "New Access Token: $($newTokenData.access_token.Substring(0, 30))..." -ForegroundColor Cyan

# ========== SUMMARY ==========
Write-Host ""
Write-Host "========== SUCCESS ==========" -ForegroundColor Green
Write-Host "✅ User registered"
Write-Host "✅ User logged in"
Write-Host "✅ Token verified"
Write-Host "✅ Token refreshed"
Write-Host "============================"
```

Run it:
```powershell
.\auth-workflow.ps1
```

---

## 🆘 TROUBLESHOOTING

### Problem: "Connection refused"
```powershell
# Check if services are running
docker-compose ps

# If they're not, start them:
docker-compose up -d

# Wait 10 seconds and try again
```

### Problem: "Invalid credentials"
```powershell
# Make sure email and password match what you registered
# Try logging in again with correct credentials
```

### Problem: "User already exists"
```powershell
# Use a different email address
$email = "different@test.com"  # Change this
```

### Problem: "Authorization header is invalid"
```powershell
# Make sure you have the correct token format:
# Should be: "Bearer eyJhbGciOiJSUzI1NiI..."
# Check that token starts with "eyJ"
```

---

## 💡 USEFUL POWERSHELL TRICKS

### Save token to variable for reuse:
```powershell
$token = ($login.Content | ConvertFrom-Json).access_token
Write-Host "Token saved: $token"
```

### Pretty print JSON responses:
```powershell
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Save response to file:
```powershell
$response.Content | Out-File -FilePath "response.json"
```

### Extract specific field:
```powershell
$userId = ($register.Content | ConvertFrom-Json).user_id
Write-Host "User ID: $userId"
```

---

## 📋 QUICK REFERENCE: PowerShell vs curl

| Task | curl (Linux) | PowerShell (Windows) |
|------|--------------|----------------------|
| POST | `curl -X POST` | `Invoke-WebRequest -Method POST` |
| GET | `curl -X GET` | `Invoke-WebRequest -Method GET` |
| Header `-H` | `-H "name: value"` | `-Headers @{"name"="value"}` |
| Body `-d` | `-d '{"key":"value"}'` | `-Body $body` (JSON) |
| Response | stdout | `$response.Content` |

---

## 🎯 NEXT STEPS WITH YOUR TOKEN

Now that you have a working token, you can:

```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"

# 1. Create a customer
$customerBody = @{
    email = "john@example.com"
    phone = "555-0123"
    address = "123 Main St"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/customers" `
  -Method POST `
  -ContentType "application/json" `
  -Body $customerBody `
  -Headers @{"Authorization" = "Bearer $token"}

# 2. List all customers
Invoke-WebRequest -Uri "http://localhost:8000/customers" `
  -Method GET `
  -Headers @{"Authorization" = "Bearer $token"}

# 3. Create an account
Invoke-WebRequest -Uri "http://localhost:8000/accounts" `
  -Method POST `
  -Headers @{"Authorization" = "Bearer $token"}
```

---

## ✅ YOU'RE READY!

✅ You can register users
✅ You can login
✅ You can get tokens
✅ You can refresh tokens
✅ You can make authenticated requests

**All using PowerShell on Windows!** 🎉

---

**Questions?** Check the full guide: `AUTH_USER_GUIDE.md`
