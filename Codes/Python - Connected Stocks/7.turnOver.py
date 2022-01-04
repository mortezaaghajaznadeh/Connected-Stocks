#%%
from numpy.lib.shape_base import split
import pandas as pd
import re
from numpy import log as ln
import numpy as np


def convert_ar_characters(input_str):

    mapping = {
        "ك": "ک",
        "گ": "گ",
        "دِ": "د",
        "بِ": "ب",
        "زِ": "ز",
        "ذِ": "ذ",
        "شِ": "ش",
        "سِ": "س",
        "ى": "ی",
        "ي": "ی",
    }
    return _multiple_replace(mapping, input_str)


def _multiple_replace(mapping, text):
    pattern = "|".join(map(re.escape, mapping.keys()))
    return re.sub(pattern, lambda m: mapping[m.group()], str(text))


#%%
# path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\\"
path = r"E:\RA_Aghajanzadeh\Data\\"
# %%
df = pd.read_parquet(path + "Cleaned_Stock_Prices_14001006.parquet")
df = df[df.group_name != "صندوق سرمایه گذاری قابل معامله"]
df = df.sort_values(by=["name", "jalaliDate"]).rename(columns={"name": "symbol"})
df["stock_id"] = df.stock_id.astype(float)
df["close_price"] = df.close_price.astype(float)
df["date"] = df.date.astype(int)
df["volume"] = df.volume.astype(float)
df = df[df.volume > 0]
df = df[~df.title.str.startswith("ح .")]
df = df[~df.title.str.startswith("ح.")]

# %%
sdf = pd.read_csv(path + "SymbolShrout_1400_10_06.csv")
sdf = sdf.set_index(["date", "name"])
mapdict = dict(zip(sdf.index, sdf.shrout))
df["date"] = df.date.astype(int)
df["shrout"] = df.set_index(["date", "symbol"]).index.map(mapdict)
df.isnull().sum()
# %%
df = df[~df.shrout.isnull()]
df["year"] = round(df.jalaliDate / 1e4, 0)
df["year"] = df["year"].astype(int)

# %%
def BG(df, path):
    # pathBG = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Control Right - Cash Flow Right\\"
    # pathBG = r"C:\Users\RA\Desktop\RA_Aghajanzadeh\Data\\"
    n = path + "Grouping_CT.xlsx"
    BG = pd.read_excel(n)
    uolist = (
        BG[BG.listed == 1]
        .groupby(["uo", "year"])
        .filter(lambda x: x.shape[0] >= 3)
        .uo.unique()
    )
    print(len(BG))
    BG = BG[BG.uo.isin(uolist)]
    print(len(BG))
    BGroup = set(BG["uo"])
    names = sorted(BGroup)
    ids = range(len(names))
    mapingdict = dict(zip(names, ids))
    BG["BGId"] = BG["uo"].map(mapingdict)

    BG = BG.groupby(["uo", "year"]).filter(lambda x: x.shape[0] > 3)
    for i in ["uo", "cfr", "cr", "position", "centrality"]:
        print(i)
        fkey = zip(list(BG.symbol), list(BG.year))
        mapingdict = dict(zip(fkey, BG[i]))
        df[i] = df.set_index(["symbol", "year"]).index.map(mapingdict)
    return df


df = BG(df, path)
#%%
df["Grouped"] = 1
df.loc[df.uo.isnull(), "Grouped"] = 0
# %%
df["volume"] = df["volume"].astype(float)
df["value"] = df["value"].astype(float)
df["marketCap"] = df.close_price * df.shrout
# df["return"] = df.groupby("symbol").close_price.pct_change()

df["Amihud_volume"] = ln(abs(df["return"]) / df.volume)
df["TurnOver"] = ln(df.volume / df.marketCap)
df["Amihud_value"] = ln(abs(df["return"]) / df.value)
df = df[(df.Amihud_value < 1e10) & (df.Amihud_value > -1e10)]
gg = df.groupby("symbol")
df["DeltaTrun"] = gg["TurnOver"].diff()
# df["Delta_Amihud_volume"] = gg["Amihud_volume"].diff()
df["Delta_Amihud_value"] = gg["Amihud_value"].diff()

# %%
df = df[df.jalaliDate > 13900000].reset_index(drop=True)
gg = df.groupby("date")
# g = gg.get_group(20081207)
# print(g.name)


def groupDaily(sg):
    sg["weight"] = sg.marketCap * sg.cr
    sg["weight"] = sg["weight"] / sg["weight"].sum()
    sg["weight_JustMarket"] = sg["marketCap"] / sg["marketCap"].sum()

    for i in ["", "_JustMarket"]:
        sg["Delta" + i] = (sg["weight" + i] * sg["DeltaTrun"]).sum()
        sg["Delta_Amihud_value" + i] = (
            sg["weight" + i] * sg["Delta_Amihud_value"]
        ).sum()
    sg["number"] = len(sg)
    return sg


def IndustryDaily(sg):
    sg["weight"] = sg["marketCap"] / sg["marketCap"].sum()
    for i in [""]:
        sg["Delta" + i] = (sg["weight" + i] * sg["DeltaTrun"]).sum()
        # sg["Delta_Amihud_volume" + i] = (
        #     sg["weight" + i] * sg["Delta_Amihud_volume"]
        # ).sum()
        sg["Delta_Amihud_value" + i] = (
            sg["weight" + i] * sg["Delta_Amihud_value"]
        ).sum()
    return sg


def Daily(g):
    print(g.name)
    g["weight"] = g.marketCap / g.marketCap.sum()
    g["DeltaMarket"] = (g["weight"] * g["DeltaTrun"]).sum()
    # g["Delta_Amihud_volumeMarket"] = (g["weight"] * g["Delta_Amihud_volume"]).sum()
    g["Delta_Amihud_valueMarket"] = (g["weight"] * g["Delta_Amihud_value"]).sum()
    g["DeltaMarket_Equall"] = g["DeltaTrun"].mean()
    sgg = g.groupby("uo")
    t = sgg.apply(groupDaily).set_index("uo")
    if len(t) > 0:
        for i in [
            "weight",
            "weight_JustMarket",
            "number",
            "Delta",
            "Delta_JustMarket",
            "Delta_Amihud_value",
            "Delta_Amihud_value_JustMarket",
        ]:

            # "Delta_Amihud_volume",
            # "Delta_Amihud_volume_JustMarket",
            mapdict = dict(zip(t.index, t[i]))
            g[i + "Group"] = g.uo.map(mapdict)
    else:
        for i in [
            "weight",
            "weight_JustMarket",
            "number",
            "Delta",
            "Delta_JustMarket",
            "Delta_Amihud_value",
            "Delta_Amihud_value_JustMarket",
        ]:
            g[i + "Group"] = np.nan
    t = sgg.DeltaTrun.mean().to_frame()
    mapdict = dict(zip(t.index, t["DeltaTrun"]))
    g["DeltaGroup_Equall"] = g.uo.map(mapdict)
    sgg = g.groupby("group_name")
    t = sgg.apply(IndustryDaily).set_index("group_name")
    for i in [
        "weight",
        "Delta",
        "Delta_Amihud_value",
    ]:

        # "Delta_Amihud_volume",
        mapdict = dict(zip(t.index, t[i]))
        g[i + "Industry"] = g.group_name.map(mapdict)
    return g


a = gg.apply(Daily)
#%%
df = a
df = df[~df.DeltaTrun.isnull()]
# %%
result = pd.DataFrame()
result = result.append(df)

result["DeltaGroup"] = (result.DeltaGroup - result.weightGroup * result.DeltaTrun) / (
    1 - result.weightGroup
)
result["Delta_JustMarketGroup"] = (
    result.Delta_JustMarketGroup - result.weight_JustMarketGroup * result.DeltaTrun
) / (1 - result.weight_JustMarketGroup)
result["DeltaGroup_Equall"] = (
    result.DeltaGroup_Equall - result.DeltaTrun / result.numberGroup
) / (1 - 1 / df.numberGroup)
result["Delta_Amihud_valueGroup"] = (
    df.Delta_Amihud_valueGroup - result.weightGroup * result.Delta_Amihud_value
) / (1 - result.weightGroup)
result["Delta_Amihud_value_JustMarketGroup"] = (
    result.Delta_Amihud_value_JustMarketGroup
    - result.weight_JustMarketGroup * result.Delta_Amihud_value
) / (1 - result.weight_JustMarketGroup)


result["DeltaIndustry"] = (
    result.DeltaIndustry - result.weightIndustry * result.DeltaTrun
) / (1 - result.weightIndustry)

result["Delta_Amihud_valueIndustry"] = (
    df.Delta_Amihud_valueIndustry - result.weightIndustry * result.Delta_Amihud_value
) / (1 - result.weightIndustry)
#%%


import requests


def removeSlash(row):
    X = row.split("/")
    if len(X[1]) < 2:
        X[1] = "0" + X[1]
    if len(X[2]) < 2:
        X[2] = "0" + X[2]

    return int(X[0] + X[1] + X[2])


def Overall_index():
    url = (
        r"http://www.tsetmc.com/tsev2/chart/data/Index.aspx?i=32097828799138957&t=value"
    )
    r = requests.get(url)
    jalaliDate = []
    Value = []
    for i in r.text.split(";"):
        x = i.split(",")
        jalaliDate.append(x[0])
        Value.append(float(x[1]))
    df = pd.DataFrame(
        {
            "jalaliDate": jalaliDate,
            "Value": Value,
        },
        columns=["jalaliDate", "Value"],
    )
    df["jalaliDate"] = df.jalaliDate.apply(removeSlash)
    return df


market = Overall_index()

market["Mreturn"] = market["Value"].pct_change()
market["lagMreturn"] = market["Mreturn"].shift()
market["leadMreturn"] = market["Mreturn"].shift(-1)
for i in ["Mreturn", "lagMreturn", "leadMreturn"]:
    print(i)
    mapdict = dict(zip(market.jalaliDate, market[i]))
    result[i] = result.jalaliDate.map(mapdict)

#%%
result = result.rename(
    columns={
        "Delta_Amihud_valueIndustry": "Delta_Amihud_Industry",
        "Delta_Amihud_valueGroup": "Delta_Amihud_Group",
        "Delta_Amihud_value_JustMarketGroup": "Delta_Amihud_JustMarketGroup",
        "Delta_Amihud_valueMarket": "Delta_Amihud_Market",
        "Delta_Amihud_value": "Delta_Amihud",
    }
)

#%%
mlist = result.symbol.unique()
mapdict = dict(zip(mlist, range(len(mlist))))
result["id"] = result.symbol.map(mapdict)
mlist = result.date.unique()
mapdict = dict(zip(mlist, range(len(mlist))))
result["t"] = result.date.map(mapdict)
# %%
result["month"] = ((result.jalaliDate.astype(int) - result.year * 1e4) / 100).astype(
    int
)
result[["jalaliDate", "month", "year"]]
#%%
result["yearmonth"] = result.year.astype(str) + "-" + result.month.astype(str)
#%%
result["idyear"] = result["id"].astype(str) + "-" + result["yearmonth"].astype(str)
mlist = result.idyear.unique()
mapdict = dict(zip(mlist, range(len(mlist))))
result["regidyear"] = result.idyear.map(mapdict)
result
# %%
mlist = [
    "DeltaMarket",
    "Delta_Amihud_Market",
    "DeltaGroup",
    "Delta_JustMarketGroup",
    "Delta_Amihud_Group",
    "Delta_Amihud_JustMarketGroup",
    "DeltaIndustry",
    "Delta_Amihud_Industry",
]
gg = result.groupby("id")
for i in mlist:
    print(i)
    result["lag" + i] = gg[i].shift()
    result["lead" + i] = gg[i].shift(-1)
result = result.rename(
    columns={
        "lagDelta_Amihud_JustMarketGroup": "lagDelta_Amihud_MarketGroup",
        "leadDelta_Amihud_JustMarketGroup": "leadDelta_Amihud_MarketGroup",
    }
)

#%%
result.to_csv(path + "\Connected_Stocks\TurnOver_1400_10_06.csv", index=False)
#%%