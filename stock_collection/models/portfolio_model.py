import logging
from typing import List, Dict, Any
import requests
from stock_collection.models.stock_model import Stock
from stock_collection.utils.logger import configure_logger
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
configure_logger(logger)

class PortfolioModel:
    """
    A class to manage a portfolio of stocks.

    Attributes:
        stock_list (Dict[Stock]): A dictionary of stocks in the portfolio. (Key: Stock Symbol, Value: Stock Object)

    """

    def __init__(self):
        """
        Initializes the PortfolioModel with an empty portfolio.
        """
        self.stock_list: Dict[str, Stock] = {} # Key: Stock Symbol, Value: Stock Object

    def get_current_price(self) -> float:
        """
        Fetches the current stock price from Alpha Vantage API.

        Returns:
            float: the current price of the stock.
        
        """
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')  # Replace with your actual API key
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': self.symbol,
            'interval': '5min',
            'apikey': api_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()

            # Check if data contains 'Time Series (5min)'
            if "Time Series (5min)" in data:
                latest_data = data["Time Series (5min)"]
                latest_close = list(latest_data.values())[0]["4. close"]
                return float(latest_close)
            else:
                logger.error(f"Error fetching data for {self.symbol}. Response: {data}")
                return 0.0
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to API for {self.symbol}: {e}")
            return 0.0

    
    def view_portfolio(self) -> None:
        """
        Displays the user's current stock holdings, including quantity, the current price of
        each stock, and the total value of each holding, culminating in an overall portfolio
        value.
        """
        if not self.stock_list:
            logger.info("Portfolio is empty. No stocks to display.")
            print("Your portfolio is empty.")
            return
        
        total_value = 0.0
        logger.info("Displaying portfolio details:")

        print("\nPortfolio Details:")
        print("-------------------------------------------------")
        for stock_symbol, stock in self.stock_list.items():
            stock_value = stock.quantity * stock.current_price
            total_value += stock_value

            logger.debug(f"Stock: {stock.name} ({stock.symbol})")
            logger.debug(f"Quantity: {stock.quantity}")
            logger.debug(f"Current Price: ${stock.current_price}")
            logger.debug(f"Total Value: ${stock_value:.2f}")

            print(f"Stock: {stock.name} ({stock.symbol})")
            print(f"Quantity: {stock.quantity}")
            print(f"Current Price: ${stock.current_price}")
            print(f"Total Value: ${stock_value:.2f}")
            print("-------------------------------------------------")
        
        logger.info(f"Total Portfolio Value: ${total_value:.2f}")
        print(f"\nTotal Portfolio Value: ${total_value:.2f}")
        print("-------------------------------------------------")


    def calculate_portfolio_value(self) -> float:
        """
        Calculates the total value of the user's investment portfolio in real-time, reflecting
        the latest stock prices. This helps users understand the current worth of their 
        investments. 

        Returns:
            float: the total value of the portfolio
        """
        total_value = 0.0
        logger.info("Calculating total portfolio value:")

        for stock_symbol, stock in self.stock_list.items():
            stock_value = stock.quantity * stock.current_price
            total_value += stock_value

            logger.debug(f"Stock: {stock.name} ({stock.symbol})")
            logger.debug(f"  Quantity: {stock.quantity}, Current Price: ${stock.current_price}")
            logger.debug(f"  Stock Value: ${stock_value:.2f}")
            
        logger.info(f"Total Portfolio Value: ${total_value:.2f}")
        return total_value


    def buy_stock(self, stock_symbol: str, stock_name: str, quantity: int) -> int:
        """
        Enables users to purchase shares of a specified stock.

        Args:
            stock_symbol (str): The stock symbol of the company.
            stock_name (str): The name of the company stock.
            quantity (int): An integer representing the quantity of the stock the user wants to purchase. 

        Returns:
            int: The updated quantity of the stock in the portfolio after the purchase.

        Raises:
            ValueError: If the amount of stock to be bought is 0 or in the negatie
        """
        if quantity <= 0:
            logger.error("Quantity must be a positive integer to add or buy stock.")
            raise ValueError("Quantity must be a positive integer to add or buy stock.")
            
        
        # Check if the stock already exists in the portfolio
        existing_stock = self.stock_list.get(stock_symbol)

        if existing_stock:
            # Stock exists in portfolio, update the quantity
            existing_stock.buy(quantity)
            logger.info(f"Added {quantity} more shares of {stock_symbol} to portfolio. New quantity: {existing_stock.quantity}")
            return existing_stock.quantity
        else:
            # Stock does not exist, create a new stock object and add it
            current_price = self.get_current_price(stock_symbol)
            if current_price > 0:
                new_stock = Stock(symbol=stock_symbol, name=stock_name, quantity=quantity, current_price=current_price)
                self.stock_list[stock_symbol] = new_stock
                logger.info(f"Added {quantity} shares of {stock_symbol} to portfolio at price ${current_price}.")
                return new_stock.quantity
            else:
                logger.error(f"Failed to retrieve current price for {stock_symbol}, cannot add stock.")
                return -1



    def sell_stock(self, stock_symbol: str, quantity: int) -> int:
        """
        Allows users to sell shares of a stock they currently hold.

        Args:
            stock_symbol (str): The symbol of the stock to sell/remove.
            quantity (int): An integer representing the quantity of the stock the user wants to sell.

        Returns:
            int: An integer representing the current quantity of the stock the user holds.
        
        Raises:
            ValueError: If the amount of stock to be sold is 0 or in the negatie
            KeyError: If the stock is not found in portfolio
            ValueError: If the amount of stock being sold is greater than the amount bought
        """
        if quantity <= 0:
            logger.error("Quantity must be a positive integer to sell stock.")
            raise ValueError("Quantity must be a positive integer to sell stock.")  # Return an invalid quantity to indicate failure
        
        stock = self.stock_list.get(stock_symbol)

        if not stock:
            logger.warning(f"Stock {stock_symbol} is not in the portfolio.")
            raise KeyError (f"Stock {stock_symbol} is not in the portfolio.")
        
        if stock.quantity < quantity:
            logger.error(f"Not enough shares of {stock_symbol} to sell. You have {stock.quantity} shares.")
            raise ValueError(f"Not enough shares of {stock_symbol} to sell. You have {stock.quantity} shares.")  
        # Sell the stock
        stock.sell(quantity)

        # If the stock quantity becomes 0, remove the stock from the portfolio
        if stock.quantity == 0:
            del self.stock_list[stock_symbol]
            logger.info(f"Removed {stock_symbol} from portfolio after selling all shares.")
        else:
            logger.info(f"Sold {quantity} shares of {stock_symbol}. Remaining quantity: {stock.quantity}")

        # Return the updated quantity of the stock
        return stock.quantity
