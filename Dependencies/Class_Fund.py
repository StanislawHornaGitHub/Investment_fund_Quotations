import requests
import json
import csv
from lxml.html import fromstring
from datetime import datetime

global todaysFundStatsFileSuffix
global analizyplQuotationAPI

global xpathFilter_Price
global xpathFilter_Currency
global xpathFilter_UpdateDate
global xpathFilter_ChangePercentage1D
global xpathFilter_ChangeValue1D

global analizyplAPIresponse_ID
global analizyplAPIresponse_Currency
global analizyplAPIresponse_QuotationDetails
global analizyplAPIresponse_QuotationList
global analizyplAPIresponse_QuotationDate
global analizyplAPIresponse_QuotationValue

todaysFundStatsFileSuffix = "Report"
analizyplQuotationAPI = "https://www.analizy.pl/api/quotation"

xpathFilter_Price = '//span[@class="productBigText"]/text()'
xpathFilter_Currency = '//div[@class="primaryContent"]/text()'
xpathFilter_UpdateDate = '//p[@class="lightProductText"]/text()'
xpathFilter_ChangePercentage1D = '//p[@class="productValueChange"]/text()'
xpathFilter_ChangeValue1D = '//p[@class="productValueChange"]/text()'

analizyplAPIresponse_ID = "id"
analizyplAPIresponse_Currency = "currency"
analizyplAPIresponse_QuotationDetails = "series"
analizyplAPIresponse_QuotationList = "price"
analizyplAPIresponse_QuotationDate = "date"
analizyplAPIresponse_QuotationValue = "value"

class ListOfFunds:    
    def __init__(self, ListOfFundURL):
        if not isinstance(ListOfFundURL, list):
            raise TypeError("ListOfFundURL must be a list")

        self.ListOfFunds = {}
        for item in ListOfFundURL:
            temp = AnalizyFund(item)
            self.ListOfFunds[temp.getFundID()] = temp

    def downloadLatestDetails(self):
        for fund in self.ListOfFunds:
            self.ListOfFunds[fund].downloadLatestDetails()

    def printFundInfo(self):
        for fund in self.ListOfFunds:
            self.ListOfFunds[fund].printFundInfo()
            
    def downloadHistoricalQuotation(self):
        for fund in self.ListOfFunds:
            self.ListOfFunds[fund].downloadHistoricalQuotation()

    def saveQuotationJSON(self, destinationPath = None):
        for fund in self.ListOfFunds:
            self.ListOfFunds[fund].saveQuotationJSON(destinationPath)

    def saveQuotationCSV(self, destinationPath = None):
        for fund in self.ListOfFunds:
            self.ListOfFunds[fund].saveQuotationCSV(destinationPath)
            
    def saveTodaysResults(self, destinationPath = None):
        if destinationPath == None:
            destinationFilePath = f"{datetime.now().strftime("%Y-%m-%d")}_{todaysFundStatsFileSuffix}.json"
        else:
            destinationFilePath = f"{destinationPath}/{datetime.now().strftime("%Y-%m-%d")}_{todaysFundStatsFileSuffix}.json"

        listToExport = []
        for fund in self.ListOfFunds:
            listToExport.append(self.ListOfFunds[fund].ExportTodaysResults())
            
        with open(destinationFilePath, "w") as todaysResultJSON:
            todaysResultJSON.write(json.dumps(listToExport, indent=4))
            
    def getFundByID(self, ID):
        if not type(ID) == str:
            raise Exception("ID must be a string")
        return self.ListOfFunds[ID]


class AnalizyFund:
    QuotationsAPI = analizyplQuotationAPI

    def __init__(self, FundURL):
        if not isinstance(FundURL, str):
            raise TypeError("FundURL must be a string")
        urlBreakdown = FundURL.split("/")
        self.URL = FundURL
        self.Category = urlBreakdown[3]
        self.ID = urlBreakdown[4]
        self.Name = urlBreakdown[5].replace("-", " ").title()
        self.CategoryShortCut = "".join([word[0] for word in self.Category.split("-")])

    def getFundName(self):
        return self.Name

    def getFundID(self):
        return self.ID

    def getFundURL(self):
        return self.URL

    def getCategoryName(self):
        return self.Category

    def getCategoryShortCut(self):
        return self.CategoryShortCut

    def getPrice(self):
        return float(self.Price)

    def getCurrency(self):
        return self.Currency

    def getChangePercentage1D(self):
        return self.ChangePercentage1D

    def getChangeValue1D(self):
        return self.ChangeValue1D

    def getQuotation(self):        
        return self.QuotationJSON["Price"]

    def getFundPriceOnDate(self, date):
        return float(
            [item for item in self.QuotationJSON["Price"] 
            if item[analizyplAPIresponse_QuotationDate] == date][0]["value"]
            )

    def downloadLatestDetails(self):
        response = requests.get(self.URL)

        treeHTML = fromstring(response.content)

        self.Price = (
            str(
                treeHTML
                .xpath(xpathFilter_Price)[0]
                )
            .strip()
            .replace(",", ".")
        )

        self.Currency = str(
            treeHTML
            .xpath(xpathFilter_Currency)[1]
        ).strip()

        self.UpdateDate = str(
            treeHTML
            .xpath(xpathFilter_UpdateDate)[0]
        ).strip()

        self.ChangePercentage1D = (
            str(
                treeHTML
                .xpath(xpathFilter_ChangePercentage1D)[1]
                .replace("/", "")[:-1]
            )
            .strip()
            .replace(",", ".")
        )

        self.ChangeValue1D = (
            str(treeHTML.xpath(xpathFilter_ChangeValue1D)[0])
            .strip()
            .replace(",", ".")
        )

    def downloadHistoricalQuotation(self):
        URL = f"{AnalizyFund.QuotationsAPI}/{self.CategoryShortCut}/{self.ID}"
        fundQuotationResponse = json.loads(requests.get(URL).content)
        self.QuotationJSON = {
            "FundID": fundQuotationResponse[analizyplAPIresponse_ID],
            "Currency": fundQuotationResponse[analizyplAPIresponse_Currency],
            "Price": fundQuotationResponse[analizyplAPIresponse_QuotationDetails][0][analizyplAPIresponse_QuotationList],
        }

    def saveQuotationJSON(self, destinationPath):
        if destinationPath == None:
            destinationFilePath = f"FQ_{self.CategoryShortCut}_{self.ID}.csv"
        else:
            destinationFilePath = f"{destinationPath}/FQ_{self.CategoryShortCut}_{self.ID}.csv"
        with open(destinationFilePath,"w") as destinationFileJSON:
            destinationFileJSON.write(json.dumps(self.QuotationJSON, indent=4))

    def saveQuotationCSV(self, destinationPath):
        if destinationPath == None:
            destinationFilePath = f"FQ_{self.CategoryShortCut}_{self.ID}.csv"
        else:
            destinationFilePath = f"{destinationPath}/FQ_{self.CategoryShortCut}_{self.ID}.csv"
        with open(destinationFilePath,"w") as destinationFileCSV:
            writer = csv.writer(destinationFileCSV, delimiter='\t')
            writer.writerow(["Date","Price","Currency"])
            for row in self.QuotationJSON["Price"]:
                writer.writerow(
                    [
                        row[analizyplAPIresponse_QuotationDate], 
                        row[analizyplAPIresponse_QuotationValue],
                        self.Currency
                    ]
                    )

    def ExportTodaysResults(self):
        return {
            "FundName": self.Name,
            "FundID": self.ID,
            "Price": self.Price,
            "Currency": self.Currency,
            "ChangePercent(1D)": self.ChangePercentage1D,
            "ChangePrice(1D)": self.ChangeValue1D,
            "LastUpdate": self.UpdateDate,
            "FundURL": self.URL
        }

    def printFundInfo(self):
        print(
            f"\n{self.Name} ( {self.ID} ) \n",
            f"Kurs: {self.Price} {self.Currency} \n",
            f"Data Aktualizacji: {self.UpdateDate}\n",
            f"Zmiana Wartości (1D): {self.ChangeValue1D} {self.Currency}\n",
            f"Zmina Procentowo: {self.ChangePercentage1D} %",
        )
