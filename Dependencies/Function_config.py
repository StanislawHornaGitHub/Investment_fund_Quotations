"""
.DESCRIPTION
    getConfiguration
        Function to read config file.

    checkIfConfigFileExists
        Function to check if config file exists.
        
    createFolderIfNotExists
        Function to check if desired folder exists, if not it will create it.

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
import os

# Custom created variables modules
from Dependencies.Variables_Config import *


# Function to read config file
def getConfiguration(options):
    checkIfConfigFileExists()

    # Read and load config file to the variable which is later returned
    with open(configFilePath, "r") as configFile:
        configuration = json.loads("\n".join(configFile.readlines()))

    # If Directories for outputs is provided create required folder
    if configuration[HistoricalQuotationDirectoryNameKey]:
        createFolderIfNotExists(configuration[HistoricalQuotationDirectoryNameKey])

    if configuration[DailyReportDirectoryName]:
        createFolderIfNotExists(configuration[DailyReportDirectoryName])

    if configuration[InvestmentHistoryDayByDayDirectory]:
        createFolderIfNotExists(configuration[InvestmentHistoryDayByDayDirectory])

    return configuration


# Function to check if config file exists
def checkIfConfigFileExists():
    # If config file does not exist raise an error
    if not os.path.isfile(configFilePath):
        raise Exception("Config file does not exist")


# Function to check if desired folder exists, if not it will create it
def createFolderIfNotExists(folderPath):
    # if destination directory does not exist create it
    if not os.path.exists(folderPath):
        try:
            os.makedirs(folderPath)
        except:
            raise Exception("Cannot create output folder")
