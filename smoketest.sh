#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

check_health() { 
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

update_password() {
  echo "Updating password..."
  response=$(curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123", "new_password":"password12345"}')
  if echo "$response" | grep -q '"message": "Password password12345 updated successfully."'; then
    echo "Password updated successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to update password."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Initialization Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initialize the database."
    exit 1
  fi
}

look_up_stock() {
  echo "Looking up stock (AAPL)"
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/aapl")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID (1)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID 1):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID (1)."
    exit 1
  fi
}


view_portfolio() {
  echo "Getting the portfolio..."
  response=$(curl -s -X GET "$BASE_URL/view-portfolio")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Retrieved all stocks from the portfolio"
    if [ "$ECHO_JSON" = true ]; then
      echo "Portfolio JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Error retrieving stocks from portfolio"
    exit 1
  fi
}

calculate_portfolio_value() {
    echo "Calculating portfolio value"
    response=$(curl -s -X GET "$BASE_URL/calculate-portfolio-value")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Calculation successful"
    else
        echo "Calculation failed"
        exit 1
    fi
}

buy_stock() {
  echo "Buying stock..."
  response=$(curl -s -X POST "$BASE_URL/buy-stock" -H "Content-Type: application/json" \
    -d "{\"stock_symbol\":\"appl\", \"stock_name\":\"Apple Inc\", \"quantity\":"5"}")
  if echo "$response" | grep -q '"status": "stock purchased"'; then
    echo "Purchase successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Purchase JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to purchase stock."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

sell_stock() {
  symbol=$1
  quantity=$2

  echo "Buying stock..."
  response=$(curl -s -X POST "$BASE_URL/sell-stock" -H "Content-Type: application/json" \
    -d "{\"stock_symbol\":\"$symbol\", \"quantity\":"$quantity"}")
  if echo "$response" | grep -q '"status": "stock sold"'; then
    echo "Sold stocks successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Purchase JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to sell stock."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

check_health
init_db
create_user
login_user
update_password
view_portfolio
calculate_portfolio_value
echo "Tests passed"


