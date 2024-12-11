# CS411 Final Project - Ashtosh Bhandari, Berk Komurcuoglu, & Lily Beaudion

## Application Description

This application is a Flask-based API that allows users to manage their stock portfolio, including creating accounts, logging in, adding/removing stocks, and tracking portfolio value. It is designed for individual investors who want to manage their portfolios, execute trades, and monitor market conditions.

The application can only make 25 API calls a day for free, so it was difficult to perform extensive testing.

## Steps Required to Run
1) Run the docker script.
2) Create an API key from Alpha Vantage (https://www.alphavantage.co/)

## Variables Defined in Environment
- Dockerfile
- .env file
  - ALPHA_VANTAGE_API_KEY: API key needed to run the application.
  - DB_PATH: Database path for the application.
  - SQL_CREATE_TABLE_PATH: Path to SQL script used to create a database file.
  - CREATE_DB: Sets up the database
## Route Descriptions

### Route 1: Healthcheck
- **Path**: `/api/health`
- **Request Type**: `GET`
- **Purpose**: Verifies that the service is running and healthy.
- **Request Format**:
  - No parameters required.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: ```{"status": "healthy"}```
- **Example Request**:
  ```bash
  GET /api/health
- **Example Response**:
  ````json
    {
      "status": "healthy"
    }
  ````
  
### Route 2: Create Account
- **Path**: `/api/create-account`
- **Request Type**: `POST`
- **Purpose**: Creates a new user account with a username and password.
- **Request Format**:
  - `username` (String): User's chosen username.
  - `password` (String): User's chosen password.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 201
    - Content: ```{"status": "user added", "username": username}```
- **Example Request**:
  ````json
    {
      "username": "john_doe",
      "password": "securepassword"
    }
  ````
- **Example Response**:
  ````json
    {
      "status": "user added",
      "username": "john_doe"
    }
  ````


### Route 3: Login
- **Path**: `/api/login`
- **Request Type**: `POST`
- **Purpose**: Authenticates a user with their username and password.
- **Request Format**:
  - `username` (String): User's username.
  - `password` (String): User's password.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: ```{"message": "User 'username' logged in successfully."}```
- **Example Request**:
  ````json
    {
      "username": "john_doe",
      "password": "securepassword"
    }
  ````
- **Example Response**:
  ````json
    {
      "message": "User john_doe logged in successfully."
    }
  ````


### Route 4: Update Password
- **Path**: `/api/update-password`
- **Request Type**: `POST`
- **Purpose**: Updates the password for a given user.
- **Request Format**:
  - `username` (String): User's username.
  - `password` (String): User's curent password.
  - 'new_password' (String): User's new chosen password.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: ```{"message": "Password 'new_password' updated successfully."}```
- **Example Request**:
  ````json
    {
      "username": "john_doe",
      "password": "securepassword",
      "new_password": "securepassword2"
    }
  ````
- **Example Response**:
  ````json
    {
      "message": "Password securepassword2 updated successfully."
    }
  ````


### Route 5: Initialize Database
- **Path**: `/api/init`
- **Request Type**: `POST`
- **Purpose**: Initializes or recreates the databases needed.
- **Request Format**:
  - No parameters required.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: ```{"status": "success", "message": "Database initialized successfully."}```
- **Example Request**:
  ```bash
  POST /api/init
  ```
- **Example Response**:
  ````json
    {
      "status": "success",
      "message": "Database initialized successfully."
    }
  ````


### Route 6: Look Up Stock
- **Path**: `/api/look-up-stock`
- **Request Type**: `GET`
- **Purpose**: Fetches information about a specific stock.
- **Request Format**:
  - `symbol` (str): The symbol of the stock to look up.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: ```{"symbol": stock_symbol, "current_price": stock.current_price, "company_name": stock.company_name, "company_description": stock.company_description, "market_cap": stock.market_cap}```
- **Example Request**:
  ````json
    {
      "symbol": "AAPL"
    }
  ````
- **Example Response**:
  ````json
    {
      "symbol": "AAPL",
      "current_price": 247.77,
      "company_name": "Apple Inc",
      "company_description": "Apple designs consumer electronics...",
      "market_cap": "2.5T"
    }
  ````


### Route 7: View Portfolio
- **Path**: `/api/view-portfolio`
- **Request Type**: `GET`
- **Purpose**: Retrieves all stocks from the user's portfolio.
- **Request Format**:
  - No parameters required.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: ```{"status": "success", "songs": stocks}```
- **Example Request**:
  ```bash
    GET /api/view-portfolio
  ```
- **Example Response**:
  ````json
    {
      "status": "success",
      "stocks": [
        {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "quantity": 10
        },
        {
          "symbol": "TSLA",
          "name": "Tesla Inc.",
          "quantity": 5
        }
      ]
    }
  ````


### Route 8: Calculate Portfolio Value
- **Path**: `/api/calculate-portfolio-value`
- **Request Type**: `GET`
- **Purpose**: Calculates the total value of the portfolio based on current stock prices.
- **Request Format**:
  - No parameters required.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: ```{"status": "success", "value": portfolio_value}```
- **Example Request**:
  ```bash
    GET /api/calculate-portfolio-value
  ```
- **Example Response**:
  ````json
    {
      "status": "success",
      "value:" 14523.50
    }
  ````


### Route 9: Buy Stock
- **Path**: `/api/buy-stock`
- **Request Type**: `POST`
- **Purpose**: Allows a user to buy a specified quantity of a stock and add it to their portfolio.
- **Request Format**:
  - `stock_symbol` (String): The stock symbol of the company.
  - `stock_name` (String): The name of the company.
  - `quantity` (int): The amount of stocks to purchase.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 201
    - Content: ```{"status": "stock purchased", "company": stock_symbol, "updated_quantity": updated_quantity}```
- **Example Request**:
  ````json
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 10
    }
  ````
- **Example Response**:
  ````json
    {
      "status": "stock purchased",
      "company": "AAPL",
      "updated_quantity": 10
    }
  ````


### Route 10: Sell Stock
- **Path**: `/api/sell-stock`
- **Request Type**: `DELETE`
- **Purpose**: Allows a user to sell a specified quantity of a stock from their portfolio.
- **Request Format**:
  - `symbol` (String): The symbol of the stock to sell.
  - `quantity` (int): The quantity of shares to sell.
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 201
    - Content: ```{"status": "stock sold", "company": symbol, "updated_quantity": updated_quantity}```
- **Example Request**:
  ````json
    {
      "symbol": "AAPL",
      "quantity": 5
    }
  ````
- **Example Response**:
  ````json
    {
      "status": "stock sold",
      "company": "AAPL",
      "updated_quantity": 3
    }
  ````
  
