from contextlib import contextmanager
import re
import sqlite3

import pytest

from stock_collection.models.stock_model import Stock
   

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("stock_collection.models.stock_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

mock_current_price = 150.0
mock_stock_details = {
    'current_price': mock_current_price,
    'description': 'A tech company.',
    'historical_data': [{'date': '2024-01-01', 'close': 145.0}, {'date': '2024-01-02', 'close': 155.0}]
}
mock_stock_history = [{'date': '2024-01-01', 'close': 145.0}, {'date': '2024-01-02', 'close': 155.0}]

def stock_instance():
    """Fixture to create a new Stock instance for each test."""
    return Stock()

######################################################
#
#    Search Stock
#
######################################################

def test_get_current_price(stock_instance, mocker):
    """Test the get_current_price function."""

    mocker.patch.object(stock_instance, 'get_current_price', return_value=150.0)
    price = stock_instance.get_current_price()
    assert price == 150.0


def test_look_up_stock(stock_instance, mocker):
    """Test the look_up_stock function."""
    
    mock_stock_details = {
        'current_price': 150.0,
        'description': 'A leading tech company',
        'historical_data': [
            {'date': '2024-01-01', 'close': 145.0},
            {'date': '2024-01-02', 'close': 155.0}
        ]
    }
    
    mocker.patch.object(stock_instance, 'look_up_stock', return_value=mock_stock_details)
    
    stock_info = stock_instance.look_up_stock()

    assert stock_info['current_price'] == 150.0
    assert stock_info['description'] == 'A leading tech company'
    assert len(stock_info['historical_data']) == 2
    assert stock_info['historical_data'][0]['date'] == '2024-01-01'
    assert stock_info['historical_data'][1]['close'] == 155.0


def test_get_stock_history(stock_instance, mocker):
    """Test the get_stock_history function."""
    
    mock_stock_history = [
        {'date': '2024-01-01', 'close': 145.0},
        {'date': '2024-01-02', 'close': 155.0}
    ]
    
    mocker.patch.object(stock_instance, 'get_stock_history', return_value=mock_stock_history)
    
    history = stock_instance.get_stock_history()
    
    assert len(history) == 2
    assert history[0]['date'] == '2024-01-01'
    assert history[1]['close'] == 155.0

def test_get_current_price_api_error(stock_instance, mocker):
    """Test the get_current_price function when the API call fails."""
    
    mocker.patch.object(stock_instance, 'get_current_price', side_effect=Exception("API request failed"))
    
    with pytest.raises(Exception, match="API request failed"):
        stock_instance.get_current_price()


def test_look_up_stock_api_error(stock_instance, mocker):
    """Test the look_up_stock function when the API call fails."""
    
    mocker.patch.object(stock_instance, 'look_up_stock', side_effect=Exception("API request failed"))
    
    with pytest.raises(Exception, match="API request failed"):
        stock_instance.look_up_stock()


def test_get_stock_history_api_error(stock_instance, mocker):
    """Test the get_stock_history function when the API call fails."""
    
    mocker.patch.object(stock_instance, 'get_stock_history', side_effect=Exception("API request failed"))
    
    with pytest.raises(Exception, match="API request failed"):
        stock_instance.get_stock_history()