# User Registration & Login Guide - CRIP Auth Service

## 🚀 Quick Start: 5 Steps to Auth Success

### Step 1: Start All Services
```bash
cd c:\Users\asdha\credit-risk-platform
docker-compose up -d
```

Wait 10 seconds for services to initialize, then verify:
```bash
curl http://localhost:8001/health
```

You should see:
```json
{"status": "healthy"}
```

---

## 📝 REGISTER NEW USER

⚠️ **WINDOWS USERS:** Skip Method 1 (curl) and go directly to **Method 2 (PowerShell)** below!

curl commands don't work in PowerShell. Use `Invoke-WebRequest` instead.

### Method 1: Using curl (Linux/Mac/Git Bash ONLY)

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Expected Response (201 Created):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active",
  "created_at": "2026-06-11T10:30:45.123456"
}
```

---

### Method 2: Using PowerShell ✅ **USE THIS ON WINDOWS**

```powershell
# Copy and paste this entire block into PowerShell
$body = @{
    email = "john.doe@example.com"
    password = "SecurePassword123"
    first_name = "John"
    last_name = "Doe"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Expected Output:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active"
}
```

---

### Method 3: Using Postman

1. **Open Postman**
2. **Create New Request:**
   - Method: **POST**
   - URL: `http://localhost:8001/auth/register`
   
3. **Headers Tab:**
   ```
   Content-Type: application/json
   ```

4. **Body Tab** (select "raw" → "JSON"):
   ```json
   {
     "email": "john.doe@example.com",
     "password": "SecurePassword123",
     "first_name": "John",
     "last_name": "Doe"
   }
   ```

5. **Click Send**

---

## 🔐 LOGIN & GET JWT TOKEN

⚠️ **WINDOWS USERS:** Use **Method 2 (PowerShell)** below!

### Method 1: Using curl (Linux/Mac/Git Bash ONLY)

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePassword123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Copy the access_token - you'll need it!** ✅

---

### Method 2: Using PowerShell ✅ **USE THIS ON WINDOWS**

```powershell
# Copy and paste this entire block into PowerShell
$body = @{
    email = "john.doe@example.com"
    password = "SecurePassword123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8001/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

$response.Content | ConvertFrom-Json
```

**Expected Output:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**✅ Copy the access_token - you'll need it!**

---

### Method 3: Using Postman

1. **Create New Request:**
   - Method: **POST**
   - URL: `http://localhost:8001/auth/login`

2. **Headers Tab:**
   ```
   Content-Type: application/json
   ```

3. **Body Tab** (raw → JSON):
   ```json
   {
     "email": "john.doe@example.com",
     "password": "SecurePassword123"
   }
   ```

4. **Click Send** → Copy the `access_token` value

---

## ✅ VERIFY LOGIN WORKED

### Use Access Token to Get User Info

**With curl:**
```bash
# Replace YOUR_TOKEN with the access_token you got from login
curl -X GET http://localhost:8001/auth/users/YOUR_USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example with real token:**
```bash
curl -X GET http://localhost:8001/auth/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Expected Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active",
  "created_at": "2026-06-11T10:30:45.123456"
}
```

---

## 🔄 REFRESH YOUR TOKEN

When access_token expires, use refresh_token to get a new one:

```bash
curl -X POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN_HERE"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

## 🎯 COMPLETE WORKFLOW EXAMPLE

### Step-by-Step with curl

```bash
# 1. REGISTER NEW USER
echo "📝 Registering user..."
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@company.com",
    "password": "Alice2024Secure!",
    "first_name": "Alice",
    "last_name": "Smith"
  }'

echo ""
echo "✅ User registered! Now logging in..."
echo ""

# 2. LOGIN & GET TOKENS
echo "🔐 Logging in..."
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@company.com",
    "password": "Alice2024Secure!"
  }'

# 3. SAVE TOKEN and use it for next request
# (You'll need to manually copy the access_token)
```

---

## 🧪 TESTING IN POSTMAN (Complete Flow)

### 1. Create Collection
- New → Collection → Name it "Auth Testing"

### 2. Request 1: Register User
```
POST http://localhost:8001/auth/register

Body (raw/JSON):
{
  "email": "test.user@example.com",
  "password": "TestPass123",
  "first_name": "Test",
  "last_name": "User"
}
```

### 3. Request 2: Login
```
POST http://localhost:8001/auth/login

Body (raw/JSON):
{
  "email": "test.user@example.com",
  "password": "TestPass123"
}

Save the access_token from response
```

### 4. Request 3: Get User (with Auth)
```
GET http://localhost:8001/auth/users/[user_id_from_register]

Headers:
Authorization: Bearer [access_token_from_login]
```

---

## ⚡ PRACTICAL TEST SCENARIOS

### Scenario 1: New User Registration

**Input:**
```bash
Email: new.user@example.com
Password: MySecurePass2024
First Name: John
Last Name: Smith
```

**Expected Flow:**
1. Register → User created ✅
2. Login → JWT tokens issued ✅
3. Use token → Access user info ✅

### Scenario 2: Wrong Password

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "WrongPassword"
  }'
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid credentials"
}
```

### Scenario 3: User Not Found

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "AnyPassword"
  }'
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid credentials"
}
```

---

## 📋 PASSWORD REQUIREMENTS

When registering, your password must meet:
- ✅ Minimum 8 characters
- ✅ Should contain uppercase and lowercase
- ✅ Should contain numbers
- ✅ Should contain special characters

**Good Examples:**
- `SecurePass123!`
- `MyPassword2024@`
- `TestUser#2026`

**Bad Examples:**
- `password` (too simple)
- `12345678` (numbers only)
- `Pass123` (only 7 characters)

---

## 🔍 DEBUG COMMON ISSUES

### Issue 1: "Connection refused" on localhost:8001
**Solution:**
```bash
# Check if services are running
docker-compose ps

# If not running, start them
docker-compose up -d

# Check logs
docker-compose logs auth-service
```

### Issue 2: "Invalid email format"
**Solution:** Make sure email is valid:
- ✅ `user@example.com`
- ❌ `user@` (missing domain)
- ❌ `user.example.com` (missing @)

### Issue 3: "Password too weak"
**Solution:** Use stronger password:
- ❌ `pass123` (8 chars but weak)
- ✅ `Pass123!Strong` (12+ chars, mixed case, special char)

### Issue 4: "User already exists"
**Solution:** Use a different email or login with existing user
```bash
# List of test users created:
# john.doe@example.com
# alice@company.com
# test.user@example.com
```

---

## 🛠️ ADVANCED: Using Token with Other Services

Your JWT token from Auth Service can be used across all services:

```bash
# Use auth token to create customer (Gateway routes it to Customer Service)
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "email": "john@example.com",
    "phone": "555-0123",
    "address": "123 Main St"
  }'
```

---

## 📊 API ENDPOINTS REFERENCE

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---|
| `/auth/register` | POST | Create new user | ❌ No |
| `/auth/login` | POST | Get JWT tokens | ❌ No |
| `/auth/refresh` | POST | Get new access token | ❌ No |
| `/auth/users/{user_id}` | GET | Get user info | ✅ Yes |
| `/auth/change-password` | POST | Change password | ✅ Yes |
| `/auth/roles` | GET | List all roles | ✅ Yes |
| `/auth/roles/{user_id}` | POST | Assign role to user | ✅ Yes |
| `/health` | GET | Service health | ❌ No |

---

## 🎬 VIDEO-STYLE WALKTHROUGH

### Minute 1-2: Setup
```bash
# Terminal 1: Start services
cd c:\Users\asdha\credit-risk-platform
docker-compose up -d
```

### Minute 2-3: Register User
```bash
# Terminal 2: Register
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo2024!","first_name":"Demo","last_name":"User"}'
```

### Minute 3-4: Login
```bash
# Same terminal: Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo2024!"}'
```

### Minute 4-5: Verify Token
```bash
# Copy access_token from login response, then:
curl -X GET http://localhost:8001/auth/users/YOUR_USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💡 TIPS & TRICKS

✅ **Save tokens to file for reuse:**
```bash
# Windows PowerShell
curl -X POST http://localhost:8001/auth/login ... | ConvertFrom-Json > token.json
cat token.json
```

✅ **Use environment variables:**
```bash
# Linux/Mac
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login ... | jq -r '.access_token')
echo $TOKEN
```

✅ **Create shell script for repeated testing:**
```bash
#!/bin/bash
# save as login.sh
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$1\",\"password\":\"$2\"}"
```

---

## ✨ QUICK COPY-PASTE COMMANDS

### Register (Windows PowerShell):
```powershell
$body = @{
    email = "newuser@test.com"
    password = "TestPass2024!"
    first_name = "New"
    last_name = "User"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/auth/register" -Method POST -ContentType "application/json" -Body $body
```

### Login (Windows PowerShell):
```powershell
$body = @{
    email = "newuser@test.com"
    password = "TestPass2024!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8001/auth/login" -Method POST -ContentType "application/json" -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json
```

---

## 🎯 NEXT STEPS AFTER LOGIN

Once you have a JWT token, you can:

1. **Create Customer Profile**
   ```bash
   curl -X POST http://localhost:8000/customers \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Create Account**
   ```bash
   curl -X POST http://localhost:8000/accounts \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Make Transaction**
   ```bash
   curl -X POST http://localhost:8000/accounts/ACCOUNT_ID/deposit \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

---

## 🎉 SUMMARY

**You now know how to:**
✅ Register a new user
✅ Login and get JWT tokens
✅ Use tokens to access protected endpoints
✅ Refresh expired tokens
✅ Test all authentication flows

**Start testing now!** 🚀

---

**Need Help?** Check service logs:
```bash
docker-compose logs -f auth-service
```

**Still having issues?** Validate services are running:
```bash
curl http://localhost:8000/services/health
```
