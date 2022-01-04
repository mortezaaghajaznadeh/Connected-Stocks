#%%
import pandas as pd
import os
import pickle

path = r"E:\RA_Aghajanzadeh\Data\Connected_Stocks\\"


def add(row):
    if len(row) < 2:
        row = "0" + row
    return row


def firstStep(d, df):
    mapingdict = dict(zip(df.id, df.symbol))

    d["symbol_x"] = d["id_x"].map(mapingdict)
    d["symbol_y"] = d["id_y"].map(mapingdict)

    d["month_of_year"] = d["month_of_year"].astype(str).apply(add)
    d["week_of_year"] = d["week_of_year"].astype(str).apply(add)

    d["year_of_year"] = d["year_of_year"].astype(str)

    d["Year_Month_week"] = d["year_of_year"] + d["week_of_year"]
    d["Year_Month"] = d["year_of_year"] + d["month_of_year"]

    days = list(set(d.date))
    days.sort()
    t = list(range(len(days)))
    mapingdict = dict(zip(days, t))
    d["t"] = d["date"].map(mapingdict)

    days = list(set(d.Year_Month_week))
    days.sort()
    t = list(range(len(days)))
    mapingdict = dict(zip(days, t))
    d["t_Week"] = d["Year_Month_week"].map(mapingdict)

    days = list(set(d.Year_Month))
    days.sort()
    t = list(range(len(days)))
    mapingdict = dict(zip(days, t))
    d["t_Month"] = d["Year_Month"].map(mapingdict)

    d["id_x"] = d.id_x.astype(str)
    d["id_y"] = d.id_y.astype(str)
    d["id"] = d["id_x"] + "-" + d["id_y"]
    ids = list(set(d.id))
    id = list(range(len(ids)))
    mapingdict = dict(zip(ids, id))
    d["id"] = d["id"].map(mapingdict)
    return d



def SecondStep(a):
    a = a.reset_index(drop=True)
    a["id_x"] = a.id_x.astype(str)
    a["id_y"] = a.id_y.astype(str)
    a["id"] = a["id_x"] + "-" + a["id_y"]
    ids = list(set(a.id))
    id = list(range(len(ids)))
    mapingdict = dict(zip(ids, id))
    a["id"] = a["id"].map(mapingdict)
    return a


#%%
df = pd.read_parquet(path + "Holder_Residual_1400_10_06.parquet")
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
mlist = [
            "Monthlyρ_2",
            "Monthlyρ_4",
            "Monthlyρ_5",
            "Monthlyρ_6",
            "Monthlyρ_5Lag",
            "Monthlyρ_turn",
            "Monthlyρ_amihud",
            "MonthlySizeRatio",
            "MonthlyMarketCap_x",
            "MonthlyMarketCap_y",
            "MonthlyPercentile_Rank_x",
            "MonthlyPercentile_Rank_y",
            "Monthlysize1",
            "Monthlysize2",
            "MonthlySameSize",
            "MonthlyB/M1",
            "MonthlyB/M2",
            "MonthlySameB/M",
            "MonthlyCrossOwnership",
            "MonthlyTurnOver_x",
            "MonthlyAmihud_x",
            "Monthlyvolume_x",
            "Monthlyvalue_x",
            "MonthlyTurnOver_y",
            "MonthlyAmihud_y",
            "Monthlyvolume_y",
            "Monthlyvalue_y",
            "MonthlyFCAPf",
            "MonthlyFCA",
            "Monthlyρ_2_f",
            "Monthlyρ_4_f",
            "Monthlyρ_5_f",
            "Monthlyρ_6_f",
            "MonthlyρLag_5_f",
            "Monthlyρ_turn_f",
            "Monthlyρ_amihud_f",
        ]

#%%
Monthly = pd.DataFrame()
Weekly = pd.DataFrame()
time = pd.DataFrame()
d = pd.DataFrame()
arrs = os.listdir(path + "NormalzedFCAP9.1")
arrs.remove('Old')
counter_file = 0
#%%
for counter, i in enumerate(arrs):
    print(counter, len(Monthly),i)
    d = pd.read_pickle(path + "NormalzedFCAP9.1\\" + i)
    if len(d) == 0:
        continue
    d = d.drop(
        columns= mlist
    )
    if len(d) == 0:
        continue
    d = firstStep(d, df)
    m = d.drop_duplicates(["id", "t_Week"], keep="last")
    Monthly = Monthly.append(m)
    d = pd.DataFrame()
    if len(Monthly) > 6e6:
        counter_file += 1
        pickle.dump(
            # Monthly,
            # open(
                # path + "mergerd_first_step_weekly_part_{}.p".format(counter_file),
                # "wb",
            # ),
        )
        Monthly = pd.DataFrame()
counter_file += 1
pickle.dump(
    Monthly,
    open(
        path + "mergerd_first_step_weekly_part_{}.p".format(counter_file),
        "wb",
    ),
)
Monthly = pd.DataFrame()
# %%

path = r"E:\RA_Aghajanzadeh\Data\Connected_Stocks\NormalzedFCAP9.1_AllPairs\\"
path2 = r"E:\RA_Aghajanzadeh\Data\Connected_Stocks\\"
arr = os.listdir(path)
arr.remove('Old')
df = pd.read_parquet(path2 + "Holder_Residual_1400_10_06.parquet")
# %%
result = pd.DataFrame()
counter, counter_file = 0, 0
# arr.remove("MonthlyAllPairs_1400_06_28.csv")
for i, name in enumerate(arr):
    print(i, len(result),name)
    d = pd.read_pickle(path + name).reset_index(drop=True)
    if len(d) < 1:
        continue
    d = d.drop(
        columns= mlist
    )
    d = firstStep(d, df).drop_duplicates(["id", "t_Week"], keep="last")
    result = result.append(d)
    d = pd.DataFrame()
    if len(result) > 6e6:
        counter_file += 1
        pickle.dump(
            result,
            open(
                path2
                + "mergerd_first_step_weekly_all_part_{}.p".format(counter_file),
                "wb",
            ),
        )
        result = pd.DataFrame()
counter_file += 1
pickle.dump(
            result,
            open(
                path2
                + "mergerd_first_step_weekly_all_part_{}.p".format(counter_file),
                "wb",
            ),
        )
result = pd.DataFrame()


# %%
