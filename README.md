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
    ┌───────────────────┬────────┬───────────┬────────────────┬─────────────┬───────────────┬────────────────┬────────────────┬─────────────────┐
    │ Investment Name   │ Days   │ Fund ID   │ Investment %   │ Profit      │ Refund Rate   │ Profit daily   │ Refund daily   │ Refund yearly   │
    ├───────────────────┼────────┼───────────┼────────────────┼─────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │ Savings           │ 26.00  │           │                │ +720.51 PLN │ +0.71 %       │ +27.71 PLN     │ +0.03 %        │ +9.92 %         │
    ├───────────────────┼────────┼───────────┼────────────────┼─────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                   │        │ DWS05     │ 49.99 %        │ +353.91 PLN │ +0.69 %       │ +13.61 PLN     │ +0.03 %        │ +9.69 %         │
    ├───────────────────┼────────┼───────────┼────────────────┼─────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                   │        │ UNI32     │ 50.01 %        │ +366.60 PLN │ +0.72 %       │ +14.10 PLN     │ +0.03 %        │ +10.11 %        │
    ├───────────────────┼────────┼───────────┼────────────────┼─────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                   │        │           │                │             │               │                │                │                 │
    ├───────────────────┼────────┼───────────┼────────────────┼─────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │ Goldman           │ 36.00  │           │                │ +16.19 PLN  │ +2.70 %       │ +0.45 PLN      │ +0.07 %        │ +27.36 %        │
    ├───────────────────┼────────┼───────────┼────────────────┼─────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                   │        │ ING02     │ 50.37 %        │ +10.36 PLN  │ +3.45 %       │ +0.29 PLN      │ +0.10 %        │ +34.98 %        │
    ├───────────────────┼────────┼───────────┼────────────────┼─────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                   │        │ ING07     │ 49.63 %        │ +5.83 PLN   │ +1.94 %       │ +0.16 PLN      │ +0.05 %        │ +19.67 %        │
    └───────────────────┴────────┴───────────┴────────────────┴─────────────┴───────────────┴────────────────┴────────────────┴─────────────────┘

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