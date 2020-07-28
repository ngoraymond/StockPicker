#FROM PICKER

    #Dataframe version grpBy.groupby('sector')
    by_sector = itertools.groupby(stock_dict, sectorFunc)
    for x in by_sector:
        listOfStocks = list(x[1])
        print(listOfStocks[0]['sector'])
        for y in listOfStocks:
            print(y['shortName'])