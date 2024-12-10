from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized

from config import ProductionConfig
from stock_collection.db import db
from stock_collection.models.portfolio_model import PortfolioModel
from stock_collection.models.stock_model import Stock
from stock_collection.models.user_model import Users

# Load environment variables from .env file
load_dotenv()


def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    portfolio_model = PortfolioModel()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    ##########################################################
    #
    # User management
    #
    ##########################################################

    @app.route('/api/create-account', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new account.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to "log in" a user and load their portfolio.
        This only securely handles the password.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500

    @app.route('/api/update-password', methods=['POST'])
    def update_password():
        """
        Route to update a user's password.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's current password.

        Returns:
            JSON response indicating the success of the updated password.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data or 'new_password' not in data:
            app.logger.error("Invalid request payload.")
            raise BadRequest("Invalid request payload. 'username', 'password', and 'new_password' are required.")

        username = data['username']
        password = data['password']
        new_password = data['new_password']

        try:
            # Validate user's current password
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")
            
            # Update the password
            Users.update_password(username, new_password)

            app.logger.info("Password %s updated successfully.", new_password)
            return jsonify({"message": f"Password {new_password} updated successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500

    ###########################################################
    #
    # Stocks
    #
    ###########################################################

    @app.route('/api/init-db', methods=['POST'])
    def init_db():
        """
        Initialize or recreate database tables.

        This route initializes the database tables defined in the SQLAlchemy models.
        If the tables already exist, they are dropped and recreated to ensure a clean
        slate. Use this with caution as all existing data will be deleted.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.

        Logs:
            Logs the status of the database initialization process.
        """
        try:
            with app.app_context():
                app.logger.info("Dropping all existing tables.")
                db.drop_all()  # Drop all existing tables
                app.logger.info("Creating all tables from models.")
                db.create_all()  # Recreate all tables
            app.logger.info("Database initialized successfully.")
            return jsonify({"status": "success", "message": "Database initialized successfully."}), 200
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", str(e))
            return jsonify({"status": "error", "message": "Failed to initialize database."}), 500
        

    @app.route('/api/look-up-stock', methods=['GET'])
    def look_up_stock(stock_symbol: str):
        """
        Route to look up detailed information about a specific stock, including its current market
        price, historical price data, and a brief description of the company.

        Expected JSON Input:
            - symbol (str): The symbol of the stock to look up.

        Returns:
            JSON response indicating the success of the stock look-up.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue looking up the stock.
        """
        stock_symbol = request.args.get('stock_symbol', '').strip()

        if not stock_symbol:
            return jsonify({"error": "Stock symbol is required"}), 400

        # Call the model's method to fetch stock details
        stock_data = portfolio_model.look_up_stock(stock_symbol)

        # If there's an error in the response
        if "error" in stock_data:
            return jsonify({"error": stock_data["error"]}), 500

        # Return a successful response
        return jsonify({
            "symbol": stock_symbol,
            "current_price": stock_data.get("current_price"),
            "company_name": stock_data.get("company_name"),
            "company_description": stock_data.get("company_description"),
            "market_cap": stock_data.get("market_cap"),
        }), 200

    ############################################################
    #
    # Portfolio
    #
    ############################################################

    @app.route('/api/view-portfolio', methods=['GET'])
    def view_portfolio() -> Response:
        """
        Route to get the stocks from the portfolio.

        Returns:
            JSON response with the list of stocks.
        Raises:
            500 error if there is an issue retrieving the stocks from the portfolio.
        """
        try:
            app.logger.info("Retrieving all stocks from the portfolio")

            # Get all stocks from the portfolio
            stocks = portfolio_model.view_portfolio()

            return make_response(jsonify({'status': 'success', 'songs': stocks}), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving stocks from portfolio: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/calculate-portfolio-value', methods=['GET'])
    def calculate_portfolio_value() -> Response:
        """
        Route to calculate the portfolio value.

        Returns:
            JSON response indicating the total value of the portfolio.
        Raises:
            500 error if there is an issue calculating the portfolio.
        """
        try:
            app.logger.info('Calculating portfolio value')
            portfolio_value = portfolio_model.calculate_portfolio_value()
            return make_response(jsonify({'status': 'success', 'value': portfolio_value}), 200)
        except Exception as e:
            app.logger.error(f"Error calculating portfolio value: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/buy-stock', methods=['POST'])
    def buy_stock() -> Response:
        """
        Route to buy a new stock to the database.

        Expected JSON Input:
            - stock_symbol (str): The stock symbol of the company.
            - stock_name (str): The name of the company.
            - quantity (int): The amount of stocks to purchase.

        Returns:
            JSON response indicating the success of the stock purchase.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the stock purchase to the database.
        """
        app.logger.info('Buying new stock')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            stock_symbol = data.get('symbol')
            stock_name = data.get('name')
            quantity = data.get('quantity')

            if not stock_symbol or not isinstance(stock_symbol, str):
                raise BadRequest("Stock symbol is required and should be a string.")
            
            if not isinstance(quantity, int) or quantity <= 0:
                raise BadRequest("Quantity must be a positive integer.")
            
            if not stock_name or not isinstance(stock_name, str):
                raise BadRequest("Company name is required and should be a string.")
            
            # Ensure the stock exists and the operation is possible (mock behavior in this case)
            stock = Stock.query.filter_by(symbol=stock_symbol).first()
            if not stock:
                raise BadRequest(f"Stock symbol {stock_symbol} not found.")
            

            # Call the buy_stock method to update the stock
            app.logger.info('Buying stock: %s, %d', stock_symbol, quantity)
            updated_quantity = portfolio_model.buy_stock(stock_symbol, stock_name, quantity)

            if updated_quantity == -1:
                # If the return value is -1, it indicates an error in the buy operation
                return make_response(jsonify({'error': 'Failed to buy stock'}), 400)

            app.logger.info("Stock purchased: %s, %s, %d", stock_symbol, stock_name, updated_quantity)
            return make_response(jsonify({'status': 'stock purchased', 'company': stock_symbol, 'updated_quantity': updated_quantity}), 201)
        except Exception as e:
            app.logger.error("Failed to buy stock: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/sell-stock', methods=['DELETE'])
    def sell_stock() -> Response:
        """
        Route to sell a stock.

        Expected JSON Input:
            - symbol (str): The symbol of the stock to sell.
            - quantity (int): The quantity of shares to sell.

        Returns:
            JSON response indicating success of the selling or error message.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the stock selling to the database.
        """
        app.logger.info('Selling stock')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            symbol = data.get('symbol')
            quantity = data.get('quantity')

            if not symbol or not isinstance(symbol, str):
                raise BadRequest("Stock symbol is required and should be a string.")
            
            if not isinstance(quantity, int) or quantity <= 0:
                raise BadRequest("Quantity must be a positive integer.")
            
            # Ensure the stock exists in the portfolio
            stock = Stock.query.filter_by(symbol=symbol).first()
            if not stock:
                raise BadRequest(f"Stock symbol {symbol} not found in portfolio.")
            
            # Call the sell_stock method to update the stock
            app.logger.info('Selling stock: %s, %d', symbol, quantity)
            updated_quantity = portfolio_model.sell_stock(symbol, quantity)

            if updated_quantity == -1:
                # If the return value is -1, it indicates an error in the sell operation
                return make_response(jsonify({'error': 'Failed to sell stock or invalid quantity'}), 400)

            app.logger.info("Stock sold: %s, %d", symbol, updated_quantity)
            return make_response(jsonify({'status': 'stock sold', 'company': symbol, 'updated_quantity': updated_quantity}), 201)
        except Exception as e:
            app.logger.error("Failed to sell stock: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
