import os
import json
from datetime import datetime
from dateutil.parser import parse
from Dependencies.Class_Fund import ListOfFunds

date_format = "%Y-%d-%m"

class InvestmentWallet:
    def __init__(self, InvestmentsFilePath, FundsList):
        if not isinstance(InvestmentsFilePath, str):
            raise Exception("InvestmentsFilePath must be a string")
        
        if not os.path.isfile(InvestmentsFilePath):
            raise Exception("Investments file does not exist")
        
        if not type(FundsList) == ListOfFunds:
            raise Exception("Funds must be an instance of a class ListOfFunds")
        
        with open(InvestmentsFilePath, "r") as Invest:
            investments = json.loads(str("\n".join(Invest.readlines())))
        
        self.Wallets = {}
        
        for item in investments:
            self.Wallets[item] = RefundRate(investments[item], FundsList)
            
    def calculateRefundDetails(self):
        for item in self.Wallets:
            self.Wallets[item].calculateRefundDetails()
    
    def printInvestmentResults(self):
        for item in self.Wallets:
            results = self.Wallets[item].getResult()
            print(f"\n{item}:")
            print(f"   profit: {results["Profit"]}")
            print(f"   refund rate: {results["RefundRate"]}")
            print(f"   timeframe: {self.Wallets[item].getInvestmentDurationDays()} days")

class RefundRate:
    def __init__(self, Investment, FundsList):

        if not type(Investment) == dict:
            raise Exception("Investment must be a dictionary")
        
        self.Investment = Investment
        self.Currency = ""
        self.FundsQuotations = {}
        
        currencySet = set()
        
        for fund in Investment:
            self.FundsQuotations[fund] = FundsList.getFundByID(fund)
            currencySet.add(self.FundsQuotations[fund].getCurrency())

        self.Currency = currencySet.pop()
        while len(currencySet):
            self.Currency += " / " + currencySet.pop()

    def calculateRefundDetails(self):
        self.profit = 0.0
        self.InvestedMoney = 0.0
        self.TodaysValue = 0.0
        
        startDate = datetime(1900,1,9)
        for fund in self.Investment:
            if startDate < parse(self.Investment[fund]["BuyDate"]):
                startDate = parse(self.Investment[fund]["BuyDate"])
                
            buyPrice = self.FundsQuotations[fund].getFundPriceOnDate(self.Investment[fund]["BuyDate"])
            self.InvestedMoney += float(self.Investment[fund]["Money"])
            self.Investment[fund]["ParticipationUnits"] = float(self.Investment[fund]["Money"]) / buyPrice
            self.Investment[fund]["TodaysValue"] = self.Investment[fund]["ParticipationUnits"] * self.FundsQuotations[fund].getPrice()
            self.TodaysValue += self.Investment[fund]["TodaysValue"]
            self.Investment[fund]["RefundRate"] =  (self.Investment[fund]["TodaysValue"] / float(self.Investment[fund]["Money"]))
            self.profit += self.Investment[fund]["TodaysValue"] - float(self.Investment[fund]["Money"])
            
        self.refundRate = ((self.TodaysValue / self.InvestedMoney) - 1) * 100
        self.investmentDurationDays = (datetime.now() - startDate).days

    def getProfit(self):
        return round(self.profit, 2)
    
    def getRefundRate(self):
        return round(self.refundRate, 4)
    
    def getInvestmentDurationDays(self):
        return self.investmentDurationDays
    
    def getResult(self):
        result = {}
        profit = self.getProfit()
        if profit > 0:
            sign = "+"
        else:
            sign = "-"
        result["Profit"] = f"{sign}{str(profit)} {self.Currency}"
        
        refund = self.getRefundRate()
        if refund > 0:
            sign = "+"
        else:
            sign = "-"
            
        result["RefundRate"] = f"{sign}{str(refund)} %"
        
        return result
    
    def saveInvestmentHistoryDayByDay(self, destinationFilePath):
        