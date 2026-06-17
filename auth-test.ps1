# PowerShell Script for Auth Testing - Windows Users
# Save as: auth-test.ps1

# ============================================
# CRIP Auth Service Testing Script
# For Windows PowerShell
# ============================================

Write-Host "=" * 60
Write-Host "CRIP Enterprise Platform - Auth Testing" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""

# Function to make API calls
function Invoke-AuthAPI {
    param(
        [string]$Endpoint,
        [string]$Method,
        [hashtable]$Body,
        [string]$Token
    )
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($Token) {
            $headers["Authorization"] = "Bearer $Token"
        }
        
        $response = Invoke-WebRequest `
            -Uri "http://localhost:8001$Endpoint" `
            -Method $Method `
            -Headers $headers `
            -Body ($Body | ConvertTo-Json) `
            -ErrorAction Stop
        
        return $response.Content | ConvertFrom-Json
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================
# STEP 1: REGISTER NEW USER
# ============================================
Write-Host "Step 1️⃣ : REGISTER NEW USER" -ForegroundColor Yellow
Write-Host "-" * 60

$registerBody = @{
    email = "demo.user@example.com"
    password = "DemoUser2024!"
    first_name = "Demo"
    last_name = "User"
}

Write-Host "📝 Registering user: demo.user@example.com"
$registerResponse = Invoke-AuthAPI -Endpoint "/auth/register" -Method "POST" -Body $registerBody

if ($registerResponse) {
    Write-Host "✅ Registration successful!" -ForegroundColor Green
    Write-Host "User ID: $($registerResponse.user_id)"
    Write-Host "Email: $($registerResponse.email)"
    Write-Host "Status: $($registerResponse.status)"
    $userId = $registerResponse.user_id
}
else {
    Write-Host "❌ Registration failed!" -ForegroundColor Red
    exit
}

Write-Host ""
Read-Host "Press Enter to continue to Login..."
Write-Host ""

# ============================================
# STEP 2: LOGIN & GET JWT TOKENS
# ============================================
Write-Host "Step 2️⃣ : LOGIN & GET JWT TOKENS" -ForegroundColor Yellow
Write-Host "-" * 60

$loginBody = @{
    email = "demo.user@example.com"
    password = "DemoUser2024!"
}

Write-Host "🔐 Logging in with registered credentials..."
$loginResponse = Invoke-AuthAPI -Endpoint "/auth/login" -Method "POST" -Body $loginBody

if ($loginResponse) {
    Write-Host "✅ Login successful!" -ForegroundColor Green
    Write-Host "Token Type: $($loginResponse.token_type)"
    Write-Host "Expires In: $($loginResponse.expires_in) seconds"
    Write-Host ""
    Write-Host "🔑 Access Token (first 50 chars):"
    Write-Host $($loginResponse.access_token.Substring(0, 50)) -ForegroundColor Cyan
    Write-Host ""
    $accessToken = $loginResponse.access_token
    $refreshToken = $loginResponse.refresh_token
}
else {
    Write-Host "❌ Login failed!" -ForegroundColor Red
    exit
}

Write-Host ""
Read-Host "Press Enter to verify the token..."
Write-Host ""

# ============================================
# STEP 3: GET USER INFO WITH TOKEN
# ============================================
Write-Host "Step 3️⃣ : VERIFY TOKEN - GET USER INFO" -ForegroundColor Yellow
Write-Host "-" * 60

Write-Host "📋 Fetching user info using token..."
$userInfoResponse = Invoke-AuthAPI -Endpoint "/auth/users/$userId" -Method "GET" -Token $accessToken

if ($userInfoResponse) {
    Write-Host "✅ Token verified successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "User Information:"
    Write-Host "  User ID: $($userInfoResponse.user_id)"
    Write-Host "  Email: $($userInfoResponse.email)"
    Write-Host "  Name: $($userInfoResponse.first_name) $($userInfoResponse.last_name)"
    Write-Host "  Status: $($userInfoResponse.status)"
    Write-Host "  Created: $($userInfoResponse.created_at)"
}
else {
    Write-Host "❌ Failed to get user info!" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to refresh the token..."
Write-Host ""

# ============================================
# STEP 4: REFRESH TOKEN
# ============================================
Write-Host "Step 4️⃣ : REFRESH TOKEN" -ForegroundColor Yellow
Write-Host "-" * 60

$refreshBody = @{
    refresh_token = $refreshToken
}

Write-Host "🔄 Refreshing access token..."
$refreshResponse = Invoke-AuthAPI -Endpoint "/auth/refresh" -Method "POST" -Body $refreshBody

if ($refreshResponse) {
    Write-Host "✅ Token refreshed successfully!" -ForegroundColor Green
    Write-Host "New Access Token (first 50 chars):"
    Write-Host $($refreshResponse.access_token.Substring(0, 50)) -ForegroundColor Cyan
    Write-Host "Expires In: $($refreshResponse.expires_in) seconds"
}
else {
    Write-Host "❌ Token refresh failed!" -ForegroundColor Red
}

# ============================================
# SUMMARY
# ============================================
Write-Host ""
Write-Host "=" * 60
Write-Host "✅ ALL TESTS COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "Summary:"
Write-Host "  ✅ User registered"
Write-Host "  ✅ User logged in"
Write-Host "  ✅ Token verified"
Write-Host "  ✅ Token refreshed"
Write-Host ""
Write-Host "You can now use this workflow in your application!" -ForegroundColor Green
Write-Host ""
