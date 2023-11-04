import taipy as tp
from taipy import Config, Core, Gui
import pandas as pd
from utils import load_krp_file, get_laps


################################################################
#            Configure application                             #
################################################################
def load_telemetry_file(name):
    print("xxx")
    return f"Hello {name}!"


# A first data node configuration to model an input name.
fname_data_node_cfg = Config.configure_data_node(id="fname")
# A second data node configuration to model the message to display.
df_head_data_node_cfg = Config.configure_data_node(id="df_head")
# A task configuration to model the build_message function.
build_telemetry_task_cfg = Config.configure_task("load_telemetry_file", load_telemetry_file, fname_data_node_cfg, df_head_data_node_cfg)
# The scenario configuration represents the whole execution graph.
scenario_cfg = Config.configure_scenario("scenario", task_configs=[build_telemetry_task_cfg])

################################################################
#            Design graphical interface                        #
################################################################

#fname = None
#df_head = None

fname = "Logdata Essay mini60 2023-10-31.csv"
df_head, df_units, df, laptimes = load_krp_file(fname)
laps = get_laps(df)
print(laps)
df_disp = df.copy()
df_disp.index = (df_disp.index - pd.to_datetime(0)).total_seconds()

def load_telemetry_file_scenario(state):
    fname = state.fname
    df_head, df_units, df, laptimes = load_krp_file(fname)
    state.scenario.df_head.write(df_head)
    state.scenario.submit()
    state.df_head = scenario.df_head.read()


page = """
<|{fname}|file_selector|label=Open Kart Racing Pro Telemetry File|on_action=load_telemetry_file_scenario|extensions=.csv|drop_message=Drop Message|>

<|{laps}|toggle|>

<|layout|columns=40% 30% 30%|

<|{df_head.reset_index()}|table|page_size=5|>

<|{laptimes.reset_index()}|table|page_size=5|>

<|{df_units.reset_index()}|table|page_size=5|>

|>


<|{df}|chart|mode=line|x=Distance|y=Engine|color=Lap|>

<|{df}|chart|mode=scatter|x=PosX|y=PosY|>

<|{df_disp.reset_index()}|table|>
"""

if __name__ == "__main__":
    # Instantiate and run Core service
    Core().run()
    # Manage scenarios and data nodes
    scenario = tp.create_scenario(scenario_cfg)
    # Instantiate and run Gui service
    Gui(page).run()

