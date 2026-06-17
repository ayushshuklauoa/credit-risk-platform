#!/bin/bash

# ============================================
# CRIP Auth Service Testing Script (Linux/Mac)
# Save as: auth-test.sh
# Usage: bash auth-test.sh
# ============================================

set -e  # Exit on error

echo ""
echo "============================================================"
echo "  CRIP Enterprise Platform - Auth Testing"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${YELLOW}Step $1️⃣ : $2${NC}"
    echo "------------------------------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if services are running
print_info "Checking if Auth Service is running..."
if ! curl -s http://localhost:8001/health > /dev/null; then
    print_error "Auth Service is not running!"
    echo "Start services with: docker-compose up -d"
    exit 1
fi
print_success "Auth Service is running!"
echo ""

# ============================================
# STEP 1: REGISTER NEW USER
# ============================================
print_step "1" "REGISTER NEW USER"

EMAIL="demo.user@example.com"
PASSWORD="DemoUser2024!"
FIRST_NAME="Demo"
LAST_NAME="User"

echo "📝 Registering user: $EMAIL"
echo ""

REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"first_name\": \"$FIRST_NAME\",
    \"last_name\": \"$LAST_NAME\"
  }")

# Extract user_id from response
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.user_id' 2>/dev/null)

if [ -z "$USER_ID" ] || [ "$USER_ID" == "null" ]; then
    print_error "Registration failed!"
    echo "Response: $REGISTER_RESPONSE"
    exit 1
fi

print_success "Registration successful!"
echo "User ID: $USER_ID"
echo "Email: $EMAIL"
echo ""

read -p "Press Enter to continue to Login..."
echo ""

# ============================================
# STEP 2: LOGIN & GET JWT TOKENS
# ============================================
print_step "2" "LOGIN & GET JWT TOKENS"

echo "🔐 Logging in with registered credentials..."
echo ""

LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

# Extract tokens
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token' 2>/dev/null)
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token' 2>/dev/null)
TOKEN_TYPE=$(echo $LOGIN_RESPONSE | jq -r '.token_type' 2>/dev/null)
EXPIRES_IN=$(echo $LOGIN_RESPONSE | jq -r '.expires_in' 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" == "null" ]; then
    print_error "Login failed!"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

print_success "Login successful!"
echo "Token Type: $TOKEN_TYPE"
echo "Expires In: $EXPIRES_IN seconds"
echo ""
echo "🔑 Access Token (first 50 chars):"
echo "${BLUE}${ACCESS_TOKEN:0:50}...${NC}"
echo ""

read -p "Press Enter to verify the token..."
echo ""

# ============================================
# STEP 3: GET USER INFO WITH TOKEN
# ============================================
print_step "3" "VERIFY TOKEN - GET USER INFO"

echo "📋 Fetching user info using token..."
echo ""

USER_INFO_RESPONSE=$(curl -s -X GET http://localhost:8001/auth/users/$USER_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN")

USER_EMAIL=$(echo $USER_INFO_RESPONSE | jq -r '.email' 2>/dev/null)

if [ -z "$USER_EMAIL" ] || [ "$USER_EMAIL" == "null" ]; then
    print_error "Failed to get user info!"
    echo "Response: $USER_INFO_RESPONSE"
    exit 1
fi

print_success "Token verified successfully!"
echo ""
echo "User Information:"
echo "  User ID: $(echo $USER_INFO_RESPONSE | jq -r '.user_id')"
echo "  Email: $(echo $USER_INFO_RESPONSE | jq -r '.email')"
echo "  Name: $(echo $USER_INFO_RESPONSE | jq -r '.first_name') $(echo $USER_INFO_RESPONSE | jq -r '.last_name')"
echo "  Status: $(echo $USER_INFO_RESPONSE | jq -r '.status')"
echo "  Created: $(echo $USER_INFO_RESPONSE | jq -r '.created_at')"
echo ""

read -p "Press Enter to refresh the token..."
echo ""

# ============================================
# STEP 4: REFRESH TOKEN
# ============================================
print_step "4" "REFRESH TOKEN"

echo "🔄 Refreshing access token..."
echo ""

REFRESH_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }")

NEW_ACCESS_TOKEN=$(echo $REFRESH_RESPONSE | jq -r '.access_token' 2>/dev/null)

if [ -z "$NEW_ACCESS_TOKEN" ] || [ "$NEW_ACCESS_TOKEN" == "null" ]; then
    print_error "Token refresh failed!"
    echo "Response: $REFRESH_RESPONSE"
    exit 1
fi

print_success "Token refreshed successfully!"
echo "New Access Token (first 50 chars):"
echo "${BLUE}${NEW_ACCESS_TOKEN:0:50}...${NC}"
echo "Expires In: $(echo $REFRESH_RESPONSE | jq -r '.expires_in') seconds"
echo ""

# ============================================
# SUMMARY
# ============================================
echo ""
echo "============================================================"
print_success "ALL TESTS COMPLETED SUCCESSFULLY!"
echo "============================================================"
echo ""
echo "Summary:"
echo "  ✅ User registered"
echo "  ✅ User logged in"
echo "  ✅ Token verified"
echo "  ✅ Token refreshed"
echo ""
echo -e "${GREEN}You can now use this workflow in your application!${NC}"
echo ""

# Display tokens for reference
echo "For reference (do not share these tokens):"
echo "User ID: $USER_ID"
echo "Access Token: ${ACCESS_TOKEN:0:30}..."
echo ""
