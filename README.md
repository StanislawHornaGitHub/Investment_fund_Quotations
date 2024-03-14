# Investment_fund_quotations
    Program to download funds quotations from website Analizy.pl, based on URLs provided in CONFIG.json.
    Additionally it will calculate profit of investments defined in Investments.json.
    Without params program is creating report about todays funds' stats in JSON

# Sample Console output
### Fund's stats for today (-l param)

Displays latest funds' stats

    | Name                        | ID    | Price      | ValueChange   | PercentChange   | LastUpdate   |
    |-----------------------------|-------|------------|---------------|-----------------|--------------|
    | Generali Savings            | UNI32 | 145.16 PLN | +0.03 PLN     | +0.02 %         | 13.03.2024   |
    | Investor Savings            | DWS05 | 297.74 PLN | +0.03 PLN     | +0.01 %         | 13.03.2024   |
    | Goldman Sachs Japan         | ING43 | 356.97 PLN | -4.66 PLN     | -1.29 %         | 13.03.2024   |
    | Pzu Global Corporate Bonds  | PZU40 | 62.96 PLN  | +0.00 PLN     | +0.00 %         | 13.03.2024   |
    | Pzu Safe                    | PZU45 | 78.06 PLN  | +0.00 PLN     | +0.00 %         | 13.03.2024   |
    | Pzu Short-Term Bonds        | PZU79 | 92.27 PLN  | -0.01 PLN     | -0.01 %         | 13.03.2024   |

### Investments stats (-i param)

Prints actual results of investments,
based on the amount of money invested. Percentage values are sum of all invested money
divided by investment value for latest quotation.

    ┌──────────────────────────┬────────┬───────────┬────────────────┬──────────────┬───────────────┬────────────────┬────────────────┬─────────────────┐
    │ Investment Name          │ Days   │ Fund ID   │ Investment %   │ Profit       │ Refund Rate   │ Profit daily   │ Refund daily   │ Refund yearly   │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │ Savings                  │ 47.00  │           │                │ +1215.50 PLN │ +1.19 %       │ +25.86 PLN     │ +0.03 %        │ +9.25 %         │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │ DWS05     │ 49.99 %        │ +600.00 PLN  │ +1.18 %       │ +12.77 PLN     │ +0.03 %        │ +9.16 %         │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │ UNI32     │ 50.01 %        │ +615.50 PLN  │ +1.21 %       │ +13.10 PLN     │ +0.03 %        │ +9.40 %         │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │           │                │              │               │                │                │                 │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │ Japan                    │ 19.00  │ ING43     │ 100.00 %       │ -29.30 PLN   │ -1.47 %       │ -1.54 PLN      │ -0.08 %        │ -28.14 %        │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │           │                │              │               │                │                │                 │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │ PZU funds                │ 13.00  │           │                │ +26.78 PLN   │ +0.26 %       │ +2.06 PLN      │ +0.02 %        │ +7.16 %         │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │ PZU40     │ 33.40 %        │ +16.04 PLN   │ +0.46 %       │ +1.23 PLN      │ +0.04 %        │ +12.92 %        │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │ PZU45     │ 33.31 %        │ +6.61 PLN    │ +0.19 %       │ +0.51 PLN      │ +0.01 %        │ +5.33 %         │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │ PZU79     │ 33.29 %        │ +4.13 PLN    │ +0.12 %       │ +0.32 PLN      │ +0.01 %        │ +3.37 %         │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │                          │        │           │                │              │               │                │                │                 │
    ├──────────────────────────┼────────┼───────────┼────────────────┼──────────────┼───────────────┼────────────────┼────────────────┼─────────────────┤
    │ (Arch.) Goldman          │ 34.00  │           │                │ +16.19 PLN   │ +2.70 %       │ +0.48 PLN      │ +0.08 %        │ +28.97 %        │
    └──────────────────────────┴────────┴───────────┴────────────────┴──────────────┴───────────────┴────────────────┴────────────────┴─────────────────┘

### Refund analysis (-a param)

Prints calculated refund analysis,
based on the payments, timing and invested money. Represents the weighted average,
where all investment duration is divided in buckets between each buy or sell request,
the refund is calculated based on fund price at the start and end of the bucket, 
the weight for each result is duration of the bucket and owned participation units.
Owned participation units are cumulative sum of all units including those from previous buckets.


    | Name                        | FundID   |   Refund_% |   RefundPerDay_% |   RefundYearly_% |
    |-----------------------------|----------|------------|------------------|------------------|
    | Generali Savings            | DWS05    |  1.17523   |       0.0226007  |          8.24924 |
    | Investor Savings            | UNI32    |  1.20589   |       0.02461    |          8.98266 |
    | Goldman Sachs Japan         | ING43    | -1.33114   |      -0.073952   |        -26.9925  |
    | Pzu Global Corporate Bonds  | PZU40    |  0.3461    |       0.0288417  |         10.5272  |
    | Pzu Safe                    | PZU45    |  0.130571  |       0.0108809  |          3.97154 |
    | Pzu Short-Term Bonds        | PZU79    |  0.0664023 |       0.00553353 |          2.01974 |

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

### Investments.json structure
    {
        "<Name_of_investment_wallet>": {
            "StartDate": "<yyyy-MM-dd>",
            "EndDate":  "<yyyy-MM-dd>",
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
            "StartDate": "<yyyy-MM-dd>",
            "EndDate":  "<yyyy-MM-dd>",
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