import os
import json
import csv
import datetime
from dateutil.parser import parse
from Dependencies.Class_Fund import ListOfFunds

global InvestmentFile_BuyDate
global InvestmentFile_Money

InvestmentFile_BuyDate = "BuyDate"
InvestmentFile_Money = "Money"


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
            
    def saveInvestmentHistoryDayByDay(self):
        for item in self.Wallets:
            self.Wallets[item].saveInvestmentHistoryDayByDay(item)

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
        
        startDate = datetime.datetime(1900,1,9)
        for fund in self.Investment:
            if startDate < parse(self.Investment[fund][InvestmentFile_BuyDate]):
                startDate = parse(self.Investment[fund][InvestmentFile_BuyDate])
                
            buyPrice = self.FundsQuotations[fund].getFundPriceOnDate(self.Investment[fund][InvestmentFile_BuyDate])
            self.InvestedMoney += float(self.Investment[fund][InvestmentFile_Money])
            self.Investment[fund]["ParticipationUnits"] = float(self.Investment[fund][InvestmentFile_Money]) / buyPrice
            self.Investment[fund]["TodaysValue"] = self.Investment[fund]["ParticipationUnits"] * self.FundsQuotations[fund].getPrice()
            self.TodaysValue += self.Investment[fund]["TodaysValue"]
            self.Investment[fund]["RefundRate"] =  (self.Investment[fund]["TodaysValue"] / float(self.Investment[fund][InvestmentFile_Money]))
            self.profit += self.Investment[fund]["TodaysValue"] - float(self.Investment[fund][InvestmentFile_Money])
            
        self.refundRate = ((self.TodaysValue / self.InvestedMoney) - 1) * 100
        self.investmentDurationDays = (datetime.datetime.now() - startDate).days

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
    
    def saveInvestmentHistoryDayByDay(self, investmentName):

        currentDate = datetime.datetime(2100,1,1)
        fileName = ""
        for fund in self.Investment:
            if currentDate > parse(self.Investment[fund][InvestmentFile_BuyDate]):
                currentDate = parse(self.Investment[fund][InvestmentFile_BuyDate])
                
            if self.Investment[fund]["ParticipationUnits"] == None:
                buyPrice = self.FundsQuotations[fund].getFundPriceOnDate(self.Investment[fund][InvestmentFile_BuyDate])
                self.Investment[fund]["ParticipationUnits"] = float(self.Investment[fund][InvestmentFile_Money]) / buyPrice
            fileName += f"{self.FundsQuotations[fund].getFundID()}_"
        
        with open(f"{investmentName}_{fileName[:-1]}.csv", "w") as investHistory:
            writer = csv.writer(investHistory, delimiter='\t')
            writer.writerow(["Date","Value", "Funds"])
            
            while currentDate.date() <=  datetime.date.today():
                currentValue = 0.0
                fundsBought = ""
                for fund in self.Investment:
                    if currentDate.date() >= parse(self.Investment[fund][InvestmentFile_BuyDate]).date():
                        fundsBought += f"{fund},"
                        try:
                            units = self.Investment[fund]["ParticipationUnits"]
                            price = self.FundsQuotations[fund].getFundPriceOnDate(currentDate.strftime("%Y-%m-%d"))
                            currentValue += units * price
                        except:
                            break
                    else:
                        currentValue += float(self.Investment[fund][InvestmentFile_Money]) 
                else:
                    writer.writerow(
                            [
                                f"{currentDate.strftime("%Y-%m-%d")}",
                                round(currentValue, 2),
                                fundsBought[:-1]
                            ]
                        )
                
                currentDate += datetime.timedelta(days=1)