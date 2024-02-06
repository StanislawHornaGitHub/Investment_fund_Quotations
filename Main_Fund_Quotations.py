"""
.SYNOPSIS
    Program to download funds quotations and calculate profits of investments.
    Without params program is creating report about todays funds' stats in JSON

.DESCRIPTION
    Program which will download funds quotations from website Analizy.pl, based on URLs provided in CONFIG.json.
    Additionally it will calculate profit of investments defined in Investments.json
    
    CONFIG.json structure:
    {
        "HistoricalQuotationDirectoryName": "Output",
        "InvestmentsFilePath":"Investments.json",
        "FundsToCheckURLs": [
            "<URL_To_Fund_1>",
            "<URL_To_Fund_2>",
            "<URL_To_Fund_3>",
            "<URL_To_Fund_4>"
        ]
    }
    HistoricalQuotationDirectoryName <- path to the folder where historical quotations will be saved
        It can be relative or absolute path
    InvestmentsFilePath <- file path to the JSON with investments definition. 
        It can be relative or absolute path
    FundsToCheckURLs <- list of URL to funds which will be checked
    
    Investments.json structure:
    {
        "<Name_of_investment_wallet>": {
            "<Fund_ID_1>": {
                "BuyDate": "<Date_when_fund_was_bought>",
                "Money": <Amount_allocated_for_the_purchase>
            },
            "<Fund_ID_2>": {
                "BuyDate": "<Date_when_fund_was_bought>",
                "Money": <Amount_allocated_for_the_purchase>
            }
        },
        "<Name_of_investment_wallet>": {
            "<Fund_ID_3>": {
                "BuyDate": "<Date_when_fund_was_bought>",
                "Money": <Amount_allocated_for_the_purchase>
            },
            "<Fund_ID_4>": {
                "BuyDate": "<Date_when_fund_was_bought>",
                "Money": <Amount_allocated_for_the_purchase>
            }
        },
    }
    Each fund selected in Investments.json must be included in CONFIG.json in section FundsToCheckURLs
    <Name_of_investment_wallet> <- User friendly name of funds set 
    <Fund_ID_X> <- Fund ID allocated under particular fund set,
        it can be read out from fund URL or run program with -l (--Latest_Fund_Data_Only) param
    <Date_when_fund_was_bought> <- Date when fund was bought
    <Amount_allocated_for_the_purchase> <- amount of money used to buy particular fund
    
    
.INPUTS
        --Latest_Fund_Data_Only <- displays todays funds' stats
        --Print_Investment_Refund_Calculation <- prints investment refund for today
        --Quotations_Output_Format {CSV,JSON} <- accepts only CSV or JSON as an input.
            According to provided format Historical quotations will be saved.

.OUTPUTS
    None

.NOTES

    Version:            1.1
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      05-Feb-2024
    ChangeLog:

    Date            Who                     What
    2024-02-06      Stanislaw Horna         Command-line arguments modified.
                                            saveInvestmentHistoryDayByDay method added
"""

import argparse
from Dependencies.Class_Fund import ListOfFunds
from Dependencies.Class_InvestmentWallet import InvestmentWallet
from Dependencies.Function_config import *

programSynopsis = '''
Program to download funds quotations and calculate profits of investments.
Without params program is creating report about todays funds' stats in JSON
'''

parser = argparse.ArgumentParser(
    description = programSynopsis
)
parser.add_argument(
    "-l",
    "--Print_Latest_Fund_Data_Only",
    action="store_true",
    help="Prints current fund's details",
)
parser.add_argument(
    "-i",
    "--Print_Investment_Refund_Calculation",
    action="store_true",
    help="Prints result of investments refund",
)
parser.add_argument(
    "--Quotations_Output_Format", 
    choices=["CSV", "JSON"], 
    help="Define file type in which historical fund quotations will be saved."
)


def main(options):
    
    config = getConfiguration(options)
    
    Funds = ListOfFunds(config[FundsToCheckURLsKey])
    Funds.downloadLatestDetails()
    Funds.saveTodaysResults()
    Funds.downloadHistoricalQuotation()
    
    latestFundDataOnly(Funds, options)
    historicalQuotations(Funds, options)
    
    investments = InvestmentWallet(config[InvestmentsFilePathKey], Funds)
    investments.calculateRefundDetails()
    investments.saveInvestmentHistoryDayByDay()
    
    
    investmentRefundCalculation(investments, options)
    exit(0)

def latestFundDataOnly(Funds, options):
    if options.Print_Latest_Fund_Data_Only:
        Funds.printFundInfo()

def historicalQuotations(Funds, options):
    if options.Quotations_Output_Format == "JSON":
        Funds.saveQuotationJSON()
    
    if options.Quotations_Output_Format == "CSV":
        Funds.saveQuotationCSV()
        

def investmentRefundCalculation(investments, options):
    if options.Print_Investment_Refund_Calculation:
        investments.printInvestmentResults()


main(parser.parse_args())
