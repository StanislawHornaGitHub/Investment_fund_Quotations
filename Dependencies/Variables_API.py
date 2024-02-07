"""
.DESCRIPTION
    File with www.analizy.pl API related variables to correctly read out response content

.NOTES

    Version:            1.0
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      07-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
global analizyplQuotationAPI
global analizyplAPIresponse_ID
global analizyplAPIresponse_Currency
global analizyplAPIresponse_QuotationDetails
global analizyplAPIresponse_QuotationList
global analizyplAPIresponse_QuotationDate
global analizyplAPIresponse_QuotationValue

analizyplQuotationAPI = "https://www.analizy.pl/api/quotation"
analizyplAPIresponse_ID = "id"
analizyplAPIresponse_Currency = "currency"
analizyplAPIresponse_QuotationDetails = "series"
analizyplAPIresponse_QuotationList = "price"
analizyplAPIresponse_QuotationDate = "date"
analizyplAPIresponse_QuotationValue = "value"