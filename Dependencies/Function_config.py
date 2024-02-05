import json
import os

global FundsToCheckURLsKey
global HistoricalQuotationDirectoryNameKey
global InvestmentsFilePathKey

FundsToCheckURLsKey = "FundsToCheckURLs"
HistoricalQuotationDirectoryNameKey = "HistoricalQuotationDirectoryName"
InvestmentsFilePathKey = "InvestmentsFilePath"

configFilePath = "CONFIG.json"

def getConfiguration(options):
    checkIfConfigFileExists()
    with open(configFilePath,"r") as configFile:
        configuration = json.loads("\n".join(configFile.readlines()))
        
    if configuration[HistoricalQuotationDirectoryNameKey]:
        createFolderIfNotExists(configuration[HistoricalQuotationDirectoryNameKey], options)
    
    return configuration

def checkIfConfigFileExists():
    if not os.path.isfile(configFilePath):
        raise Exception("Config file does not exist")

def createFolderIfNotExists(folderPath, options):    
    if options.Quotations_Output_Format == None:
        return
    if not os.path.exists(folderPath):
        try:
            os.makedirs(folderPath)
        except:
            raise Exception("Cannot create output folder")
