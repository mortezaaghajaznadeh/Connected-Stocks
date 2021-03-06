#%%
import pandas as pd
import numpy as np
import re


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

path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Connected stocks\\"


n1 = path + "MonthlyNormalzedFCAP7.1" + ".parquet"
df1 = pd.read_parquet(n1)
df = pd.read_parquet(path + "Holder_Residual.parquet")
time = df[["date", "jalaliDate"]].drop_duplicates()
#%%
df["id"] = df.id.astype(int)
mapdict = dict(zip(df.id, df.symbol))
df1["id_x"] = df1.id_x.astype(int)
df1["id_y"] = df1.id_y.astype(int)
df1["symbol_x"] = df1.id_x.map(mapdict)
df1["symbol_y"] = df1.id_y.map(mapdict)
df1[["symbol_x", "symbol_y"]].isnull().sum()
#%%

df1 = df1[df1.id_x != df1.id_y]
# %%
path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\\"
n = path + "IRX6XTPI0009.xls"
Index = pd.read_excel(n)

Index["YearMonth"] = (Index["<DTYYYYMMDD>"] / 100).round(0)
Index["YearMonth"] = Index["YearMonth"].astype(int)
Index["YearMonth"] = Index["YearMonth"].astype(str)
Index = Index[["YearMonth", "<CLOSE>"]]
Index = Index.drop_duplicates(subset="YearMonth", keep="last")
Index["change"] = Index["<CLOSE>"].pct_change() * 100
Index["Bullish"] = 0
Index["Bearish"] = 0
Index = Index.replace(np.nan, -1.709737)
Index["change"] = Index.change.shift(-1)

Index.loc[Index.change >= 2, "Bullish"] = 1
Index.loc[Index.change <= -2, "Bearish"] = 1

mapdict = dict(zip(Index.YearMonth, Index.Bullish))
df1["Bullish"] = df1["Year_Month"].map(mapdict)
mapdict = dict(zip(Index.YearMonth, Index.Bearish))
df1["Bearish"] = df1["Year_Month"].map(mapdict)
print(len(df1))
df1 = df1[df1.jalaliDate < 13990000]
df1.isnull().sum()
print(len(df1))
# %%
path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Connected stocks\\"
BGId = pd.read_csv(path + "BGId.csv")
mapdict = dict(zip(BGId.BGId, BGId.uo))
df1["uo_x"] = df1["BGId_x"].map(mapdict)
mapdict = dict(zip(BGId.BGId, BGId.uo))
df1["uo_y"] = df1["BGId_y"].map(mapdict)
df1[["BGId_x", "BGId_y", "uo_x", "uo_y"]].isnull().sum()


#%%
pathBG = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Control Right - Cash Flow Right\\"
# pathBG = path
n = pathBG + "Grouping_CT.xlsx"
BG = pd.read_excel(n)
BG = BG[BG.listed == 1]
BG = BG.groupby(["uo", "year"]).filter(lambda x: x.shape[0] >= 3.0)
df1["year"] = round(df1.jalaliDate / 10000, 0)
df1["year"] = df1["year"].astype(int)


for t in BG.year.unique():
    print(t)
    tempt = BG[BG.year == t].uo.unique()
    df1.loc[(~(df1.uo_x.isin(tempt))) & (df1.year == t), "uo_x"] = np.nan
    df1.loc[(~(df1.uo_x.isin(tempt))) & (df1.year == t), "BGId_x"] = np.nan
    df1.loc[(~(df1.uo_y.isin(tempt))) & (df1.year == t), "uo_y"] = np.nan
    df1.loc[(~(df1.uo_y.isin(tempt))) & (df1.year == t), "BGId_y"] = np.nan

df1.isnull().sum()

# %%
BGId = (
    df1[["BGId_x", "uo_x"]]
    .drop_duplicates()
    .rename(columns={"BGId_x": "BGId", "uo_x": "uo"})
    .append(
        df1[["BGId_y", "uo_y"]]
        .drop_duplicates()
        .rename(columns={"BGId_y": "BGId", "uo_y": "uo"})
    )
    .drop_duplicates()
    .reset_index(drop=True)
    .sort_values(by="BGId")
)

bankingUo = [
    "وبصادر",
    "بانک ملی ایران",
    "وبملت",
    "دی",
    "وتجارت",
    "بانک مسکن",
    "بانک صنعت ومعدن",
    "بانک سپه",
]
bankingSymbol = [
    "وملت",
    "وسینا",
    "وپاسار",
    "وبملت",
    "وبصادر",
    "وتجارت",
    "وپست",
    "ومسکن",
    "وحکمت",
    "وزمین",
]
investmentSymbol = [
    "واعتبار",
    "وسپه",
    "ونیکی",
    "والبر",
    "وپترو",
    "وتوشه",
    "وغدیر",
    "ورنا",
    "وبانک",
    "ونفت",
    "وبیمه",
    "وصندوق",
    "وصنعت",
    "ومعادن",
    "وآردل",
    "وتوکا",
    "وبوعلی",
    "واتی",
    "وتوسم",
    "وامید",
    "ونیرو",
    "وساپا",
    "ودی",
    "وشمال",
    "وگستر",
    "وسکاب",
    "ولتجار",
    "وخارزم",
    "وکادو",
    "ومشان",
    "وآفر",
    "وبهمن",
    "وثوق",
    "وسنا",
    "وارس",
    "وجامی",
    "وآتوس",
    "وبرق",
    "وپسا",
    "وسبحان",
    "ومعین",
    "وپویا",
    "وایرا",
    "وآذر",
]
pathBG = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Control Right - Cash Flow Right\\"
# pathBG = path
n = pathBG + "Grouping_CT.xlsx"
DD = pd.read_excel(n)
bankinGroup = list(DD[DD.symbol.isin(bankingSymbol)]["uo"].unique())
invinGroup = list(DD[DD.symbol.isin(investmentSymbol)]["uo"].unique())

BGId["Bank in Group"] = 0
BGId.loc[BGId.uo.isin(bankinGroup), "Bank in Group"] = 1
BGId["Bank is UO"] = 0
BGId.loc[BGId.uo.isin(bankingUo), "Bank is UO"] = 1
BGId["Inv. in Group"] = 0
BGId.loc[BGId.uo.isin(invinGroup), "Inv. in Group"] = 1


mapdict = dict(zip(BGId["BGId"], BGId["Bank in Group"]))
df1["bankinGroup_x"] = df1.BGId_x.map(mapdict)
df1["bankinGroup_y"] = df1.BGId_y.map(mapdict)
mapdict = dict(zip(BGId["BGId"], BGId["Bank is UO"]))
df1["bankingUo_x"] = df1.BGId_x.map(mapdict)
df1["bankingUo_y"] = df1.BGId_y.map(mapdict)
mapdict = dict(zip(BGId["BGId"], BGId["Inv. in Group"]))
df1["invinGroup_x"] = df1.BGId_x.map(mapdict)
df1["invinGroup_y"] = df1.BGId_y.map(mapdict)

df1.isnull().sum()

# %%

df1 = df1[(df1.MonthlyFCAPf < 1) & (df1.WeeklyFCAPf < 1) & (df1.FCAPf < 1)]
gg = df1.groupby(["t_Month"])


def NormalTransform(df_sub):
    col = df_sub.rank(pct=True)
    return (col - col.mean()) / col.std()


df1["MonthlyFCAP*"] = gg["MonthlyFCAPf"].apply(NormalTransform)
df1["MonthlyFCA*"] = gg["MonthlyFCA"].apply(NormalTransform)


#%%

pathBG = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Control Right - Cash Flow Right\\"
# pathBG = path
n = pathBG + "Grouping_CT.xlsx"
BG = pd.read_excel(n)
BG = BG[BG.listed == 1]
BG = BG.groupby(["uo", "year"]).filter(lambda x: x.shape[0] >= 3.0)
BG = BG[BG.year >= 1394]
tt = BG[BG.year == 1397]
BG = BG.append(tt).reset_index(drop=True)

# %%

path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\\"

n2 = path + "\\balance sheet - 9811" + ".xlsx"
df2 = pd.read_excel(n2)
df2 = df2.iloc[:, [0, 4, 18]]


def vv(row):
    X = row.split("/")
    return int(X[0])


df2.rename(
    columns={
        df2.columns[0]: "symbol",
        df2.columns[1]: "jalaliDate",
        df2.columns[2]: "Capital",
    },
    inplace=True,
)
df2["year"] = df2["jalaliDate"].apply(vv)

df2["symbol"] = df2.symbol.apply(convert_ar_characters)

fkey = zip(df2.symbol, df2.year)
mapdict = dict(zip(fkey, df2.Capital))
BG["shrOut"] = BG.set_index(["symbol", "year"]).index.map(mapdict)
#%%
# path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\\"
# holder = pd.read_csv(path + "BlockHolders - 800308-990528 - Annual" + ".csv")
# gg = holder.groupby(['symbol','jalaliDate'])
# def s(g):
#     return g.nshares.sum()
# holder = gg.last()
# holder['shrOut'] = gg.apply(s)
# holder = holder.reset_index()
# holder = holder [['symbol', 'jalaliDate', 'year', 'shrOut']]
# fkey = zip(holder.symbol,holder.year)
# mapdict = dict(zip(fkey,holder.shrOut))
# BG['shrOut2'] = BG.set_index(['symbol','year']).index.map(mapdict)

#%%
path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\\"
price = pd.read_csv(path + "Stocks_Prices_1399-09-24" + ".csv")

price = price[["jalaliDate", "date", "name", "close_price"]]


def vv(row):
    X = row.split("-")
    return int(X[0])


price["year"] = price["jalaliDate"].apply(vv)
price = price.groupby(["name", "year"]).last().reset_index()
price["name"] = price.name.apply(convert_ar_characters)
fkey = zip(price.name, price.year)
mapdict = dict(zip(fkey, price.close_price))
BG["close"] = BG.set_index(["symbol", "year"]).index.map(mapdict)

#%%
len(BG[BG.close.isnull()].symbol.unique())
BG["MarketCap"] = BG["close"] * BG["shrOut"]
BG["uoMarketCap"] = BG["MarketCap"] * BG["cfr"]

gg = BG.groupby(["uo"])


def summary(Sg):
    number = Sg.size
    groupMC = Sg.MarketCap.sum()
    uoCFr = Sg.cfr.sum()
    uoCFrMC = Sg.uoMarketCap.sum()
    return pd.Series(data=[number, groupMC, uoCFr, uoCFrMC])


gg = BG.groupby(["uo", "year"])
sResult = gg.apply(summary).reset_index()
sResult = sResult.rename(
    columns={0: "Number", 1: "GroupMarketCap", 2: "Totalcfr", 3: "uoMarketCap"}
)


def Number(g):
    g["QuantileNumber"] = np.nan
    for i in range(1, 5):
        g.loc[
            g.Number >= g.Number.quantile(0.25 * (i - 1)),
            "QuantileNumber",
        ] = i
    return g


def GroupMarketCap(g):
    g["QuantileGroupMarketCap"] = np.nan
    for i in range(1, 5):
        g.loc[
            g.GroupMarketCap >= g.GroupMarketCap.quantile(0.25 * (i - 1)),
            "QuantileGroupMarketCap",
        ] = i
    return g


def Totalcfr(g):
    g["QuantileTotalcfr"] = np.nan
    for i in range(1, 5):
        g.loc[
            g.Totalcfr >= g.Totalcfr.quantile(0.25 * (i - 1)),
            "QuantileTotalcfr",
        ] = i
    return g


def uoMarketCap(g):
    g["QuantileuoMarketCap"] = np.nan
    for i in range(1, 5):
        g.loc[
            g.uoMarketCap >= g.uoMarketCap.quantile(0.25 * (i - 1)),
            "QuantileuoMarketCap",
        ] = i
    return g


gg = sResult.groupby("year")
sResult = gg.apply(Number)
gg = sResult.groupby("year")
sResult = gg.apply(GroupMarketCap)
gg = sResult.groupby("year")
sResult = gg.apply(Totalcfr)
gg = sResult.groupby("year")
sResult = gg.apply(uoMarketCap)

for t in [
    "QuantileNumber",
    "QuantileGroupMarketCap",
    "QuantileTotalcfr",
    "QuantileuoMarketCap",
]:
    fkey = zip(sResult.uo, sResult.year)
    mapdict = dict(zip(fkey, sResult[t]))
    BG[t] = BG.set_index(["uo", "year"]).index.map(mapdict)

#%%
df1["year"] = round(df1.jalaliDate / 10000, 0)
df1["year"] = df1["year"].astype(int)
for t in [
    "QuantileNumber",
    "QuantileGroupMarketCap",
    "QuantileTotalcfr",
    "QuantileuoMarketCap",
]:
    print(t)
    fkey = zip(BG.uo, BG.year)
    mapdict = dict(zip(fkey, BG[t]))
    df1[t + "_x"] = df1.set_index(["uo_x", "year"]).index.map(mapdict)

    fkey = zip(BG.uo, BG.year)
    mapdict = dict(zip(fkey, BG[t]))
    df1[t + "_y"] = df1.set_index(["uo_y", "year"]).index.map(mapdict)


# for t in ['QuantileNumber',
#           'QuantileGroupMarketCap',
#           'QuantileTotalcfr',
#        'QuantileuoMarketCap']:
#     df1[t+"_x"] = df1.groupby('id')[t+"_x"].fillna(method = 'ffill')
#     df1[t+"_y"] = df1.groupby('id')[t+"_y"].fillna(method = 'ffill')

#%%

n = path + "Holder_Residual.parquet"
df = pd.read_parquet(n)
SId = df[["id", "symbol"]].drop_duplicates().reset_index(drop=True)

SData = (
    df.groupby("symbol")[["Percentile_Rank"]]
    .mean()
    .sort_values(by=["Percentile_Rank"])
    .reset_index()
)
SData = SData.merge(SId)
SData["Rank"] = SData.Percentile_Rank.rank()
SData["GRank"] = 0
for i in range(9):
    t = i + 1
    tempt = (SData["Rank"].max()) / 10
    SData.loc[SData["Rank"] > tempt * t, "GRank"] = t


for a in [df1]:
    mapingdict = dict(zip(SData.id, SData.GRank))
    a["id_x"] = a["id_x"].astype(int)
    a["id_y"] = a["id_y"].astype(int)
    a["GRank_x"] = a["id_x"].map(mapingdict)
    a["GRank_y"] = a["id_y"].map(mapingdict)
    a["SameGRank"] = 0
    a.loc[a.GRank_x == a.GRank_y, "SameGRank"] = 1
#%%
df1.head()
df1["InvInGroup"] = 0
df1["BankGroup"] = 0
df1["BankInGroup"] = 0
for i in set(BGId.BGId.dropna()):
    dname = "GDummy" + str(int(i))
    df1[dname] = 0
    df1.loc[df1.BGId_x == i, dname] = 1
    df1.loc[df1.BGId_y == i, dname] = 1
    df1.loc[(df1.BGId_x == i) & (df1.invinGroup_x == 1), "InvInGroup"] = 1
    df1.loc[(df1.BGId_y == i) & (df1.invinGroup_y == 1), "InvInGroup"] = 1
    df1.loc[(df1.BGId_x == i) & (df1.bankingUo_x == 1), "BankGroup"] = 1
    df1.loc[(df1.BGId_y == i) & (df1.bankingUo_y == 1), "BankGroup"] = 1
    df1.loc[(df1.bankinGroup_x == i) & (df1.bankinGroup_x == 1), "BankInGroup"] = 1
    df1.loc[(df1.bankinGroup_y == i) & (df1.bankinGroup_y == 1), "BankInGroup"] = 1

#%%
df1 = df1.rename(columns={"MonthlyFCA*": "NMFCA"})
df1["MonthlyCrossOwnership"] = df1.MonthlyCrossOwnership.replace(np.nan, 0)
df1 = df1.drop(
    columns=[
        "Weeklyρ_2",
        "Weeklyρ_4",
        "Weeklyρ_5",
        "WeeklyρLag_5",
        "WeeklySizeRatio",
        "WeeklyMarketCap_x",
        "WeeklyMarketCap_y",
        "WeeklyPercentile_Rank_x",
        "WeeklyPercentile_Rank_y",
        "Weeklysize1",
        "Weeklysize2",
        "WeeklySameSize",
        "WeeklyB/M1",
        "WeeklyB/M2",
        "WeeklySameB/M",
        "WeeklyFCAPf",
        "WeeklyFCA",
        "Weeklyρ_2_f",
        "Weeklyρ_4_f",
        "Weeklyρ_5_f",
        "WeeklyρLag_5_f",
        "FCAP*",
        "FCA*",
        "WeeklyFCAP*",
        "WeeklyFCA*",
        "Ret_x",
        "Ret_y",
        "SizeRatio",
        "MarketCap_x",
        "MarketCap_y",
        "2-Residual_x",
        "2-Residual_y",
        "4_Residual_x",
        "4_Residual_y",
        "5-Residual_x",
        "5-Residual_y",
        "5Lag_Residual_x",
        "5Lag_Residual_y",
        "Percentile_Rank_x",
        "Percentile_Rank_y",
        "BookToMarket_x",
        "BookToMarket_y",
        "WeeklyCrossOwnership",
    ]
)
#%%
df1["sBgroup"] = 0
df1.loc[df1.uo_x == df1.uo_y, "sBgroup"] = 1
df1.loc[df1.uo_x.isnull(), "sBgroup"] = 0
df1.loc[df1.uo_y.isnull(), "sBgroup"] = 0
df1.sBgroup.isnull().sum()
#%%
df1 = df1.sort_values(by=["id", "t_Month"])
df1["Monthlyρ_5_1"] = df1.groupby("id").Monthlyρ_5.shift(1)
df1["Monthlyρ_5_2"] = df1.groupby("id").Monthlyρ_5.shift(2)
df1["Monthlyρ_5_3"] = df1.groupby("id").Monthlyρ_5.shift(3)
df1["Monthlyρ_5_4"] = df1.groupby("id").Monthlyρ_5.shift(4)
df1["Monthlyρ_5_5"] = df1.groupby("id").Monthlyρ_5.shift(5)
#%%
df1["sameBgChange"] = 0
df1["becomeSameBG"] = 0
gg = df1.groupby("id")
df1["changedBG"] = 0


def changedBg(t):
    print(t.name)
    if t.sBgroup.sum() != len(t) and t.sBgroup.sum() != 0:
        t["changedBG"] = 1
        if t.sBgroup.iloc[0] == 1:
            ind = t.loc[t.sBgroup == 0].index[0]
            t.loc[t.index >= ind, "sameBgChange"] = 1
        else:
            ind = t.loc[t.sBgroup == 1].index[0]
            t.loc[t.index >= ind, "sameBgChange"] = 1
            t["becomeSameBG"] = 1
    return t


df1 = gg.apply(changedBg)


#%%
df1["2rdQarter"] = 0
df1["4rdQarter"] = 0
gg = df1.groupby(["t_Month"])
g = gg.get_group(2)


def quarter(g):
    print(g.name)
    q1 = g[g.MonthlyFCA > 0].MonthlyFCA.quantile(0.75)
    mt = g[g.MonthlyFCA > 0].MonthlyFCA.quantile(0.5)
    g.loc[g.MonthlyFCA > q1, "4rdQarter"] = 1
    g.loc[g.MonthlyFCA > mt, "2rdQarter"] = 1
    return g


gg = df1.groupby(["t_Month"])
df1 = gg.apply(quarter)

#%%


def Normalize(df_sub):
    col = df_sub
    return (col - col.mean()) / col.std()


df1["NMFCA2"] = df1["NMFCA"] * df1["NMFCA"]

gg = df1.groupby(["t_Month"])
df1["NMFCA2"] = gg["NMFCA2"].apply(Normalize)
df1.groupby(["t_Month"]).NMFCA2.std()
#%%

mapdict = dict(zip(time.jalaliDate, time.date))
path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\\"
df = pd.read_csv(path + "Stock Trade details.csv")
df["date"] = df.jalali.map(mapdict)
df = df[~df.ind_buy_count.isnull()].drop(
    columns=[
        "baseVol",
        "max_price",
        "min_price",
        "close_price",
        "last_price",
        "open_price",
        "value",
        "volume",
        "quantity",
        "Price",
        "open_Adjprice",
        "Adjusted price",
    ]
)
df["year"] = round(df.jalali / 10000)
df["year"] = df["year"].astype(int)
df = df[df.year >= 1394]


def vv4(row):
    row = str(row)
    X = [1, 1, 1]
    X[0] = row[0:4]
    X[1] = row[4:6]
    X[2] = row[6:8]
    return X[0] + "-" + X[1] + "-" + X[2]


df["date1"] = df["date"].apply(vv4)
df["date1"] = pd.to_datetime(df["date1"])
df["week_of_year"] = df["date1"].dt.week
df["Month_of_year"] = df["date1"].dt.month
df["year_of_year"] = df["date1"].dt.year


def BG(df):
    pathBG = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Control Right - Cash Flow Right\\"
    # pathBG = r"C:\Users\RA\Desktop\RA_Aghajanzadeh\Data\\"
    n = pathBG + "Grouping_CT.xlsx"
    BG = pd.read_excel(n)
    uolist = (
        BG[BG.listed == 1]
        .groupby(["uo", "year"])
        .filter(lambda x: x.shape[0] >= 3)
        .uo.unique()
    )
    BG = BG[BG.listed == 1]
    print(len(BG))
    BG = BG[BG.uo.isin(uolist)]
    print(len(BG))
    BGroup = set(BG["uo"])
    names = sorted(BGroup)
    ids = range(len(names))
    mapingdict = dict(zip(names, ids))
    BG["BGId"] = BG["uo"].map(mapingdict)

    tt = BG[BG.year == 1397]
    tt["year"] = 1398
    BG = BG.append(tt).reset_index(drop=True)

    BG = BG.groupby(["uo", "year"]).filter(lambda x: x.shape[0] >= 3)
    for i in ["uo", "cfr", "cr"]:
        print(i)
        fkey = zip(list(BG.symbol), list(BG.year))
        mapingdict = dict(zip(fkey, BG[i]))
        df[i] = df.set_index(["symbol", "year"]).index.map(mapingdict)
    return df


df = BG(df)
df["Grouped"] = 1
df.loc[df.uo.isnull(), "Grouped"] = 0
mlist = [
    "ind_buy_count",
    "ins_buy_count",
    "ind_sell_count",
    "ins_sell_count",
    "ind_buy_volume",
    "ins_buy_volume",
    "ind_sell_volume",
    "ins_sell_volume",
    "ind_buy_value",
    "ins_buy_value",
    "ind_sell_value",
    "ins_sell_value",
]
df["yearMonth"] = round(df.jalali / 100)
df["yearMonth"] = df["yearMonth"].astype(int)
df["yearWeek"] = df["year_of_year"].astype(str) + "-" + df["week_of_year"].astype(str)

#%%
frequency = "yearMonth"
mdf = df.groupby(["symbol", frequency]).first().drop(columns=["jalali"])
mdf[mlist] = df.groupby(["symbol", frequency])[mlist].sum()
mdf = mdf.reset_index()
mdf["InsImbalance_count"] = (mdf.ins_buy_count - mdf.ins_sell_count) / (
    mdf.ins_buy_count + mdf.ins_sell_count
)
mdf["InsImbalance_volume"] = (mdf.ins_buy_volume - mdf.ins_sell_volume) / (
    mdf.ins_buy_volume + mdf.ins_sell_volume
)
mdf["InsImbalance_value"] = (mdf.ins_buy_value - mdf.ins_sell_value) / (
    mdf.ins_buy_value + mdf.ins_sell_value
)
mdf = mdf[
    [
        "yearWeek",
        "symbol",
        "group_name",
        "year",
        "uo",
        "cfr",
        "cr",
        "Grouped",
        "yearMonth",
        "InsImbalance_count",
        "InsImbalance_volume",
        "InsImbalance_value",
    ]
].sort_values(by=["symbol", frequency])
mdf = mdf.reset_index(drop=True)
mdf = mdf[~mdf.InsImbalance_count.isnull()]
mdf
Imbalances = [
    "InsImbalance_count",
    "InsImbalance_volume",
    "InsImbalance_value",
    "Grouped",
]
gg = mdf.groupby(frequency)


def daily(g):
    print(g.name)
    Imbalances = [
        "InsImbalance_count",
        "InsImbalance_volume",
        "InsImbalance_value",
        "Grouped",
    ]
    a = g.groupby("uo")[Imbalances].std()
    a["Grouped"] = 1
    a = a.append(
        g[g.Grouped == 0][Imbalances].std().to_frame().rename(columns={0: "NotGroup"}).T
    )
    return a


result = gg.apply(daily)
result = result.reset_index().rename(columns={"level_1": "uo"})
a = result.groupby("uo")[Imbalances[:-1]].mean()
a = a.sort_values(by=Imbalances[:-1]).dropna()
a
lowlist = list(a[a.InsImbalance_value <= a.InsImbalance_value.median()].index)
df1["lowImbalanceStd"] = 0
df1.loc[df1.uo_x.isin(lowlist), "lowImbalanceStd"] = 1
df1.loc[df1.uo_y.isin(lowlist), "lowImbalanceStd"] = 1

#%%
df1 = df1.rename(columns={"4rdQarter": "ForthQuarter", "2rdQarter": "SecondQuarter"})
path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Connected stocks\\"
n1 = path + "MonthlyNormalzedFCAP7.2" + ".csv"
print(len(df1))
df1.to_csv(n1)
# %%
import pandas as pd
import numpy as np

path = r"G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Connected stocks\\"
n1 = path + "MonthlyNormalzedFCAP6.1" + ".csv"
df = pd.read_csv(n1)
# %%
df[["BGId_x", "uo_x"]].drop_duplicates().sort_values(by="BGId_x")
# %%
df1["PairType"] = 0
df1.loc[(df1.GRank_x >= 5) & (df1.GRank_y >= 5), "PairType"] = 2
df1.loc[(df1.GRank_x < 5) & (df1.GRank_y < 5), "PairType"] = 1
df1.groupby("PairType").NMFCA.describe()
