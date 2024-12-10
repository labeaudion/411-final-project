import logging
from typing import List
from typing import List

#from logger import configure_logger
import requests
import json
import random


#logger = logging.getLogger(__name__)
#configure_logger(logger)



def findStockbySymbol(stock):
    """
        Search a stock by keywords
    """

    url = url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock}&apikey=VHM98Q5C5SWA8W94"
    r = requests.get(url)
    text = r.json()

    json_object = json.dumps(text, indent=4)
 
    with open("sample.json", "w") as outfile:
        outfile.write(json_object)

    return text

def getStockPrice(stock):
    """
        Retrievs the "real-time" price of the stock, searches by stock's SYMBOAL!!! 
    """
    
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey=VHM98Q5C5SWA8W94"
        r = requests.get(url)
        text = r.json()

    except:
        print("The stock symbol does not exist")

    json_object = json.dumps(text, indent=4)

    with open(f"{stock}.json", "w") as outfile:
        outfile.write(json_object)

    with open(f'{stock}.json', 'r') as openfile:

        search_stock = json.load(openfile)

    try:
        for stock_price in search_stock["Time Series (Daily)"].keys():
            options = ["1. open", "2. high", "3. low", "4. close"]
            ran_option = random.choice(options)

            curr_price =  search_stock["Time Series (5min)"][stock_price][ran_option]
            return float(curr_price)
        
    except:
        raise Exception("Sorry,you have ran out of the 25 searches")
            
    
    

class StockTrade:
    def __init__(self):
        self.BuyingPower = 1000.0000
        self.curr_Portfolio = [
            '''
            each dictionary contains the infromation of a stock. E.g. 
            {
            "Stock" : "IBM", holds the stock symbol; type (str) 
            "Bought @" : 100.0, holds the value at  which the stock was bought at; type (float)
            "Amt Bought" :  2, holds the value of the amount of the stock bought; type (int)
            "Total Cost" : 200.2, holds the total cost of all the stock bought 
            "Current Price": 101.0, holds the latest value(real-time) of the stock, always gets updated by calling updatePortfolio; type (float)
            "Profit @each": 1.0, holds the value of profit of 1 stock, updates according to value of current price; type (foat)
            "Totall Profit": 2.0, holds the value of total profit of the stock, updates according to value of current price; type (float)
            }
            '''     
        ]

    def updatePortfolio(self):
        """
            Get the latest (real-time) value of the stock and updates the user's portfolio accordingly
        """
        portfolio = []

        for item in self.curr_Portfolio:
            dup_item = item
            dup_item["Total Cost"] =  dup_item["Bought @"] * dup_item["Amt Bought"]
            dup_item["Current Price"] = getStockPrice(dup_item['Stock'])
            dup_item["Profit @each"] = dup_item["Bought @"] - dup_item ["Current Price"]
            dup_item["Total Profit"] = dup_item["Profit @each"] * dup_item["Amt Bought"]
            portfolio.append(dup_item)
        
        self.curr_Portfolio = portfolio


    def Buy(self,stock, amt):
        """
            Buys the amount of stock given if it is within the user's buying power
        """
        price = getStockPrice(stock)
        
        total_cost = amt  * price
        
        if total_cost > self.BuyingPower:
            print(total_cost)
            raise Exception(f"Sorry, you currently do not have enough money in your account to buy {amt} stock of {stock}.\nYou currently have ${self.BuyingPower}, while the total cost is ${total_cost}")
        
        else:
            self.BuyingPower -= total_cost
            information =  {
                "Stock" : stock,
                "Bought @": price,
                "Amt Bought": amt
            }
            self.curr_Portfolio.append(information)
            self.updatePortfolio()

    
    def Sell(self, stock, amt):
        """
            Sells the designated amount of stock if the user has the stock and the amount of it in their portfolio.
            Additionally, deletes a stock from their portfolio if they sell all of one stock
            Updates buying power accordingly
        """
        for item in self.curr_Portfolio:
            if item["Stock"] == stock:

                holding = item["Amt Bought"]
                bought_val = item["Bought @"] 
                one_profit = item["Profit @each"]
                total_profit = item["Total Profit"]
                cur_val = item["Current Price"]
                total_price = item["Total Cost"]

                if holding >= amt:

                    self.BuyingPower += total_profit

                    if holding == amt:
                        print(f"You are sellling all the {stock} stock you own. \n Removing the stock from your protfolio...")
                        self.curr_Portfolio.remove(item)

                    print(f"You bought {stock}, at ${bought_val} each for a total price of ${total_price}.\nYou are selling ${amt} at ${cur_val}\nProfit for each is ${one_profit}, with a total profi of ${amt}")
                    return
                
                else:


                    raise Exception(f"You are trying to sell more stock than you curretly hold.\nYou hold {holding} of {stock}, but you are trying to sell {amt}")
        
        raise Exception (f"{stock} could not be found in your portfolio")
    

    def calPortolio(self):
        """
            Calculates and returns total value and profit of all the stocks the user holds 
        """
        total_value = 0
        total_profit = 0
        for stock in self.curr_Portfolio:
            total_value += stock["Current Price"]
            total_profit += stock["Total Profit"]

        return (total_value, total_profit)

    def viewPortfolio(self):
        """
            Shows the user's portfolio as well as tells the buying power, total value, and profit of all the stocks in the user's portfolio
        """
        self.updatePortfolio()
        portfolio_val,  portfolio_profit = self.calPortolio()
        information = f"You have ${self.BuyingPower} to spend.\nYou currently have ${portfolio_val} in Stocks\nYou have a total profit of ${portfolio_profit}.\nBelow is your curent portfolio:\n", self.curr_Portfolio
        return information

####################
   


#print(findStockbySymbol("dodge"))
user =StockTrade()
user.Buy("IMB",2)
print(user.viewPortfolio())
print(user.curr_Portfolio)
