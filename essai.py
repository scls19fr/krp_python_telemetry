from dash import Dash, dcc, html, dash_table, Input, Output, State, callback

import base64
import datetime
import io

import numpy as np
import pandas as pd


def load_krp_file(io):
    nrows = 12
    df_head = pd.read_csv(io, nrows=nrows, names=["Key", "Value"])
    # df_head = df_head.set_index("Key")

    io.seek(0)
    df = pd.read_csv(io, skiprows=nrows)
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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    print(content_type, filename, date)

    decoded = base64.b64decode(content_string)
    dat = io.StringIO(decoded.decode('utf-8'))

    try:
        if '.csv' in filename:
            # Assume that the user uploaded a CSV file
            df_head, df_units, df, df_laptimes = load_krp_file(dat)

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    app.run(debug=True)
