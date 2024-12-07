from dataclasses import dataclass
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Stock:
    name: str
    symbol : str
    cur_price : float
    his_price : List[float]
    description: str
    activity : boolean
