#!/usr/bin/env python3

import click
from utils import load_krp_file, get_lap_data, get_laps, get_best_lap
import plotly.express as px
from dash import Dash, html, dcc, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc


@click.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="host (0.0.0.0=all, 127.0.0.1=localhost)",
)
@click.option(
    "--port",
    default=8050,
    help="port (8050 or other)",
)
@click.option(
    "--theme",
    default="YETI",
    help="A Bootswatch theme among CERULEAN, COSMO, CYBORG, "
    "DARKLY, FLATLY, JOURNAL, LITERA, LUMEN, LUX, MATERIA, "
    "MINTY, MORPH, PULSE, QUARTZ, SANDSTONE, SIMPLEX, SKETCHY, "
    "SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, VAPOR, YETI, ZEPHYR. "
    "See https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/ "
    "for more information",
)
def main(host, port, theme):
    def load_telemetry_file(fname):
        print("load_telemetry_file")

    PAGE_SIZE_HEADER = 5
    PAGE_SIZE_DATA = 100

    df_head, df_units, df, df_laptimes = load_krp_file(
        "Logdata Essay mini60 2023-10-31.csv"
    )

    laps = get_laps(df)
    selected_lap = get_best_lap(df_laptimes)

    """
    @callback(Output('output-data-upload', 'children'),
                Input('upload-data', 'contents'),
                State('upload-data', 'filename'),
                State('upload-data', 'last_modified'))
    def update_output(list_of_contents, list_of_names, list_of_dates):
        print("update_output")
    """

    @callback(
        Output("tabs-example-content-1", "children"), Input("tabs-example-1", "value")
    )
    def render_content(tab):
        if tab == "tab-about":
            return html.Div(
                [
                    dcc.Markdown(
                        """
# Kart Racing Pro Telemetry analyser

Analyse the telemetry data generated by the karting simulator [Kart Racing Pro](https://www.kartracing-pro.com/).

To run the program press "Open Kart Racing Pro Telemetry File" and then select the file created by Kart Racing Pro.

You don't own KRP? Use this [sample file](https://raw.githubusercontent.com/scls19fr/krp_python_telemetry/taipy/Logdata%20Essay%20mini60%202023-10-31.csv).

The tabs are:

 * **About** information of the tool
 * **Data** to view table data of speed, throttle, break, steer etc
 * **Analyse** to view graphs of speed, throttle, break, steer etc
 * **Laps** to show only lap times

All graphs including the track map is zoomable.

Feel free to watch code at [https://github.com/scls19fr/krp_python_telemetry](https://github.com/scls19fr/krp_python_telemetry)
                """
                    )
                ]
            )
        elif tab == "tab-data":
            return html.Div(
                [
                    html.H3("Tab content data"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dash_table.DataTable(
                                    id="datatable-head",
                                    columns=[
                                        {"name": i, "id": i} for i in df_head.columns
                                    ],
                                    page_current=0,
                                    page_size=PAGE_SIZE_HEADER,
                                    page_action="custom",
                                ),
                                width=5,
                            ),
                            dbc.Col(
                                dash_table.DataTable(
                                    id="datatable-laptimes",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in df_laptimes.columns
                                    ],
                                    page_current=0,
                                    page_size=PAGE_SIZE_HEADER,
                                    page_action="custom",
                                ),
                                width=3,
                            ),
                            dbc.Col(
                                dash_table.DataTable(
                                    id="datatable-units",
                                    columns=[
                                        {"name": i, "id": i} for i in df_units.columns
                                    ],
                                    page_current=0,
                                    page_size=PAGE_SIZE_HEADER,
                                    page_action="custom",
                                ),
                                width=4,
                            ),
                        ]
                    ),
                    html.Br(),
                    dash_table.DataTable(
                        id="datatable-data",
                        columns=[{"name": i, "id": i} for i in df.columns],
                        page_current=0,
                        page_size=PAGE_SIZE_DATA,
                        page_action="custom",
                    ),
                    # html.Br(),
                ]
            )
        elif tab == "tab-analyse":
            graphs = []
            index = "Distance"
            for col in df.columns:
                if col not in [
                    "Time",
                    "Distance",
                    "Laptime",
                    "PosX",
                    "PosY",
                    "Lap",
                    "Starttime",
                ]:
                    df_lap = get_lap_data(df, 0, index=index)
                    fig = px.line(df_lap, x=df_lap.index, y=col, color="Lap")
                    for lap in laps[1:]:
                        df_lap = get_lap_data(df, lap, index)
                        fig.add_scatter(
                            x=df_lap.index, y=df_lap[col], mode="lines", name=str(lap)
                        )

                    id = f"graph-{col}"
                    graphs.append(dcc.Graph(figure=fig, id=id))

            maps = []
            # dd_lap = dcc.Dropdown(
            #    options=laps,
            #    value=selected_lap,
            #    id="dropdown-lap-selection",
            # )
            # maps.append(dd_lap)
            for col in df.columns:
                if col not in [
                    "Time",
                    "Distance",
                    "Laptime",
                    "PosX",
                    "PosY",
                    "Lap",
                    "Starttime",
                ]:
                    if col in ["LatAcc", "LonAcc", "Steer", "YawVel"]:
                        color_scale = "RdBu"
                    else:
                        color_scale = "YlOrBr"
                    df_selected_lap = get_lap_data(df, selected_lap, index=None)
                    fig = px.scatter(
                        df_selected_lap,
                        x="PosX",
                        y="PosY",
                        color=col,
                        hover_name=index,
                        color_continuous_scale=color_scale,
                        title=col,
                    )
                    id = f"map-{col}"
                    map = dcc.Graph(figure=fig, id=id)
                    # map = dcc.Graph(id=id)
                    maps.append(map)

            return html.Div(
                [
                    html.H3("Tab content analyse"),
                    dbc.Row(
                        [
                            dbc.Col([graph for graph in graphs], width=8),
                            dbc.Col([map for map in maps], width=4),
                        ]
                    ),
                ]
            )

        elif tab == "tab-laps":
            index = "Distance"
            df_lap = get_lap_data(df, 0, index)
            fig = px.line(df_lap, x="PosX", y="PosY", color="Lap")
            for lap in laps[1:]:
                df_lap = get_lap_data(df, lap, index)
                fig.add_scatter(
                    x=df_lap["PosX"], y=df_lap["PosY"], mode="lines", name=str(lap)
                )
            map = dcc.Graph(figure=fig)

            return html.Div(
                [
                    html.H3("Tab content laps"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dash_table.DataTable(
                                    id="datatable-laptimes-all",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in df_laptimes.columns
                                    ],
                                    page_current=0,
                                    page_size=PAGE_SIZE_DATA,
                                    page_action="custom",
                                ),
                                width=6,
                            ),
                            dbc.Col(map, width=6),
                        ]
                    ),
                ]
            )

    @callback(
        Output("datatable-laptimes-all", "data"),
        Input("datatable-laptimes-all", "page_current"),
        Input("datatable-laptimes-all", "page_size"),
    )
    def update_table_laptimes_all(page_current, page_size):
        return df_laptimes.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")

    # @callback(
    #    Output("map", "figure"),
    #    Input("dropdown-lap-selection", "value"),
    # )
    # def update_maps(selected_lap):
    #    print(f"update_maps with {selected_lap}")

    # Initialize the app
    # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    # external_stylesheets = [
    #     "https://gist.githubusercontent.com/zluvsand/4debf98c2d12bea077275c56f90bc767/raw/ccbfe65ac9dab4b232ee016e6344c3b2ffba72b8/style.css"
    # ]
    # app = Dash(__name__, external_stylesheets=external_stylesheets)
    bc_theme = getattr(
        dbc.themes, theme
    )  # Boostrap Components Theme see https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
    app = Dash(
        __name__, external_stylesheets=[bc_theme]
    )  # Dash Bootstrap Components : BOOTSTRAP / CYBORG
    # app = Dash(__name__)

    app.title = "KRP Telemetry app"

    # App layout
    app.layout = html.Div(
        [
            dcc.Upload(
                id="upload-data",
                children=html.Div(
                    [
                        "Drag and Drop or ",
                        html.A("Select Open Kart Racing Pro telemetry file"),
                    ]
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,  # Don't allow multiple files to be uploaded
            ),
            dcc.Tabs(
                id="tabs-example-1",
                value="tab-about",
                children=[
                    dcc.Tab(label="About", value="tab-about"),
                    dcc.Tab(label="Data", value="tab-data"),
                    dcc.Tab(label="Laps", value="tab-laps"),
                    dcc.Tab(label="Analyse", value="tab-analyse"),
                ],
            ),
            html.Div(id="tabs-example-content-1"),
        ]
    )

    @callback(
        Output("datatable-head", "data"),
        Input("datatable-head", "page_current"),
        Input("datatable-head", "page_size"),
    )
    def update_table_head(page_current, page_size):
        return df_head.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")

    @callback(
        Output("datatable-laptimes", "data"),
        Input("datatable-laptimes", "page_current"),
        Input("datatable-laptimes", "page_size"),
    )
    def update_table_laptimes(page_current, page_size):
        return df_laptimes.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")

    @callback(
        Output("datatable-units", "data"),
        Input("datatable-units", "page_current"),
        Input("datatable-units", "page_size"),
    )
    def update_table_units(page_current, page_size):
        return df_units.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")

    @callback(
        Output("datatable-data", "data"),
        Input("datatable-data", "page_current"),
        Input("datatable-data", "page_size"),
    )
    def update_table_data(page_current, page_size):
        return df.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")

    # Run the app
    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
