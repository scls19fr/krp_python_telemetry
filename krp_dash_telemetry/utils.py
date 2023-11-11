import numpy as np
import pandas as pd
import plotly.express as px


def load_krp_file(fname):
    nrows = 12
    df_head = pd.read_csv(fname, nrows=nrows, names=["Key", "Value"])
    # df_head = df_head.set_index("Key")

    df = pd.read_csv(fname, skiprows=nrows)
    units = df.iloc[0, :]
    units.index.name = "Data"
    units.name = "Units"
    cols = df.columns
    df = df.drop(0)
    for col in df.columns:
        df[col] = df[col].astype(float)
    df["Lap"] = ((df["Distance"] - df["Distance"].shift()) < 0).astype(int).cumsum()
    # df["Laptime"] = pd.NaT
    df["Starttime"] = np.where(
        (df["Distance"] - df["Distance"].shift()) < 0, df["Time"], np.NaN
    )
    # df["Starttime"].iloc[0] = 0
    df.loc[df.index[0], "Starttime"] = 0
    # df["Starttime"] = df["Starttime"].fillna(method="ffill")
    df["Starttime"] = df["Starttime"].ffill()
    df["Laptime"] = df["Time"] - df["Starttime"]

    df["Time"] = pd.to_datetime(df["Time"], unit="s")
    # df["Time"] = pd.to_timedelta(df["Time"], unit="s")

    # df["Laptime"] = pd.to_datetime(df["Laptime"], unit="s")

    # df = df.set_index("Time")

    laptimes = df.groupby("Lap")["Laptime"].last()[0:-1]

    return (
        df_head,
        units.to_frame().reset_index(),
        df,
        laptimes.to_frame().reset_index(),
    )


def get_laps(df):
    return df["Lap"].unique()


def get_best_lap(laptimes):
    return laptimes.sort_values(by="Laptime")["Lap"].iloc[0]


def get_lap_data(df, lap, index="Laptime"):
    df_lap = df[df["Lap"] == lap]
    if index is not None:
        df_lap = df_lap.set_index(index)
    return df_lap


def plot_lap_data(df, values="Engine", index="Laptime"):
    laps = get_laps(df)
    df_lap = get_lap_data(df, 0, index)
    fig = px.line(df_lap, x=df_lap.index, y=values, color="Lap")
    for lap in laps[1:]:
        df_lap = get_lap_data(df, lap, index)
        fig.add_scatter(x=df_lap.index, y=df_lap[values], mode="lines", name=str(lap))
    fig.show()


def plot_trajectory(df):
    fig = px.scatter(df, x="PosX", y="PosY", symbol="Lap", hover_name="Laptime")
    fig.show()
