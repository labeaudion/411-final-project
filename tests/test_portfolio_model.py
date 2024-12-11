
import pytest

from stock_collection.models.portfolio_model import PortfolioModel
from stock_collection.models.stock_model import Stock


@pytest.fixture()
def portfolio_model():
    """Fixture to provide a new instance of PortfolioModel for each test."""
    return PortfolioModel()


@pytest.fixture
def sample_stock1():
    return Stock('IBM', 'IBM Common Stock', 5, 109.2)

@pytest.fixture
def sample_stock2():
    return Stock('MBG.DEX','Mercedes Benz Group AG',4, 70.04)

def sample_stock3():
    return Stock('IBM', 'IBM Common Stock', -1, 109.2)


@pytest.fixture
def sample_portfolio(sample_song1, sample_song2):
    return [sample_song1, sample_song2]

##################################################
# Buying Stock Test Cases
##################################################
def test_buy_stock(portfolio_model, sampe_stock1):
    """Testing buying a stock """
    portfolio_model.buy_stock(sample_stock1)
    assert len(portfolio_model.portfolio) == 1
    assert list(portfolio_model.portfolio.keys())[0] ==  ["IBM"]   

def test_wrong_amt_stock_buy(portfolio_model, sample_stock3):
    """Test error when no stock or negative amount of stock is trying to be bought"""
    
    with pytest.raises(ValueError, match="Quantity must be a positive integer to add or buy stock."):
        portfolio_model.buy_stock(sample_stock3)

##################################################
# Selling Stock Test Cases
##################################################

def test_sell_stock(portfolio_model, sample_stock1):
    """Testing sellig of a stock"""
    portfolio_model.buy_stock(sample_stock1)
    portfolio_model.sell_stock('IBM', 2)
    assert len(portfolio_model.portfolio) == 1
    assert list(portfolio_model.portfolio.keys())[0] ==  ["IBM"]
    portfolio_model.sell_stock('IBM', 3)
    assert len(portfolio_model.portfolio) == 0

def test_selling_wrong_amount(portfolio_model, sample_stock1):
        """Test error when no stock or negative amount of stock is trying to be sold"""
        portfolio_model.buy_stock(sample_stock1)
        with pytest.raises(ValueError, match="Quantity must be a positive integer to add or buy stock."):
            portfolio_model.sell_stock('IBM', -2)

def test_selling_more(portfolio_model, sample_stock2):
        """Test error when selling stock amount more than currently held"""
        portfolio_model.buy_stock(sample_stock2)
        with pytest.raises(ValueError, match="Not enough shares of MBG.DEX to sell. You have 4 shares."):
            portfolio_model.sell_stock('MBG.DEX', 10)

def test_selling_wrong_stock(portfolio_model, sample_stock2):
    """Test error when selling stock not bought or not in portfolio"""
    portfolio_model.buy_stock(sample_stock2)
    with pytest.raises(KeyError, match="Stock TESLA is not in the portfolio."):
            portfolio_model.sell_stock('TESLA', 1)

##################################################
# Real-Time Stock Prices Test Cases
##################################################
def test_get_current_price(portfolio_model, sample_stock1, sample_stock2):
    "Test get_current_price to see if we are gettig price of the stocks in our portfolio"
    portfolio_model.buy_stock(sample_stock1)
    price = portfolio_model.get_current_price()
    assert type(price) == float

    portfolio_model.buy_stock(sample_stock2)
    price = portfolio_model.get_current_price()
    try: 
        assert price >= 0.00
    except ValueError:
        pytest.fail("get_current_price rased ValueError unexpectedly on portfolio value")

    