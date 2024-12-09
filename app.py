
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
# from flask_cors import CORS

from config import ProductionConfig
from stock_model.db import db
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
        Route to log in a user and load their portfolio.

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

            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Load user's combatants into the battle model
            login_user(user_id, portfolio_model)

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

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

    @app.route('/api/buy-stock', methods=['POST'])
    def buy_stock() -> Response:
        """
        Route to buy a new stock to the database.

        Expected JSON Input:
            # the below must be changed
            # - meal (str): The name of the combatant (meal).
            # - cuisine (str): The cuisine type of the combatant (e.g., Italian, Chinese).
            # - price (float): The price of the combatant.
            # - difficulty (str): The preparation difficulty (HIGH, MED, LOW).

        Returns:
            JSON response indicating the success of the stock purchase.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the stock purchase to the database.
        """
        
    @app.route('/api/sell-stock/<int:stock_id>', methods=['DELETE'])
    def sell_stock(stock_id: int) -> Response:
        """
        Route to delete a stock by its ID. This performs a soft delete by marking it as deleted.

        Path Parameter:
            - stock_id (int): The ID of the stock to delete.

        Returns:
            JSON response indicating success of the operation or error message.
        """

    @app.route('/api/look-up-stock', methods=['GET'])
    def look_up_stock(stock_symbol: str):
        """
        Route to look up specific information about a stock.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.

        Returns:
            JSON response indicating the success of the stock look-up.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue looking up the stock.
        """

    
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
        """

    @app.route('/api/calculate-portfolio-value', methods=['POST'])
    def calculate_portfoliio_value() -> Response:
        """
        Route to calculate the portfolio value.

        Returns:
            JSON response indicating the total value of the portfolio.
        Raises:
            500 error if there is an issue calculating the porfolio.
        """




if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
