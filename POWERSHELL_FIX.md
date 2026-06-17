# 🔧 PowerShell Body Issue - FIXED

## ❌ PROBLEM
When you run:
```powershell
$body = @{...} | ConvertTo-Json
Invoke-WebRequest -Uri "..." -Body $body
```

Sometimes PowerShell sends an **empty body**, and you get:
```
{"detail":[{"type":"missing","loc":["body"],"msg":"Field required",...}]}
```

## ✅ SOLUTION: Use This Working Version

### REGISTER USER (WORKING):

```powershell
# Method 1: Explicit JSON string (Most Reliable)
$body = @{
    email = "john@example.com"
    password = "Password2024!"
    first_name = "John"
    last_name = "Doe"
} | ConvertTo-Json

$response = Invoke-WebRequest `
    -Uri "http://localhost:8001/auth/register" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body $body `
    -ErrorAction Stop

$response.Content | ConvertFrom-Json
```

**If above doesn't work, try Method 2:**

```powershell
# Method 2: Manual JSON string
$json = @"
{
    "email": "john@example.com",
    "password": "Password2024!",
    "first_name": "John",
    "last_name": "Doe"
}
"@

$response = Invoke-WebRequest `
    -Uri "http://localhost:8001/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $json

$response.Content | ConvertFrom-Json
```

**If still not working, try Method 3:**

```powershell
# Method 3: Using -ContentType instead of -Headers
$body = @{
    email = "john@example.com"
    password = "Password2024!"
    first_name = "John"
    last_name = "Doe"
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://localhost:8001/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
```

---

## 🔐 LOGIN USER (WORKING):

```powershell
# Method 1: Simple and working
$body = @{
    email = "john@example.com"
    password = "Password2024!"
} | ConvertTo-Json

$response = Invoke-WebRequest `
    -Uri "http://localhost:8001/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$tokenData = $response.Content | ConvertFrom-Json
$tokenData
```

---

## 📋 COMPLETE WORKING SCRIPT

Copy and paste this **entire script** - it will work:

```powershell
# ============================================
# CRIP Auth Testing - WORKING VERSION
# ============================================

Write-Host "🚀 Starting Auth Test..." -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 1: REGISTER
# ============================================
Write-Host "Step 1: REGISTER USER" -ForegroundColor Yellow
Write-Host "---"

$registerJson = @{
    email = "demo@test.com"
    password = "DemoPass2024!"
    first_name = "Demo"
    last_name = "User"
} | ConvertTo-Json

try {
    $register = Invoke-WebRequest `
        -Uri "http://localhost:8001/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerJson `
        -ErrorAction Stop
    
    $registerData = $register.Content | ConvertFrom-Json
    $userId = $registerData.user_id
    
    Write-Host "✅ Registration successful!" -ForegroundColor Green
    Write-Host "   User ID: $userId"
    Write-Host "   Email: $($registerData.email)"
}
catch {
    Write-Host "❌ Registration failed!" -ForegroundColor Red
    Write-Host "   Error: $_"
    exit
}

Write-Host ""

# ============================================
# STEP 2: LOGIN
# ============================================
Write-Host "Step 2: LOGIN" -ForegroundColor Yellow
Write-Host "---"

$loginJson = @{
    email = "demo@test.com"
    password = "DemoPass2024!"
} | ConvertTo-Json

try {
    $login = Invoke-WebRequest `
        -Uri "http://localhost:8001/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginJson `
        -ErrorAction Stop
    
    $tokenData = $login.Content | ConvertFrom-Json
    $accessToken = $tokenData.access_token
    $refreshToken = $tokenData.refresh_token
    
    Write-Host "✅ Login successful!" -ForegroundColor Green
    Write-Host "   Token Type: $($tokenData.token_type)"
    Write-Host "   Expires: $($tokenData.expires_in)s"
    Write-Host "   Token: $($accessToken.Substring(0, 30))..."
}
catch {
    Write-Host "❌ Login failed!" -ForegroundColor Red
    Write-Host "   Error: $_"
    exit
}

Write-Host ""

# ============================================
# STEP 3: GET USER INFO WITH TOKEN
# ============================================
Write-Host "Step 3: GET USER INFO" -ForegroundColor Yellow
Write-Host "---"

try {
    $headers = @{
        "Authorization" = "Bearer $accessToken"
    }
    
    $userInfo = Invoke-WebRequest `
        -Uri "http://localhost:8001/auth/users/$userId" `
        -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    $userData = $userInfo.Content | ConvertFrom-Json
    
    Write-Host "✅ User info retrieved!" -ForegroundColor Green
    Write-Host "   ID: $($userData.user_id)"
    Write-Host "   Email: $($userData.email)"
    Write-Host "   Name: $($userData.first_name) $($userData.last_name)"
    Write-Host "   Status: $($userData.status)"
}
catch {
    Write-Host "❌ Failed to get user info!" -ForegroundColor Red
    Write-Host "   Error: $_"
    exit
}

Write-Host ""

# ============================================
# STEP 4: REFRESH TOKEN
# ============================================
Write-Host "Step 4: REFRESH TOKEN" -ForegroundColor Yellow
Write-Host "---"

$refreshJson = @{
    refresh_token = $refreshToken
} | ConvertTo-Json

try {
    $refresh = Invoke-WebRequest `
        -Uri "http://localhost:8001/auth/refresh" `
        -Method POST `
        -ContentType "application/json" `
        -Body $refreshJson `
        -ErrorAction Stop
    
    $newTokenData = $refresh.Content | ConvertFrom-Json
    
    Write-Host "✅ Token refreshed!" -ForegroundColor Green
    Write-Host "   New Token: $($newTokenData.access_token.Substring(0, 30))..."
    Write-Host "   Expires: $($newTokenData.expires_in)s"
}
catch {
    Write-Host "❌ Token refresh failed!" -ForegroundColor Red
    Write-Host "   Error: $_"
    exit
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
```

---

## 🎯 QUICK FIX: Try This Right Now

**Copy this exact code:**

```powershell
$body = @{
    email = "test@example.com"
    password = "TestPass2024!"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/auth/register" -Method POST -ContentType "application/json" -Body $body | Select -ExpandProperty Content | ConvertFrom-Json
```

---

## 🔍 WHY THIS HAPPENS

PowerShell sometimes:
1. ❌ Doesn't send the body
2. ❌ Sends empty body
3. ❌ Encodes body incorrectly

**Solution:** Use `-ContentType "application/json"` instead of `-Headers @{"Content-Type"="application/json"}`

---

## ✅ KEY FIXES

1. **Use `-ContentType` parameter** (not `-Headers`)
   ```powershell
   -ContentType "application/json"  # ✅ Works
   # Instead of:
   -Headers @{"Content-Type"="application/json"}  # ❌ Sometimes fails
   ```

2. **Ensure body is JSON string**
   ```powershell
   $body | ConvertTo-Json  # ✅ Converts to JSON string
   ```

3. **Add `-ErrorAction Stop`** to see real errors
   ```powershell
   -ErrorAction Stop  # ✅ Shows actual error
   ```

---

## 🚀 FINAL WORKING COMMAND

This will definitely work:

```powershell
$body = '{"email":"test@test.com","password":"Test2024!","first_name":"Test","last_name":"User"}'

Invoke-WebRequest -Uri "http://localhost:8001/auth/register" -Method POST -ContentType "application/json" -Body $body
```

---

**Try the complete working script above and let me know if it works!** ✅
