from dataclasses import asdict, dataclass
import logging
from typing import Any, List, Dict
import requests
from dotenv import load_dotenv
import os

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from stock_collection.db import db
from stock_collection.utils.logger import configure_logger

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Stock:
    """
    Initializes a stock object.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL").
        name (str): The name of the stock.
        quantity (int): The number of shares the user owns.
        current_price (float): The current market price of the stock.
    """
    symbol: str = db.Column(db.String(10), primary_key=True)
    name: str = db.Column(db.String(80), unique=True, nullable=False)
    quantity: int = db.Column(db.Integer, default=0)
    current_price: float = db.Column(db.Float, nullable=False)


    def get_current_price(self) -> float:
        """
        Fetch the current stock price from an external API.

        Returns:
            float: The current stock price.
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

    def look_up_stock(self) -> Dict[str, Any]:
        """
        Fetch detailed information about the stock: current price, historical data, and company description.

        Returns:
            Dict: A dictionary containing stock details (e.g., current price, historical data, description).
        """
        # First, get the current price
        current_price = self.get_current_price()

        # Fetch company description and historical data
        description = self.get_stock_description()
        historical_prices = self.get_stock_history()

        return {
            'symbol': self.symbol,
            'name': self.name,
            'current_price': current_price,
            'description': description,
            'historical_prices': historical_prices
        }

    def get_stock_history(self) -> List[Dict[str, Any]]:
        """
        Fetch the historical price data of the stock from an external API.

        Returns:
            List: A list of historical price data.
        """
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')  # Replace with your actual API key
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': self.symbol,
            'apikey': api_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "Time Series (Daily)" in data:
                historical_data = data["Time Series (Daily)"]
                return [{'date': date, 'price': details["4. close"]} for date, details in historical_data.items()]
            else:
                logger.error(f"Error fetching historical data for {self.symbol}. Response: {data}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to API for {self.symbol}: {e}")
            return []

    def get_stock_description(self) -> str:
        """
        Fetch a brief description of the company associated with the stock.

        Returns:
            str: A brief description of the company.
        """
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')  # Replace with your actual API key
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'OVERVIEW',
            'symbol': self.symbol,
            'apikey': api_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "Description" in data:
                return data["Description"]
            else:
                logger.error(f"Error fetching description for {self.symbol}. Response: {data}")
                return "No description available."
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to API for {self.symbol}: {e}")
            return "No description available."
        

    def sell(self, quantity: int) -> None:
        """
        Reduces the quantity of the stock after a sale.
        
        Args:
            quantity (int): The number of shares the user wants to sell.
        
        Raises:
            ValueError: If the quantity the user wants to sell is below or equal to 0, 
                or if the quantity the user wants to sell is too many shares to sell
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if self.quantity < quantity:
            raise ValueError(f"Not enough shares to sell. Current quantity: {self.quantity}")
        self.quantity -= quantity


    def buy(self, quantity: int) -> None:
        """
        Increases the quantity of the stock after a purchase.

        Args:
            quantity (int): The number of shares the user wants to purchase.
        
        Raises:
            ValueError: If the quantity the user wants to buy is below or equal to 0.

        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        self.quantity += quantity