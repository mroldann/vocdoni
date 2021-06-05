import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.figure_factory import create_scatterplotmatrix
pio.renderers.default = 'iframe_connected'
import pandas as pd
from datetime import timedelta

def add_time_cols(df_processes, AVG_BLOCK_TIME_SECS):
    creationTime_ts = "creationTime_ts"
    blocks = "blocks"
    proccess_duration_d = "proccess_duration_d"

    df_processes[blocks] = (df_processes["endBlock"] 
    - df_processes["startBlock"])

    
    df_processes[proccess_duration_d] = (df_processes[blocks] 
                                       / AVG_BLOCK_TIME_SECS # seconds
                                       / 60 # minutes
                                       / 24 # days
                                      )

    df_processes[creationTime_ts] = pd.to_datetime(df_processes["creationTime"])

    MIN_KNOWN_DATE = df_processes[creationTime_ts].min()
    
    df_processes["endingTime_ts"] = (df_processes[creationTime_ts] 
    + df_processes[proccess_duration_d].apply(lambda x: timedelta(days=x)))

    df_processes = df_processes.drop("_id", axis=1)
    return df_processes, MIN_KNOWN_DATE




def scatter_duration_votes(df_processes):
    fig = create_scatterplotmatrix(df_processes.loc[:, ["proccess_duration_d", "votes_count"]],
                                diag='histogram', 
                                height=700, width=900,
                                )
    return fig.show()