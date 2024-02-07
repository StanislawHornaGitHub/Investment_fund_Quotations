"""
.DESCRIPTION
    Definition file of investment class. 
    Class is data structure to store and calculate results of a single investment.
    Investment is agreed to be a set of Investment funds, where each of have following properties:
        - Fund ID <- ID from Analizy.pl website
        - BuyDate <- date when particular fund was bought
        - Money <- amount of money used to by fund's participation units
        
    To have the class to function correctly you need to pass an instance of ListOfFunds
    to class constructor.
    
.INITIALIZATION
    To create an instance of this class you need to use keywords.
    By default class was meant to be a attribute of InvestmentWallet class
    Keywords for required variables:
        -InvestmentDetails <- dict structure in following format:
                {
                    <Fund_ID_1> : {
                        "BuyDate": "<yyyy-MM-dd>",
                        "Money": "<int_or_float>"
                    },
                    <Fund_ID_2> : {
                        "BuyDate": "<yyyy-MM-dd>",
                        "Money": "<int_or_float>"
                    }
                }
        
        - FundsList <- an instance of ListOfFunds with already downloaded data from web

.NOTES

    Version:            1.0
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      07-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
# Official and 3-rd party imports
import csv
import datetime
from dateutil.parser import parse
from dataclasses import dataclass, field

# Custom created function modules
from Dependencies.Variable_InvestmentFile import *

# Custom created class modules
from Dependencies.Class_ListOfFund import ListOfFunds
from Dependencies.Class_AnalizyFund import AnalizyFund

@dataclass(kw_only=True)
class Investment:
    
    # Initialization Variables
    InvestmentDetails: dict[str, dict[str, float | str]]
    FundsList: ListOfFunds
    
    # Calculated Variables
    Currency: str = field(default_factory=str,init=False)
    FundsQuotations: dict[str, AnalizyFund] = field(default_factory=dict, init=False)
    Profit: float = field(default_factory=float, init=False)
    InvestedMoney: float = field(default_factory=float, init=False)
    TodaysValue: float = field(default_factory=float, init=False)
    InvestmentDetailsDurationDays: int = field(init=False)
    
    def __post_init__(self):
        currencySet = set()
        
        # Loop through selected funds, assign them to the class variable `FundsQuotations`, add fund currency to the set
        for fund in self.InvestmentDetails:
            self.FundsQuotations[fund] = self.FundsList.getFundByID(fund)
            currencySet.add(self.FundsQuotations[fund].getCurrency())

        # append currency string with the last set item
        self.Currency = currencySet.pop()
        # loop while currency set is not empty and add each currency
        while len(currencySet):
            self.Currency += " / " + currencySet.pop()
        
        return None

    def calcRefundDetails(self):
        # Init local variable for searching start date with all capital
        startDate = datetime.datetime(1900,1,9)
        for fund in self.InvestmentDetails:
            
            # check if current fund's date is after recently assigned one, if yes assign the "younger" one
            if startDate < parse(self.InvestmentDetails[fund][InvestmentFile_BuyDate]):
                startDate = parse(self.InvestmentDetails[fund][InvestmentFile_BuyDate])
            
            # Calculate Fund's participation units
            self.InvestmentDetails[fund]["ParticipationUnits"] = (
                    # Money invested in current fund
                float(self.InvestmentDetails[fund][InvestmentFile_Money]) 
                    # Divide by
                /   
                    # Fund price on a buy date
                (self.FundsQuotations[fund].getFundPriceOnDate(self.InvestmentDetails[fund][InvestmentFile_BuyDate]))
                )
            
            # Calculate Today's value of bought participation units
            self.InvestmentDetails[fund]["TodaysValue"] = (
                    # Number of bought participation units
                self.InvestmentDetails[fund]["ParticipationUnits"]
                    # Multiplied by
                * 
                    # Today's Fund price
                self.FundsQuotations[fund].getPrice()
                )
            
            # Calculate Refund Rate based on whole investment period
            self.InvestmentDetails[fund]["RefundRate"] =  (
                (   # Divide Today's value of bought participation units
                    (
                            # Today's investment value
                        self.InvestmentDetails[fund]["TodaysValue"]
                            # Divide by 
                        / 
                            # Invested money at the beginning
                        float(self.InvestmentDetails[fund][InvestmentFile_Money])
                    )
                # Subtract 1 from fraction to get only profit or loss
                - 1)
                # Multiply by 100 to present value as %
                * 100)
            
            # Add value of today's Fund value to calculate today's value of investment
            self.TodaysValue += self.InvestmentDetails[fund]["TodaysValue"]
            # Add value of invested money in current Fund to calculate amount of invested money
            self.InvestedMoney += float(self.InvestmentDetails[fund][InvestmentFile_Money])
        
        # Calculate overall profit of investment
        self.Profit = (self.TodaysValue - self.InvestedMoney)
        # Calculate overall refund rate of investment
        self.refundRate = ((self.TodaysValue / self.InvestedMoney) - 1) * 100
        # Calculate investment duration in days
        self.InvestmentDetailsDurationDays = (datetime.datetime.now() - startDate).days
        return None

    def getProfit(self) -> float:
        return round(self.Profit, 2)
    
    def getRefundRate(self) -> float:
        return round(self.refundRate, 4)
    
    def getInvestmentDurationDays(self) -> int:
        return self.InvestmentDetailsDurationDays
    
    def getResult(self, name: str) -> list[dict]:
        # Init local temp variables
        resultList = []
        profit = self.getProfit()
        refund = self.getRefundRate()
        timeFrame = self.getInvestmentDurationDays()
        
        # Append result list with stats of complete investment
        resultList.append(
            {
                "Investment Name": name,
                "Profit": profit,
                "Refund Rate": refund,
                "Days": timeFrame,
                "Profit per day": (profit / timeFrame),
                "Refund per day": (refund / timeFrame),
                "Fund ID": "-",
                "Investment %": "-",
                "Fund profit": "-",
                "Fund refund %": "-",
                "Last Change %": "-"
            }
        )
        
        # Loop through funds bought in investment
        for fund in self.InvestmentDetails:
            # Divide Today's fund value by invested money and multiply by 100 to receive %
            percentageOfInvestment = ((self.InvestmentDetails[fund]["TodaysValue"] / self.InvestedMoney) * 100)
            # Subtract money invested at the beginning from Today's value 
            fundProfit = (self.InvestmentDetails[fund]["TodaysValue"] - float(self.InvestmentDetails[fund][InvestmentFile_Money]))
            # Append result list with details about each bought fund
            resultList.append(
                {
                    "Investment Name": "-",
                    "Profit": "-",
                    "Refund Rate": "-",
                    "Days": "-",
                    "Profit per day": "-",
                    "Refund per day": "-",
                    "Fund ID": fund,
                    "Investment %": percentageOfInvestment,
                    "Fund profit": fundProfit,
                    "Fund refund %": self.InvestmentDetails[fund]["RefundRate"],
                    "Last Change %": self.FundsQuotations[fund].getLastChangePercentage()
                }
            )
        return resultList

    def saveInvestmentHistoryDayByDay(self, investmentName, destinationPath=None):
        # Init local variable to look for oldest buy date
        currentDate = datetime.datetime(2100,1,1)
        # Loop through each Fund
        for fund in self.InvestmentDetails:
            # Check if current fund's buy date is older than recently assigned, if yes assign "older" one
            if currentDate > parse(self.InvestmentDetails[fund][InvestmentFile_BuyDate]):
                currentDate = parse(self.InvestmentDetails[fund][InvestmentFile_BuyDate])
            
            # Check if Participation Units have been calculated if not calculate it.
            if self.InvestmentDetails[fund]["ParticipationUnits"] == None:
                # Calculate Fund's participation units
                self.InvestmentDetails[fund]["ParticipationUnits"] = (
                        # Money invested in current fund
                    float(self.InvestmentDetails[fund][InvestmentFile_Money]) 
                        # Divide by
                    /   
                        # Fund price on a buy date
                    (self.FundsQuotations[fund].getFundPriceOnDate(self.InvestmentDetails[fund][InvestmentFile_BuyDate]))
                    )
        # Check if destination Path was provided and create appropriate `destinationFilePath`
        if destinationPath == None or not destinationPath:
            destinationFilePath = f"{investmentName}.csv"
        else:
            destinationFilePath = f"{destinationPath}/{investmentName}.csv"

        # open file to write Day to day investment stats
        with open(destinationFilePath, "w") as investHistory:
            
            # Init CSV writer and write headers to the file
            writer = csv.writer(investHistory, delimiter='\t')
            writer.writerow(["Date","Value", "Funds"])
            
            # Loop until current calculation date is lower or equal to today
            while currentDate.date() <=  datetime.date.today():
                
                # Init local while loop variable
                currentValue = 0.0
                fundsBought = ""
                
                # Loop through each fund in investment
                for fund in self.InvestmentDetails:
                    
                    # If current calculation date is greater than buy date than we can perform calculations
                    if currentDate.date() >= parse(self.InvestmentDetails[fund][InvestmentFile_BuyDate]).date():
                        
                        # Append string with list of bought funds on a current calculation date
                        fundsBought += f"{fund},"
                        
                        try:
                            # try to get fund price for current calculation date
                            price = self.FundsQuotations[fund].getFundPriceOnDate(currentDate.strftime("%Y-%m-%d"))
                            units = self.InvestmentDetails[fund]["ParticipationUnits"]
                            # otherwise sum value variable with current fund's value
                            currentValue += units * price
                        except:
                            break
                    else:
                        # If If current calculation date not is greater than buy date add invested money to the value
                        currentValue += float(self.InvestmentDetails[fund][InvestmentFile_Money])
                else:
                    # if for loop was not broken write csv row to the file using initialized writer
                    writer.writerow(
                            [
                                f"{currentDate.strftime("%Y-%m-%d")}",
                                round(currentValue, 2),
                                fundsBought[:-1]
                            ]
                        )
                # Increment calculation date with +1 day
                currentDate += datetime.timedelta(days=1)
        return None
