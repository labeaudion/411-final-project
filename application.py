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
    url = url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock}&apikey=VHM98Q5C5SWA8W94"
    r = requests.get(url)
    text = r.json()

    json_object = json.dumps(text, indent=4)
 
    with open("sample.json", "w") as outfile:
        outfile.write(json_object)

    return text

def getStockPrice(stock):
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock}&interval=5min&apikey=VHM98Q5C5SWA8W94"
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
        for stock_price in search_stock["Time Series (5min)"].keys():
            options = ["1. open", "2. high", "3. low", "4. close"]
            ran_option = random.choice(options)

            curr_price =  search_stock["Time Series (5min)"][stock_price][ran_option]
            return float(curr_price)
        
    except:
        raise Exception("Sorry,you have ran out of the 25 searches")
            
    
    

class StockTrade:
    def __init__(self):
        """
        s
        """
        self.BuyingPower = 1000.0000
        self.curr_Portfolio = [
            #{
            #"Stock" : , 
            #"Bought @" : , 
            #"Amt Bought" :  ,
            #}
        ]

    def updatePortfolio(self):
        portfolio = []

        for item in self.curr_Portfolio:
            dup_item = item
            dup_item["Current Price"] = getStockPrice(dup_item['Stock'])
            dup_item["Total Cost"] =  dup_item["Bought @"] * dup_item["Amt Bought"]
            dup_item["Profit @each"] = dup_item["Bought @"] - dup_item ["Current Price"]
            dup_item["Total Profit"] = dup_item["Profit @each"] * dup_item["Amt Bought"]
            portfolio.append(dup_item)
        
        self.curr_Portfolio = portfolio


    def Buy(self,stock, amt):
        try:
            price = getStockPrice(stock)
        except:
            raise Exception("Sorry, the stock does not exist")
        
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
        self.updatePortfolio()
        portfolio_val,  portfolio_profit = self.calPortolio()
        information = f"You currently have ${portfolio_val} in Stocks\nYou have a total profit of ${portfolio_profit}.\nBelow is your curent portfolio:\n", self.curr_Portfolio
        return information

####################
   


#print(findStockbySymbol("dodge"))
user =StockTrade()
user.Buy("IMB",2)
print(user.viewPortfolio())
print(user.curr_Portfolio)
