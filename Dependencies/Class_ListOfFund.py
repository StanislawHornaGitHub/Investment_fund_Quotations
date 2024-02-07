"""
.DESCRIPTION
    Definition file of ListOfFunds class. 
    Class is data structure to store list of AnalizyFund class instances, perform calculation on them and
    present summarized results for all Funds.
    
    
.INITIALIZATION
    Class construction requires only and list of valid URLs to funds on www.analizy.pl
        

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
import json
from datetime import datetime
from tabulate import tabulate
from lxml.html import fromstring
from dataclasses import dataclass, field

# Custom created function modules
from Dependencies.Function_Conversion import convertNumericToStrPlsMnsSigns

# Custom created class modules
from Dependencies.Class_AnalizyFund import AnalizyFund

global todaysFundStatsFileSuffix

todaysFundStatsFileSuffix = "Report"

@dataclass
class ListOfFunds:
    ListOfFundURL: list[str]
    
    ListOfFunds: dict[str, AnalizyFund] = field(default_factory=dict, init=False)
    
    def __post_init__(self):
        
        # Loop through list of provided URLs
        for item in self.ListOfFundURL:
            
            # Create and instance of AnalizyFund class
            temp = AnalizyFund(URL=item)
            
            # Assign created class instance to a dict, where key is an ID of the fund
            self.ListOfFunds[temp.getFundID()] = temp
            
        return None

    def printFundInfo(self):
        
        # Init local variables for dataset and headers
        dataList = []
        dataHeaders = list(self.ListOfFunds[list(self.ListOfFunds.keys())[0]].getFundInfo().keys())
        
        # Loop through each fund
        for fund in self.ListOfFunds:
            
            # append dataset list with values to display
            dataList.append(
                
                # Convert results for each investment to add currency, % sign and
                # add + if value is greater or equal than 0 or - if value is less than 0
                convertNumericToStrPlsMnsSigns(
                    inputValues=list(self.ListOfFunds[fund].getFundInfo().values()),
                    headers = dataHeaders,
                    columnsExcludedFromSigns = ["Price"], 
                    currencyColumnNames = ["Price","ValueChange"],
                    currency = self.ListOfFunds[fund].getCurrency(),
                    percentageColumnNames = ["PercentChange"]
                    )
                )
        # Print collected dataset as table using tabulate Library
        print("\n")
        print(
            tabulate(
                tabular_data = dataList,
                tablefmt = "github", 
                headers = dataHeaders
                    )
            )
        print("\n")
        
        return None

    def saveQuotationJSON(self, destinationPath = None):
        # Invoke saving quotation for each configured fund in JSON format
        for fund in self.ListOfFunds:
            self.ListOfFunds[fund].saveQuotationJSON(destinationPath)
        
        return None

    def saveQuotationCSV(self, destinationPath = None):
        # Invoke saving quotation for each configured fund in CSV format
        for fund in self.ListOfFunds:
            self.ListOfFunds[fund].saveQuotationCSV(destinationPath)
        
        return None

    def saveTodaysResults(self, destinationPath = None):
        
        # Check if destination Path was provided and create appropriate `destinationFilePath`
        if destinationPath == None or not destinationPath:
            destinationFilePath = f"{datetime.now().strftime("%Y-%m-%d")}_{todaysFundStatsFileSuffix}.json"
        else:
            destinationFilePath = f"{destinationPath}/{datetime.now().strftime("%Y-%m-%d")}_{todaysFundStatsFileSuffix}.json"

        # Init local variable
        listToExport = []
        
        # Loop through each fund and append local list with exported details
        for fund in self.ListOfFunds:
            listToExport.append(self.ListOfFunds[fund].ExportTodaysResults())
        
        # Open destination file and write dumped dict to JSON structure
        with open(destinationFilePath, "w") as todaysResultJSON:
            todaysResultJSON.write(json.dumps(listToExport, indent=4))
            
        return None

    def getFundByID(self, ID: str) -> AnalizyFund:
        return self.ListOfFunds[ID]
