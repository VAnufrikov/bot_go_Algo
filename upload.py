import pandas as pd

from moexalgo import Ticker

def read_data_stock():
    """Подготавливаем датасет со всеми компаниями ан московской бирже"""
    df = pd.read_csv('ListingSecurityList.csv', engine="python", encoding="cp1251", sep=";")

    df = df[
        [
            "TRADE_CODE",
            "EMITENT_FULL_NAME",
            "INSTRUMENT_TYPE",
            "LIST_SECTION",
            "INSTRUMENT_CATEGORY",
            "CURRENCY",
            "NOMINAL",
            "ISSUE_AMOUNT",
        ]
    ]

    # Берем только акции#
    df = df[
        (df["INSTRUMENT_TYPE"] == "Акция обыкновенная")
        | (df["INSTRUMENT_TYPE"] == "Акции иностранного эмитента")
        ]

    return df.reset_index(drop=True)


def upload_data_from_moexalgo(TRADE_CODE, DATE_START, DATE_END):
    """Получаем данные по TRADE_CODE из moexalgo"""
    tiket = Ticker(TRADE_CODE)

    print("start upload_data_from_moexalgo")

    tradestats = pd.DataFrame(tiket.tradestats(date=DATE_START, till_date=DATE_END))
    print("tradestats ready")

    orderstats = pd.DataFrame(tiket.orderstats(date=DATE_START, till_date=DATE_END))
    print("orderstats ready")

    obstats = pd.DataFrame(tiket.obstats(date=DATE_START, till_date=DATE_END))
    print("obstats ready")

    obstats["ts"] = pd.to_datetime(obstats["ts"], format="%Y-%m-%d %H:%M")
    orderstats["ts"] = pd.to_datetime(orderstats["ts"], format="%Y-%m-%d %H:%M")
    tradestats["ts"] = pd.to_datetime(tradestats["ts"], format="%Y-%m-%d %H:%M")


    obstats.rename(columns={"secid": "ticker"}, inplace=True)


    orderstats.rename(columns={"secid": "ticker"}, inplace=True)


    tradestats.rename(columns={"secid": "ticker"}, inplace=True)


    return tradestats, orderstats, obstats

