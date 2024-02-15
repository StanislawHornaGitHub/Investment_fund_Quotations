"""
.DESCRIPTION
    Definition file of AnalizyFund class. 
    Class is data structure to download fund quotation from provided URL, store 
    and calculate results of a single investment fund.
    Investment URL must be a valid URL to www.Analizy.pl website
    
.INITIALIZATION
    By default class was meant to be a attribute of ListOfFund class

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
import requests
import json
import csv
from lxml.html import fromstring
from dataclasses import dataclass, field

# Custom created variables modules
from Dependencies.Variables_API import *
from Dependencies.Variable_Xpath_Filter import *


@dataclass
class AnalizyFund:

    # Initialization Variables
    URL: str

    # Constant Variables
    QuotationsAPI = analizyplQuotationAPI

    # Calculated Variables
    ID: str = field(init=False)
    Name: str = field(init=False)
    Category: str = field(init=False)
    CategoryShortCut: str = field(init=False)

    def __post_init__(self):
        # Collect following values from provided URL
        urlBreakdown = self.URL.split("/")
        self.Category = urlBreakdown[3]
        self.ID = urlBreakdown[4]
        self.Name = urlBreakdown[5].replace("-", " ").title()
        self.CategoryShortCut = "".join([word[0] for word in self.Category.split("-")])

        # Invoke method to download stats for Today: Price, Currency, LastUpdate date,
        # Change Value comparing to previous day, Change percentage comparing to previous day
        self.downloadLatestDetails()

        # Download historical quotation in JSON format
        self.downloadHistoricalQuotation()

    def getFundID(self) -> str:
        return self.ID

    def getPrice(self) -> float:
        return float(self.Price)

    def getCurrency(self) -> str:
        return self.Currency

    def getLastChangePercentage(self) -> float:
        return self.ChangePercentage1D

    def getFundPriceOnDate(self, date) -> float:
        return float(
            [
                item
                for item in self.QuotationJSON["Price"]
                if item[analizyplAPIresponse_QuotationDate] == date
            ][0][analizyplAPIresponse_QuotationValue]
        )

    def downloadLatestDetails(self):

        # Invoke web request to provided URL
        response = requests.get(self.URL)

        # Convert response to HTML tree
        treeHTML = fromstring(response.content)

        # Get price value filtered by `xpathFilter_Price`
        # .strip() <- to replace spaces, new lines, etc
        # .replace(",", ".") <- to change decimal separator to `.`
        self.Price = str(treeHTML.xpath(xpathFilter_Price)[0]).strip().replace(",", ".")

        # Get currency value filtered by `xpathFilter_Price`
        # .strip() <- to replace spaces, new lines, etc
        # .replace(",", ".") <- to change decimal separator to `.`
        self.Currency = str(treeHTML.xpath(xpathFilter_Currency)[1]).strip()

        # Get last update date value filtered by `xpathFilter_Price`
        # .strip() <- to replace spaces, new lines, etc
        # .replace(",", ".") <- to change decimal separator to `.`
        self.UpdateDate = str(treeHTML.xpath(xpathFilter_UpdateDate)[0]).strip()

        # Get change percentage value filtered by `xpathFilter_Price`
        # .strip() <- to replace spaces, new lines, etc
        # .replace("/", "")[:-1] <- remove / which is in the same field and skip % sign
        # .replace(",", ".") <- to change decimal separator to `.`
        self.ChangePercentage1D = (
            str(treeHTML.xpath(xpathFilter_ChangePercentage1D)[1].replace("/", "")[:-1])
            .strip()
            .replace(",", ".")
        )

        # Get last update date value filtered by `xpathFilter_Price`
        # .strip() <- to replace spaces, new lines, etc
        # .replace(",", ".") <- to change decimal separator to `.`
        self.ChangeValue1D = (
            str(treeHTML.xpath(xpathFilter_ChangeValue1D)[0]).strip().replace(",", ".")
        )
        return None

    def downloadHistoricalQuotation(self):

        # Create custom URL to access API to download JSON with all quotation
        URL = f"{AnalizyFund.QuotationsAPI}/{self.CategoryShortCut}/{self.ID}"

        # Invoke web request and convert JSON response to dict
        fundQuotationResponse = json.loads(requests.get(URL).content)

        # Save needed data from response to class attribute
        self.QuotationJSON = {
            "FundID": fundQuotationResponse[analizyplAPIresponse_ID],
            "Currency": fundQuotationResponse[analizyplAPIresponse_Currency],
            "Price": fundQuotationResponse[analizyplAPIresponse_QuotationDetails][0][
                analizyplAPIresponse_QuotationList
            ],
        }
        return None

    def saveQuotationJSON(self, destinationPath):

        # Check if destination Path was provided and create appropriate `destinationFilePath`
        if destinationPath == None:
            destinationFilePath = f"FQ_{self.CategoryShortCut}_{self.ID}.json"
        else:
            destinationFilePath = (
                f"{destinationPath}/FQ_{self.CategoryShortCut}_{self.ID}.json"
            )

        # Open destination file and write dict dumped to JSON structure
        with open(destinationFilePath, "w") as destinationFileJSON:
            destinationFileJSON.write(json.dumps(self.QuotationJSON, indent=4))

        return None

    def saveQuotationCSV(self, destinationPath):

        # Check if destination Path was provided and create appropriate `destinationFilePath`
        if destinationPath == None:
            destinationFilePath = f"FQ_{self.CategoryShortCut}_{self.ID}.csv"
        else:
            destinationFilePath = (
                f"{destinationPath}/FQ_{self.CategoryShortCut}_{self.ID}.csv"
            )

        # Open destination file
        with open(destinationFilePath, "w") as destinationFileCSV:

            # Create csv writer instance
            writer = csv.writer(destinationFileCSV, delimiter="\t")

            # Write csv headers
            writer.writerow(["Date", "Price", "Currency"])

            # Loop through quotation dict format
            for row in self.QuotationJSON["Price"]:

                # write CSV row with writer
                writer.writerow(
                    # Convert dict structure to list with same column order as already written headers
                    [
                        row[analizyplAPIresponse_QuotationDate],
                        row[analizyplAPIresponse_QuotationValue],
                        self.Currency,
                    ]
                )

        return None

    def ExportTodaysResults(self) -> dict:
        # Return class attributes as dict
        return {
            "FundName": self.Name,
            "FundID": self.ID,
            "Price": self.Price,
            "Currency": self.Currency,
            "ChangePercent(1D)": self.ChangePercentage1D,
            "ChangePrice(1D)": self.ChangeValue1D,
            "LastUpdate": self.UpdateDate,
            "FundURL": self.URL,
        }

    def getFundInfo(self) -> dict:
        # Return class attributes as dict
        return {
            "Name": f"{self.Name}",
            "ID": f"{self.ID}",
            "Price": f"{self.Price}",
            "ValueChange": f"{self.ChangeValue1D}",
            "PercentChange": f"{self.ChangePercentage1D}",
            "LastUpdate": f"{self.UpdateDate}",
        }
