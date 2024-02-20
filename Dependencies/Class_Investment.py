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
        - StartDate <- start date of investment to calculate correctly duration, profit, refund per day
        - EndDate <- end date of investment to correctly duration, profit, refund per day and
                        stop calculating the bought participation units value.
        - FundsList <- an instance of ListOfFunds with already downloaded data from web

.NOTES

    Version:            1.3
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      07-Feb-2024
    ChangeLog:

    Date            Who                     What
    2024-02-16      Stanislaw Horna         Functionality to handle multiple orders of the same Fund added.
                                            InvestmentDetails structure has changed.
                                            Bugfix - Doubled data in InvestmentDayByDay CSV
                                            Handling for sold funds as archive information.
    2024-02-20      Stanisław Horna         Refactored investment refund table

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
    StartDate: datetime.date
    EndDate: datetime.date
    FundsList: ListOfFunds
    
    # Calculated Variables
    Currency: str = field(
        init=False,
        default_factory=str
    )
    FundsQuotations: dict[str, AnalizyFund] = field(
        default_factory=dict, init=False)
    Profit: float = field(
        init=False,
        default_factory=float
    )
    InvestedMoney: float = field(
        init=False,
        default_factory=float
    )
    TodaysValue: float = field(
        init=False,
        default_factory=float
    )
    Results: dict[str, dict[str, float | str]] = field(
        init=False,
        default_factory=dict
    )
    DayByDay: list[dict[str, float | str]] = field(
        init=False,
        default_factory=list
    )
    InvestmentDetailsDurationDays: int = field(
        init=False
    )

    # Constant Variables
    EndDateNotSet = datetime.datetime(2200, 1, 1).date()
    PrefixForSoldFunds = "(Arch.)"
    
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

        self.calcInvestmentDuration()
        self.calcInvestmentDayByDay()
        self.calcRefundDetails()
        return None

    def calcRefundDetails(self):
        for fund in self.InvestmentDetails:
            self.Results[fund] = {}
            self.Results[fund]["ParticipationUnits"] = (
                self.DayByDay[-1][f"{fund} P.U."]
            )
            self.Results[fund]["InvestedMoney"] = (
                self.DayByDay[-1][f"{fund} Invested Money"]
            )
            self.Results[fund]["TodaysValue"] = (
                self.DayByDay[-1][f"{fund} Value"]
            )
            self.Results[fund]["RefundRate"] = (
                self.DayByDay[-1][f"{fund} Refund"] * 100
            )

            # Add value of today's Fund value to calculate today's value of investment
            self.TodaysValue += self.Results[fund]["TodaysValue"]
            # Add value of invested money in current Fund to calculate amount of invested money
            self.InvestedMoney += self.Results[fund]["InvestedMoney"]

        # Calculate overall profit of investment
        self.Profit = (self.TodaysValue - self.InvestedMoney)
        # Calculate overall refund rate of investment
        self.refundRate = ((self.TodaysValue / self.InvestedMoney) - 1) * 100
        return None
    
    def isEndDateSet(self)-> bool:
        if self.EndDate != Investment.EndDateNotSet:
            return True
        return False

    def getProfit(self) -> float:
        return round(self.Profit, 2)

    def getRefundRate(self) -> float:
        return round(self.refundRate, 4)

    def getInvestmentDurationDays(self) -> int:
        return self.InvestmentDetailsDurationDays

    def getResult(self, name: str) -> list[dict[str, float | str]]:

        # Init local temp variables
        resultList = []
        profit = self.getProfit()
        refund = self.getRefundRate()
        timeFrame = self.getInvestmentDurationDays()
        blankSpaceString = ""
        prefixForArchived = ""
        
        if self.isEndDateSet():
            prefixForArchived = Investment.PrefixForSoldFunds
        
        # Append result list with stats of complete investment
        resultList.append(
            {
                "Investment Name": f"{prefixForArchived} {name}",
                "Days": timeFrame,
                "Fund ID": blankSpaceString,
                "Investment %": blankSpaceString,
                "Profit": profit,
                "Refund Rate": refund,
                "Profit daily": (profit / timeFrame),
                "Refund daily": (refund / timeFrame),
                "Refund yearly": (refund / timeFrame) * 365,
            }
        )
        # If end date is set do not display fund details
        if self.isEndDateSet():
            return resultList
            
        # Loop through funds bought in investment
        for fund in self.InvestmentDetails:
            # Divide Today's fund value by invested money and multiply by 100 to receive %
            percentageOfInvestment = (
                (self.Results[fund]["TodaysValue"] / (self.InvestedMoney + profit)) * 100)
            # Subtract money invested at the beginning from Today's value
            fundProfit = (
                self.Results[fund]["TodaysValue"] - self.Results[fund]["InvestedMoney"])
            
            # Append result list with details about each bought fund
            resultList.append(
                {
                    "Investment Name": blankSpaceString,
                    "Days": blankSpaceString,
                    "Fund ID": fund,
                    "Investment %": percentageOfInvestment,
                    "Profit": fundProfit,
                    "Refund Rate":self.Results[fund]["RefundRate"],
                    "Profit daily": fundProfit / timeFrame,
                    "Refund daily": self.Results[fund]["RefundRate"] / timeFrame,
                    "Refund yearly": (self.Results[fund]["RefundRate"] / timeFrame) * 365,
                }
            )
        return resultList

    def initFundsOperationsByDate(self) -> dict[datetime.datetime, dict[str, dict[str, float]]]:
        ordersByDate = {}
        for fund in self.InvestmentDetails:
            for i in range(0, len(self.InvestmentDetails[fund])):

                currentDate = parse(
                    self.InvestmentDetails[fund][i]["BuyDate"]
                ).date()

                if currentDate not in list(ordersByDate.keys()):
                    ordersByDate[currentDate] = {}

                ordersByDate[currentDate][fund] = {}
                ordersByDate[currentDate][fund]["Money"] = self.InvestmentDetails[fund][i]["Money"]
                ordersByDate[currentDate][fund]["ParticipationUnits"] = (
                    self.InvestmentDetails[fund][i]["Money"] /
                    self.FundsQuotations[fund].getFundPriceOnDate(
                        currentDate.strftime("%Y-%m-%d")
                    )
                )

        return ordersByDate

    def initFundsCumulatively(self) -> dict[str, dict[str, float]]:
        fundsCumulatively = {}
        for fund in self.InvestmentDetails:
            fundsCumulatively[fund] = {}
            fundsCumulatively[fund]["ParticipationUnits"] = 0.0
            fundsCumulatively[fund]["Money"] = 0.0

        return fundsCumulatively

    def appendFundsCumulatively(
        self,
        currentDate: datetime.datetime,
        fundsCumulatively: dict[str,
                                dict[str, float]],
        fundsOperationsByDate: dict[datetime.datetime,
                                    dict[str,
                                         dict[str, float]]]
    ) -> dict[str, dict[str, float]]:
        for fund in fundsOperationsByDate[currentDate]:
            fundsCumulatively[fund]["ParticipationUnits"] += fundsOperationsByDate[currentDate][fund]["ParticipationUnits"]
            fundsCumulatively[fund]["Money"] += fundsOperationsByDate[currentDate][fund]["Money"]

        return fundsCumulatively

    def getOutputForCurrentDay(
        self,
        currentDate: datetime.datetime,
        currentInvestValue: float,
        fundsCumulatively: dict
    ) -> dict[str, float]:
        entry = {}

        entry["Date"] = currentDate.strftime("%Y-%m-%d")
        entry["Value"] = round(currentInvestValue, 2)

        entry["Invested Money"] = sum(
            [fundsCumulatively[value]["Money"] for value in fundsCumulatively]
        )

        for fund in fundsCumulatively:

            entry[f"{fund} P.U."] = (
                fundsCumulatively[fund]["ParticipationUnits"]
            )

            entry[f"{fund} Value"] = round((
                fundsCumulatively[fund]["ParticipationUnits"] *
                self.FundsQuotations[fund].getFundPriceOnDate(
                    currentDate.strftime("%Y-%m-%d"))
            ), 2)

            entry[f"{fund} Invested Money"] = round(
                fundsCumulatively[fund]["Money"], 2
            )

            try:
                entry[f"{fund} Refund"] = round(
                    (
                        (
                            (
                                entry[f"{fund} Value"] /
                                fundsCumulatively[fund]["Money"]
                            ) - 1
                        )
                    ), 4
                )
            except:
                entry[f"{fund} Refund"] = 0.0

        return entry
    
    def calcInvestmentDuration(self):
        if self.EndDate == Investment.EndDateNotSet:
            self.InvestmentDetailsDurationDays = (
                (datetime.datetime.now().date() - self.StartDate).days
            )
        else:
            self.InvestmentDetailsDurationDays = (
                (self.EndDate - self.StartDate).days
            )
    
    def calcInvestmentDayByDay(self):
        
        fundsOperationsByDate = self.initFundsOperationsByDate()
        fundsCumulatively = self.initFundsCumulatively()

        currentProcessingDate = sorted(list(fundsOperationsByDate.keys()))[0]
        
        while (
            (currentProcessingDate <= datetime.date.today()) and
            (currentProcessingDate <= self.EndDate)
            ):

            # Init local while loop variable
            currentValue = 0.0

            if currentProcessingDate in list(fundsOperationsByDate.keys()):
                fundsCumulatively = self.appendFundsCumulatively(
                    currentProcessingDate,
                    fundsCumulatively,
                    fundsOperationsByDate
                )

            # Loop through each fund in investment
            for fund in self.InvestmentDetails:
                try:
                    # try to get fund price for current calculation date
                    price = self.FundsQuotations[fund].getFundPriceOnDate(
                        currentProcessingDate.strftime("%Y-%m-%d")
                    )

                    units = fundsCumulatively[fund]["ParticipationUnits"]
                    currentValue += units * price
                except:
                    break
            else:
                self.DayByDay.append(
                    self.getOutputForCurrentDay(
                        currentDate=currentProcessingDate,
                        currentInvestValue=currentValue,
                        fundsCumulatively=fundsCumulatively
                    )
                )
            # Increment calculation date with +1 day
            currentProcessingDate += datetime.timedelta(days=1)

    def saveInvestmentHistoryDayByDay(self, investmentName, destinationPath=None):
        # Check if destination Path was provided and create appropriate `destinationFilePath`
        if destinationPath == None or not destinationPath:
            destinationFilePath = f"{investmentName}.csv"
        else:
            destinationFilePath = f"{destinationPath}/{investmentName}.csv"

        # open file to write Day to day investment stats
        with open(destinationFilePath, "w") as investHistory:

            # Init CSV writer and write headers to the file
            writer = csv.writer(investHistory, delimiter='\t')
            writer.writerow(list(self.DayByDay[0].keys()))
            for i in range(0, len(self.DayByDay)):
                writer.writerow(
                    list(
                        self.DayByDay[i].values()
                    )
                )

        return None
