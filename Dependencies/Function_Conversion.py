"""
.DESCRIPTION
    convertNumericToStrPlsMnsSigns
        Function to convert Number values to string with + and - signs accordingly
        if number is greater or equal to 0 or less than 0
        additionally function adds currency suffix and % sign to selected fields
    
.NOTES

    Version:            1.0
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_quotations
    Creation Date:      07-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
# Function to convert Number values to string with + and - signs accordingly
# if number is greater or equal to 0 or less than 0
# additionally function adds currency suffix and % sign to selected fields
def convertNumericToStrPlsMnsSigns(
    inputValues: list,
    headers: list,
    columnsExcludedFromSigns: list,
    currencyColumnNames: list,
    currency: str,
    percentageColumnNames: list,
) -> list:

    # loop through values
    for i in range(0, len(inputValues)):

        # try to cast value to float if it throws and error continue to next value
        try:
            inputValues[i] = float(inputValues[i])
        except:
            continue

        # check if value is greater or equal to 0 and it is not included in excluded columns list
        if inputValues[i] >= 0 and headers[i] not in columnsExcludedFromSigns:
            # add "+" sign before, format number to display 2 decimal digits and cast it to string
            inputValues[i] = "+" + str("{:4.2f}".format(inputValues[i]))
        else:
            # format number to display 2 decimal digits and cast it to string
            inputValues[i] = str("{:4.2f}".format(inputValues[i]))

        if headers[i] in currencyColumnNames:
            # if column is an currency one add currency suffix
            inputValues[i] += f" {currency}"
        elif headers[i] in percentageColumnNames:
            # if column is an percentage one add percentage sign
            inputValues[i] += " %"

    return inputValues
