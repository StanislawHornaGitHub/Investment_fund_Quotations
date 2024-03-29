"""
.DESCRIPTION
    Definition file of InvestmentWallet class. 
    Class is data structure to store list of Investment class instances, perform calculation on them and
    present summarized results for all investments.
    
    To create an instance of this class you need to use keywords.
    Keywords for required variables:
        -InvestmentsFilePath <- file path to the JSON file with following structure:
                {
                    "<Investment_name_1>": {
                        "StartDate": "<yyyy-MM-dd>",
                        "EndDate": "<yyyy-MM-dd>",
                        "Funds": {
                            "Fund_ID_1": [
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                },
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                }
                            ],
                            "<Fund_ID_2>": [
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                },
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                }
                            ]
                        },
                    "<Investment_name_2>": {
                        "StartDate": "<yyyy-MM-dd>",
                        "EndDate": "<yyyy-MM-dd>",
                        "Funds": {
                            "Fund_ID_1": [
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                },
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                }
                            ],
                            "<Fund_ID_2>": [
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                },
                                {
                                    "BuyDate": "<yyyy-MM-dd>",
                                    "Money": <int_or_float>
                                }
                            ]
                        }
                    }
                }
            EndDate in JSON structure can be set to empty string or does not exist
        - FundsList <- an instance of ListOfFunds with already downloaded data from web
        
.NOTES

    Version:            1.4
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      07-Feb-2024
    ChangeLog:

    Date            Who                     What
    2024-02-16      Stanisław Horna         According to changes in Investment class
                                            InvestmentsFile JSON structure has changed.
                                            Handling for sold funds as archive information.
    2024-02-20      Stanisław Horna         Refactored investment refund table
    2024-02-21      Stanisław Horna         Adjustments to calling Investment Class contractor and methods.
    2024-03-12      Stanisław Horna         printQuotationRefundAnalysis method to display analysis,
                                            based on the payments, timing and invested money

"""

# Official and 3-rd party imports
import json
from dataclasses import dataclass, field
from tabulate import tabulate
import datetime
from dateutil.parser import parse

# Custom created function modules
from Dependencies.Function_Conversion import convertNumericToStrPlsMnsSigns

# Custom created class modules
from Dependencies.Class_Investment import Investment
from Dependencies.Class_ListOfFund import ListOfFunds


@dataclass(kw_only=True)
class InvestmentWallet:

    # Initialization Variables
    InvestmentsFilePath: str
    FundsList: ListOfFunds

    TableFormatInvestmentResults: str = "simple_grid"
    TableFormatRefundAnalysis: str = "github"

    # Calculated Variables
    Wallets: dict[str, Investment] = field(default_factory=dict, init=False)
    WalletsResults: dict[str, list[dict[str, str | float]]] = field(
        default_factory=dict, init=False
    )

    def __post_init__(self):
        # Open investment file and parse JSON content
        with open(self.InvestmentsFilePath, "r") as Invest:
            investments = json.loads(str("\n".join(Invest.readlines())))

        # Loop through each configured investment
        # Create separate Investment class instance for each of it
        for item in investments:

            # Parse start date and end date for constructor of investment class
            startDate = parse(investments[item]["StartDate"]).date()
            if "EndDate" in list(investments[item].keys()):
                try:
                    endDate = parse(investments[item]["EndDate"]).date()
                except:
                    endDate = Investment.EndDateNotSet
            else:
                endDate = Investment.EndDateNotSet

            self.Wallets[item] = Investment(
                InvestmentDetails=investments[item]["Funds"],
                InvestmentName = item,
                StartDate=startDate,
                EndDate=endDate,
                FundsList=self.FundsList
            )

        self.calcWalletResults()
        return None

    def calcRefundDetails(self):
        # Invoke Refund calculation for each child Investment class
        for item in self.Wallets:
            self.Wallets[item].calcRefundDetails()

    def calcWalletResults(self):
        # Invoke results calculation for each child Investment class
        for item in self.Wallets:
            self.WalletsResults[item] = self.Wallets[item].getResult()

    def appendDataListToDisplay(
        self,
        fundID: str,
        dataHeaders: list[str],
        dataList: list[str | float],
        columnsWithoutSigns: list[str],
        columnsWithCurrency: list[str],
        columnsWithPercentage: list[str]
    ) -> list[list[str | float]]:
        # Loop through each line of list of dict containing fund result separately for each investment
        for i in range(0, len(self.WalletsResults[fundID])):
            # Append final data set
            dataList.append(
                # Convert results for each investment to add currency, % sign and
                # add + if value is greater or equal than 0 or - if value is less than 0
                convertNumericToStrPlsMnsSigns(
                    inputValues=list(
                        self.WalletsResults[fundID][i].values()),
                    headers=dataHeaders,
                    columnsExcludedFromSigns=columnsWithoutSigns,
                    currencyColumnNames=columnsWithCurrency,
                    currency=self.Wallets[fundID].Currency,
                    percentageColumnNames=columnsWithPercentage,
                )
            )
            
        dataList.append([])
        return dataList

    def printInvestmentResults(self):
        # Init local method variables
        dataList = []
        tempDataList = []
        dataHeaders = list(
            self.WalletsResults[list(self.WalletsResults.keys())[0]][0].keys()
        )
        columnsWithoutSigns = ["Days", "Investment %"]
        columnsWithCurrency = ["Profit", "Profit daily"]
        columnsWithPercentage = ["Refund Rate","Refund daily","Refund yearly","Investment %", "Fund refund %"]
        # Loop through each Investment class instance in self.Wallets dict
        for item in self.Wallets:
            if Investment.PrefixForSoldFunds not in self.WalletsResults[item][0]["Investment Name"]:
                dataList = self.appendDataListToDisplay(
                    item, dataHeaders, dataList, columnsWithoutSigns, columnsWithCurrency, columnsWithPercentage
                )
            else:
                tempDataList = self.appendDataListToDisplay(
                    item, dataHeaders, tempDataList, columnsWithoutSigns, columnsWithCurrency, columnsWithPercentage
                )

        # Merge active investments with archived ones
        dataList += tempDataList

        # Print collected dataset as table using tabulate Library
        print("\n")
        print(
            tabulate(
                headers=dataHeaders, 
                tabular_data=dataList[:-1], 
                tablefmt=self.TableFormatInvestmentResults,
            )
        )
        print("\n")

        return None

    def printRefundAnalysis(self):
        
        dataList = []
        
        # Loop through investments in wallet
        for item in self.Wallets.values():
            
            # Check if refund analysis is not None
            # it will be None for each archived investment
            if (refund:= item.getRefundAnalysis()) != None:
                
                # append dataList with values from analysis (without headers)
                for fund in refund.values():
                    dataList.append(fund)
        
        # print table in console
        print("\n")
        print(
            tabulate(
                headers=[row.keys() for row in dataList][0],
                tabular_data=[row.values() for row in dataList], 
                tablefmt=self.TableFormatRefundAnalysis,
            )
        )
        print("\n")

        return None
        

    def saveInvestmentHistoryDayByDay(self, destinationPath: str = None):
        # Invoke saving Investment history day by day for each Investment class instance
        for item in self.Wallets:
            self.Wallets[item].saveInvestmentHistoryDayByDay(destinationPath)
