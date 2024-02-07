# Investment_fund_quotations
    Program to download funds quotations from website Analizy.pl, based on URLs provided in CONFIG.json.
    Additionally it will calculate profit of investments defined in Investments.json.
    Without params program is creating report about todays funds' stats in JSON

# Sample Console output
### Fund's stats for today (-l param)
    | Name                             | ID    | Price      | ValueChange   | PercentChange   | LastUpdate   |
    |----------------------------------|-------|------------|---------------|-----------------|--------------|
    | Goldman Sachs Stable Growth      | ING07 | 324.53 PLN | +0.60 PLN     | +0.19 %         | 06.02.2024   |
    | Goldman Sachs Sustainable        | ING02 | 432.08 PLN | +1.03 PLN     | +0.24 %         | 06.02.2024   |
    | Generali Savings                 | UNI32 | 143.93 PLN | +0.09 PLN     | +0.06 %         | 06.02.2024   |
    | Investor Savings                 | DWS05 | 295.58 PLN | +0.24 PLN     | +0.08 %         | 06.02.2024   |

### Investments stats (-i param)
    | Investment Name   | Profit      | Refund Rate   | Days   | Profit per day   | Refund per day   | Fund ID   | Investment %   | Fund profit   | Fund refund %   | Last Change %   |
    |-------------------|-------------|---------------|--------|------------------|------------------|-----------|----------------|---------------|-----------------|-----------------|
    | Savings           | +403.09 PLN | +0.40 %       | 13.00  | +31.01 PLN       | +0.03 %          | -         | -              | -             | -               | -               |
    | -                 | -           | -             | -      | -                | -                | DWS05     | +50.22 %       | +225.30 PLN   | +0.44 %         | +0.08 %         |
    | -                 | -           | -             | -      | -                | -                | UNI32     | +50.17 %       | +177.79 PLN   | +0.35 %         | +0.06 %         |
    | Goldman           | +11.94 PLN  | +1.99 %       | 23.00  | +0.52 PLN        | +0.09 %          | -         | -              | -             | -               | -               |
    | -                 | -           | -             | -      | -                | -                | ING02     | +51.26 %       | +7.54 PLN     | +2.51 %         | +0.24 %         |
    | -                 | -           | -             | -      | -                | -                | ING07     | +50.73 %       | +4.40 PLN     | +1.47 %         | +0.19 %         |


# Configuration
    There are 2 config file:
        - CONFIG.json <- generic one which contains:
                            - wanted output directory names
                            - name with investments (Investments.json), which can be changed
                            - Funds to url to check
        
        - Investments.json <- investments definition to calculate profits and refund rates.

### CONFIG.json structure
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

### CONFIG.json structure
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
###
    Each fund selected in Investments.json must be included in CONFIG.json in section FundsToCheckURLs
    <Name_of_investment_wallet> <- User friendly name of funds set 
    <Fund_ID_X> <- Fund ID allocated under particular fund set,
        it can be read out from fund URL or run program with -l (--Print_Latest_Fund_Data) param
    <Date_when_fund_was_bought> <- Date when fund was bought
    <Amount_allocated_for_the_purchase> <- amount of money used to buy particular fund