"""
.SYNOPSIS
    Program to download funds quotations and calculate profits of investments.
    Without params program is creating report about todays funds' stats in JSON

.DESCRIPTION
    Program which will download funds quotations from website Analizy.pl, based on URLs provided in CONFIG.json.
    Additionally it will calculate profit of investments defined in Investments.json
    
    CONFIG.json structure:
    {
        "HistoricalQuotationDirectoryName": "Output_Quotations",
        "DailyReportDirectoryName": "Output_DailyChanges",
        "InvestmentHistoryDayByDayDirectory": "Output_InvestmentsDayByDay",
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
    
    DailyReportDirectoryName <- path to the folder where todays fund's stats will be saved
    
    InvestmentHistoryDayByDayDirectory <- path to the folder where DayByDay investments results will be saved
    
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
        it can be read out from fund URL or run program with -l (--Print_Latest_Fund_Data) param
    <Date_when_fund_was_bought> <- Date when fund was bought
    <Amount_allocated_for_the_purchase> <- amount of money used to buy particular fund
    
    
.INPUTS
        --Latest_Fund_Data_Only <- displays todays funds' stats
        
        --Print_Investment_Refund_Calculation <- Prints actual results of investments,
            based on the amount of money invested
        
        --Quotations_Output_Format {CSV,JSON} <- accepts only CSV or JSON as an input.
            According to provided format Historical quotations will be saved.
            
        --Print_Refund_Analysis <- Prints refund analysis calculated,
            based on the payments, timing and invested money

.OUTPUTS
    None

.NOTES

    Version:            1.4
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      05-Feb-2024
    ChangeLog:

    Date            Who                     What
    2024-02-06      Stanislaw Horna         Command-line arguments modified.
                                            saveInvestmentHistoryDayByDay method added.
                                            Functions naming convention corrected.
                                            Downloading latest stats and historical quotation moved to __post_init__
    2024-02-07      Stanislaw Horna         Refactored class code. 
                                            Improved Investment stats.
                                            Displaying console results in tables
    2024-02-21      Stanisław Horna         Investments which are ended can be pulled from InvestmentDayByDay CSV file.
                                            Dedicated result presenting method for investments consisted of only 1 fund
    2024-03-12      Stanisław Horna         Analysis based on the payments, timing and invested money implemented

"""

import argparse
from Dependencies.Class_ListOfFund import ListOfFunds
from Dependencies.Class_InvestmentWallet import InvestmentWallet
from Dependencies.Function_config import *

programSynopsis = """
Program to download funds quotations and calculate profits of investments.
Without params program is creating report about todays funds' stats in JSON
and calculating investment refund day by day which is saved as CSV file.
"""

parser = argparse.ArgumentParser(description=programSynopsis)
parser.add_argument(
    "-l",
    "--Print_Latest_Fund_Data",
    action="store_true",
    help="Prints current fund's details.",
)
parser.add_argument(
    "-i",
    "--Print_Investment_Refund_Calculation",
    action="store_true",
    help="Prints actual results of investments based on the time and amount of money invested.",
)
parser.add_argument(
    "-a",
    "--Print_Refund_Analysis",
    action="store_true",
    help="Prints refund analysis calculated, based on the payments, timing and invested money.",
)
parser.add_argument(
    "--Quotations_Output_Format",
    choices=["CSV", "JSON"],
    help="Define file type in which historical fund quotations will be saved.",
)


def main(options):

    setCorrectPath()

    config = getConfiguration()

    Funds = ListOfFunds(config[FundsToCheckURLsKey])
    Funds.saveTodaysResults(config[DailyReportDirectoryName])

    printLatestFundData(Funds, options)
    saveHistoricalQuotations(
        Funds,
        config["HistoricalQuotationDirectoryName"],
        options
    )

    if os.path.isfile(config[InvestmentsFilePathKey]):
        investments: InvestmentWallet = InvestmentWallet(
            InvestmentsFilePath=config[InvestmentsFilePathKey],
            FundsList=Funds
        )

        investments.saveInvestmentHistoryDayByDay(
            config[InvestmentHistoryDayByDayDirectory]
        )

        printInvestmentRefundCalculation(investments, options)

        printRefundAnalysis(investments, options)

    exit(0)


def setCorrectPath() -> None:
    
    file_path = os.path.realpath(__file__)
    file_path = "/".join(file_path.split("/")[:-1])
    os.chdir(file_path)

    return None


def printLatestFundData(Funds: ListOfFunds, options: argparse.Namespace) -> None:
    
    # Check if appropriate param was used
    if options.Print_Latest_Fund_Data:
        
        Funds.printFundInfo()

    return None


def saveHistoricalQuotations(Funds: ListOfFunds, destinationDir: str, options: argparse.Namespace) -> None:
    
    # Check if appropriate param was used
    if options.Quotations_Output_Format == "JSON":
        
        Funds.saveQuotationJSON(destinationDir)

    # Check if appropriate param was used
    if options.Quotations_Output_Format == "CSV":
        
        Funds.saveQuotationCSV(destinationDir)

    return None


def printInvestmentRefundCalculation(investments: InvestmentWallet, options: argparse.Namespace) -> None:

    # Check if appropriate param was used
    if options.Print_Investment_Refund_Calculation:

        investments.printInvestmentResults()

    return None


def printRefundAnalysis(investments: InvestmentWallet, options: argparse.Namespace) -> None:

    # Check if appropriate param was used
    if options.Print_Refund_Analysis:

        investments.printRefundAnalysis()

    return None


# Run only if this file is called
if __name__ == "__main__":

    # invoke main function with parser args
    main(parser.parse_args())
