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

    Version:            1.5
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
    2024-02-21      Stanisław Horna         Investments which are ended can be pulled from InvestmentDayByDay CSV file.
                                            Dedicated result presenting method for investments consisted of only 1 fund
    2024-03-04      Stanisław Horna         Handling for investments containing funds which do not receive updated data
                                            at the same time.
    2024-03-08      Stanisław Horna         Multiple payments for same fund at the same date summed up,
                                            instead of taking the last one

"""
# Official and 3-rd party imports
import os
import csv
import datetime
from dateutil.parser import parse
from dataclasses import dataclass, field

# Custom created function modules
from Dependencies.Variable_InvestmentFile import *
from Dependencies.Function_config import getConfiguration

# Custom created class modules
from Dependencies.Class_ListOfFund import ListOfFunds
from Dependencies.Class_AnalizyFund import AnalizyFund

from tabulate import tabulate


@dataclass(kw_only=True)
class Investment:

    # Initialization Variables
    InvestmentDetails: dict[str, dict[str, float | str]]
    InvestmentName: str
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
    Refunds: dict[str, dict[str, float | str]] = field(
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

    def __post_init__(self) -> None:
        currencySet = set()

        # If investment date is set and try to import data from previously created file
        if self.isEndDateSet() and self.importArchivedInvestmentFromFile():

            # get investment currency
            firstDay = self.DayByDay[0]
            for column in [col for col in list(firstDay.keys()) if "Currency" in col]:
                currencySet.add(firstDay[column])

            self.Currency = currencySet.pop()
            while len(currencySet):
                self.Currency += " / " + currencySet.pop()
        else:

            # Loop through selected funds, assign them to the class variable `FundsQuotations`, add fund currency to the set
            for fund in self.InvestmentDetails:
                self.FundsQuotations[fund] = self.FundsList.getFundByID(fund)
                currencySet.add(self.FundsQuotations[fund].getCurrency())

            # append currency string with the last set item
            self.Currency = currencySet.pop()

            # loop while currency set is not empty and add each currency
            while len(currencySet):
                self.Currency += " / " + currencySet.pop()

            self.calcInvestmentDayByDay()
            self.calcRefundDetails()

        self.calcInvestmentDuration()

        return None

    def importArchivedInvestmentFromFile(self) -> bool:

        # Import config file to get localization of DayByDay investment files
        config = getConfiguration()
        investFilePath = f"{
            config["InvestmentHistoryDayByDayDirectory"]}/{self.InvestmentName}.csv"

        # Check if file exists
        if os.path.isfile(investFilePath):

            # Open file and assign it to class attribute
            with open(investFilePath, "r") as file:
                self.DayByDay = list((csv.DictReader(file, delimiter='\t')))

            # Convert number values to float datatype
            for row in self.DayByDay:
                for col in row:
                    try:
                        row[col] = float(row[col])
                    except:
                        pass

            # Check if found file ends with the same date as End investment date is set
            if parse(self.DayByDay[-1]["Date"]).date() == self.EndDate:
                return True

        # If file does not exist return False as nothing can be done
        return False

    def calcRefundDetails(self) -> None:

        refundPeriods = {}

        # create a summary for each period between payments
        for fund in self.InvestmentDetails:
            refundPeriods = []

            for i in range(0, len(self.InvestmentDetails[fund])):

                refundPeriods.append(
                    {
                        "startDate": parse(self.InvestmentDetails[fund][i]["BuyDate"]).date(),
                        "endDate": None,
                        "timeFrameInDays": None,
                        "refund": None
                    }
                )
                try:
                    refundPeriods[i-1]["endDate"] = parse(
                        self.InvestmentDetails[fund][i]["BuyDate"]
                    ).date()
                except:
                    pass

            # Add end date for last payment
            refundPeriods[-1]["endDate"] = self.FundsQuotations[fund].getLastQuotationDate()

            self.Refunds[fund] = (
                self.FundsQuotations[fund]
            ).getSyntheticRefundData(refundPeriods)

        return None

    def printNewFundRefund(self):

        data = []
        try:
            headers = list(self.Refunds[list((self.Refunds.keys()))[0]].keys())
        except:
            return None

        for fund in self.Refunds:
            data.append(self.Refunds[fund].values())

        print("\n")
        print(
            tabulate(
                tabular_data=data, tablefmt="github", headers=headers
            )
        )
        print("\n")

    def isEndDateSet(self) -> bool:
        if self.EndDate != Investment.EndDateNotSet:
            return True
        return False

    def getProfit(self) -> float:
        return round(self.Profit, 2)

    def getRefundRate(self) -> float:
        return round(self.refundRate, 4)

    def getInvestmentDurationDays(self) -> int:
        return self.InvestmentDetailsDurationDays

    def getNearestFundPrice(self, fundID: str, date: datetime.date, daysLimit: int) -> float:
        # init local variables to look for fund quotation
        daysToSubtract = 0
        newDateToCheck = date
        price = None

        # Loop until price is None or daysToSubtract is greater than 7
        # It makes no sense to look further in the past for the quotation of particular fund investment
        while price == None and daysToSubtract <= daysLimit:

            # calculate new date to check the quotation
            newDateToCheck -= datetime.timedelta(
                days=daysToSubtract
            )

            # get the fund price for new (older) date
            # if it will be different than None, than while loop will not be continued
            price = self.FundsQuotations[fundID].getFundPriceOnDate(
                newDateToCheck.strftime("%Y-%m-%d")
            )

            # Increment value for next iteration if value will be still None
            daysToSubtract += 1

        return price

    def initResults(self) -> None:

        # Loop through each fund, to calculate latest results
        for fund in self.InvestmentDetails:

            # Init dict for current fund
            self.Results[fund] = {}

            # Set current participation units
            self.Results[fund]["ParticipationUnits"] = (
                self.DayByDay[-1][f"{fund} P.U."]
            )

            # Set invested in fund money
            self.Results[fund]["InvestedMoney"] = (
                self.DayByDay[-1][f"{fund} Invested Money"]
            )

            # Set the fund value for today
            self.Results[fund]["TodaysValue"] = (
                self.DayByDay[-1][f"{fund} Value"]
            )

            # Set refund rate
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

    def getResult(self) -> list[dict[str, float | str]]:

        self.initResults()

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
                "Investment Name": f"{prefixForArchived} {self.InvestmentName}",
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
                    "Refund Rate": self.Results[fund]["RefundRate"],
                    "Profit daily": fundProfit / timeFrame,
                    "Refund daily": self.Results[fund]["RefundRate"] / timeFrame,
                    "Refund yearly": (self.Results[fund]["RefundRate"] / timeFrame) * 365,
                }
            )

        # Handling edge case if the investment consists of only 1 fund
        if len(self.InvestmentDetails) == 1:
            resultList[0]["Fund ID"] = resultList[1]["Fund ID"]
            resultList[0]["Investment %"] = resultList[1]["Investment %"]
            resultList = [resultList[0]]

        # return data to display
        return resultList

    def initFundsOperationsByDate(self) -> dict[datetime.datetime, dict[str, dict[str, float]]]:

        # init local variable to return
        ordersByDate = {}

        # Loop thorough each fund in investment
        for fund in self.InvestmentDetails:

            # Loop thorough each operation defined in investment config
            for i in range(0, len(self.InvestmentDetails[fund])):

                # parse date of currently processed operation
                currentDate = parse(
                    self.InvestmentDetails[fund][i]["BuyDate"]
                ).date()

                # if this date is not included create an inner dict
                if currentDate not in list(ordersByDate.keys()):
                    ordersByDate[currentDate] = {}

                # create inner dict for particular fund
                if fund not in list(ordersByDate[currentDate].keys()):
                    ordersByDate[currentDate][fund] = {
                        "Money": 0,
                        "ParticipationUnits": 0
                    }

                # get invested money at this day
                ordersByDate[currentDate][fund]["Money"] += self.InvestmentDetails[fund][i]["Money"]

                # calculate fund participation units for this day
                ordersByDate[currentDate][fund]["ParticipationUnits"] += (
                    self.InvestmentDetails[fund][i]["Money"] /
                    self.FundsQuotations[fund].getFundPriceOnDate(
                        currentDate.strftime("%Y-%m-%d")
                    )
                )

        # return organized data
        return ordersByDate

    def initFundsCumulatively(self) -> dict[str, dict[str, float]]:

        # Inits an investment entry for further calculations
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

        # appends initialized investment entry
        for fund in fundsOperationsByDate[currentDate]:
            fundsCumulatively[fund]["ParticipationUnits"] += fundsOperationsByDate[currentDate][fund]["ParticipationUnits"]
            fundsCumulatively[fund]["Money"] += fundsOperationsByDate[currentDate][fund]["Money"]

        return fundsCumulatively

    def getOutputForCurrentDay(
        self,
        currentDate: datetime.datetime,
        todaysFundStats: dict[str, dict[str, float]],
        fundsCumulatively: dict
    ) -> dict[str, float]:

        # Init local variable to return
        entry = {}
        currentValue = 0.0
        # Loop thorough each fund
        for fund in todaysFundStats:

            # Calculate current investment value
            currentValue += (
                todaysFundStats[fund]["units"] *
                todaysFundStats[fund]["price"]
            )

        # Parse the date and round investment value
        entry["Date"] = currentDate.strftime("%Y-%m-%d")
        entry["Value"] = round(currentValue, 2)

        # Sum up invested money in this investment
        entry["Invested Money"] = sum(
            [fundsCumulatively[value]["Money"] for value in fundsCumulatively]
        )

        # Loop through each fund to calculate fund's related stats with proper headers
        for fund in fundsCumulatively:

            # Participation units
            entry[f"{fund} P.U."] = (
                fundsCumulatively[fund]["ParticipationUnits"]
            )

            # Rounded fund current value on a given day
            entry[f"{fund} Value"] = round((
                todaysFundStats[fund]["units"] *
                todaysFundStats[fund]["price"]
            ), 2)

            # Invested money in current fund
            entry[f"{fund} Invested Money"] = round(
                fundsCumulatively[fund]["Money"], 2
            )

            # Try to calculate refund in percentage for current fund
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
            # If refund calculation will fail it is most likely related to 0 division error
            # in such case set the value to 0, because
            # it will handle the edge case when:
            # on the first day we bought fund A, on the second day we bought fund B.
            # If we would like to calculate the investment results on the first day,
            # we do not have any money invested in fund B yet, so it's value will be 0, as
            # we will buy it in the future looking form the day first perspective
            except:
                entry[f"{fund} Refund"] = 0.0

            # Add currency for the fund which will be required for reading out historical investments from file
            entry[f"{fund} Currency"] = self.FundsQuotations[fund].getCurrency()

        return entry

    def calcInvestmentDuration(self) -> None:

        # If EndDate is set to static attribute means that it has not been sold,
        # so we have to calculate the duration using current date
        if self.EndDate == Investment.EndDateNotSet:
            oldestQuotationDate = sorted([fund.getLastQuotationDate() for fund in self.FundsQuotations.values()])[-1]
            self.InvestmentDetailsDurationDays = (
                (oldestQuotationDate - self.StartDate).days
            )

        # if End date is set to any other date than we have to use it,
        # as investment has been completed
        else:
            self.InvestmentDetailsDurationDays = (
                (self.EndDate - self.StartDate).days
            )

        # Subtracting 1 because on buy date fund is only bought and it is not possible to make any profit
        self.InvestmentDetailsDurationDays -= 1

        return None

    def calcInvestmentDayByDay(self) -> None:

        # Init local calculation variables
        fundsOperationsByDate = self.initFundsOperationsByDate()
        fundsCumulatively = self.initFundsCumulatively()

        # Get first date when any fund of the investment was bought
        currentProcessingDate = sorted(list(fundsOperationsByDate.keys()))[0]

        # Loop until the current date is less or equal to today's date or investment end date
        while (
            (currentProcessingDate <= datetime.date.today()) and
            (currentProcessingDate <= self.EndDate)
        ):

            # Check if on currently processing dates funds were not bought or sold
            if currentProcessingDate in list(fundsOperationsByDate.keys()):
                fundsCumulatively = self.appendFundsCumulatively(
                    currentProcessingDate,
                    fundsCumulatively,
                    fundsOperationsByDate
                )

            # init temp dict to collect funds' units and prices
            tempInvestDetails = {}

            # Loop through each fund in investment
            for fund in self.InvestmentDetails:

                # get fund data for currently processing day
                tempInvestDetails[fund] = {
                    "price": self.FundsQuotations[fund].getFundPriceOnDate(
                        currentProcessingDate.strftime("%Y-%m-%d")
                    ),
                    "units": fundsCumulatively[fund]["ParticipationUnits"]
                }

            # Check if collected fund prices contains None values only, this will find out, if
            # there are no prices for any fund, it means that there is nothing to calculate and
            # we can continue to next while loop iteration.
            # It can happen most likely during the weekends or bank holidays,
            # that for this date no fund will have quotation established
            # (None is returned by .getFundPriceOnDate() if there is no price for a given date)
            if not [tempInvestDetails[fund]["price"]
                    for fund in tempInvestDetails.keys()
                    if tempInvestDetails[fund]["price"] != None]:
                # Increment calculation date with +1 day
                currentProcessingDate += datetime.timedelta(days=1)
                continue
            # If there are no "None" values or results are mixed - some funds have price, some "None",
            # we have data to perform calculation
            else:

                # Get the list of fund IDs which has "None" as price
                fundsWithoutPrice = [
                    fund for fund in tempInvestDetails.keys()
                    if tempInvestDetails[fund]["price"] == None
                ]

                # Loop thorough each fund with None price,
                # for each fund we will try to find quotation for previous days before this currently being processed.
                for fund in fundsWithoutPrice:

                    # init local variables to look for fund quotation
                    daysToSubtract = 1
                    newDateToCheck = currentProcessingDate

                    # Loop until price is None or daysToSubtract is greater than 7
                    # It makes no sense to look further in the past for the quotation of particular fund investment
                    while tempInvestDetails[fund]["price"] == None and daysToSubtract <= 7:

                        # calculate new date to check the quotation
                        newDateToCheck -= datetime.timedelta(
                            days=daysToSubtract
                        )

                        # get the fund price for new (older) date
                        # if it will be different than None, than while loop will not be continued
                        tempInvestDetails[fund]["price"] = self.FundsQuotations[fund].getFundPriceOnDate(
                            newDateToCheck.strftime("%Y-%m-%d")
                        )

                        # Increment value for next iteration if value will be still None
                        daysToSubtract += 1

            # Check if all funds of the investment have the price found.
            # Dates with missing fund values will not be included in DayByDay investment result.
            # We have to keep this condition according to the while loop above with additional exit condition:
            # daysToSubtract <= 7
            if None not in [tempInvestDetails[fund]["price"] for fund in tempInvestDetails.keys()]:

                # Append result attribute with the proper output
                self.DayByDay.append(
                    self.getOutputForCurrentDay(
                        currentDate=currentProcessingDate,
                        todaysFundStats=tempInvestDetails,
                        fundsCumulatively=fundsCumulatively
                    )
                )

            # Increment calculation date with +1 day
            currentProcessingDate += datetime.timedelta(days=1)

        return None

    def saveInvestmentHistoryDayByDay(self, destinationPath=None) -> None:

        # Check if destination Path was provided and create appropriate `destinationFilePath`
        if destinationPath == None or not destinationPath:
            destinationFilePath = f"{self.InvestmentName}.csv"
        else:
            destinationFilePath = f"{
                destinationPath}/{self.InvestmentName}.csv"

        # open file to write Day to day investment stats
        with open(destinationFilePath, "w") as investHistory:

            # Init CSV writer and write headers to the file
            writer = csv.writer(investHistory, delimiter='\t')
            
            # write headers to file
            writer.writerow(list(self.DayByDay[0].keys()))
            
            # loop through each calculated date
            for i in range(0, len(self.DayByDay)):
                
                # convert values for current date to list and write them to file
                writer.writerow(
                    list(
                        self.DayByDay[i].values()
                    )
                )

        return None
