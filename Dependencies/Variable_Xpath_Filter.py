"""
.DESCRIPTION
    File with xpath filters used to read out from www.analizy.pl website following fund properties:
        - price
        - currency
        - last update Date
        - Change percentage since last day
        - Change value since last day
    
.NOTES

    Version:            1.0
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      07-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
global xpathFilter_Price
global xpathFilter_Currency
global xpathFilter_UpdateDate
global xpathFilter_ChangePercentage1D
global xpathFilter_ChangeValue1D

xpathFilter_Price = '//span[@class="productBigText"]/text()'
xpathFilter_Currency = '//div[@class="primaryContent"]/text()'
xpathFilter_UpdateDate = '//p[@class="lightProductText"]/text()'
xpathFilter_ChangePercentage1D = '//p[@class="productValueChange"]/text()'
xpathFilter_ChangeValue1D = '//p[@class="productValueChange"]/text()'