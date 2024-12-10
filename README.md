# CS411 Final Project

## Application Description

The application can only make 25 API calls a day for free, so it was hard to perform extensive testing.

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
    - Code: 200
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



### Route 4: Update Password



### Route 5: Initialize Database



### Route 6: Look Up Stock



### Route 7: View Portfolio



### Route 8: Calculate Portfolio Value



### Route 9: Buy Stock



### Route 10: Sell Stock
