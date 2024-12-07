import logging
from typing import List
from stock_collection.models.stock_model import Stock
from stock_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class PortfolioModel:
    """
    A class to manage a portfolio of stocks.

    Attributes:
        stock_list (List[Stock]): The list of stocks in the portfolio.

    """

    def __init__(self):
        """
        Initializes the PortfolioModel with an empty porfolio.
        """
        self.stock_list: List[Stock] = []

  
    
