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

class globalIndicadors:
    creationTime_ts = "creationTime_ts"
    blocks = "blocks"
    proccess_duration_d = "proccess_duration_d"

    def __init__(self, df_processes, df_envelopes, AVG_BLOCK_TIME_SECS):
        self.df_processes = df_processes
        self.df_envelopes = df_envelopes
        self.AVG_BLOCK_TIME_SECS = AVG_BLOCK_TIME_SECS
        self._preprocess()
        self.get_global_indicators()

    def _preprocess(self):
        self.df_processes[self.blocks] = (self.df_processes["endBlock"] - self.df_processes["startBlock"])
        self.df_processes[self.proccess_duration_d] = (self.df_processes[self.blocks] 
                                                    / self.AVG_BLOCK_TIME_SECS # seconds
                                                    / 60 # minutes
                                                    / 24 # days
                                        )

        self.df_processes[self.creationTime_ts] = pd.to_datetime(self.df_processes["creationTime"])
        self.MIN_KNOWN_DATE = self.df_processes[self.creationTime_ts].min()


    def scatter_duration_votes(self):
        tmp_df = self.df_processes.loc[:, ["proccess_duration_d", "votes_count"]]
        return self._scatter_duration_votes(tmp_df, title="Process duration vs votes count")

    def _scatter_duration_votes(self, df, title):
        fig = create_scatterplotmatrix(
                                df,
                                diag='histogram', 
                                height=700, width=900,
                                title=title
                                )
        return fig.show()
    
    def get_global_indicators(self):
        # Processes
        self.total_processes = len(self.df_processes["processId"].unique())
        self.processes_evol = self.df_processes.groupby('creationTime_ts')['processId'].count().cumsum(axis=0)

        # Entities
        self.df_processes['not_dup'] = 1 - self.df_processes["entityId"].duplicated()
        self.entities_evol = self.df_processes.groupby('creationTime_ts')['not_dup'].sum().cumsum()
        self.df_processes.drop('not_dup', inplace=True, axis=1)
        self.total_entities = len(self.df_processes["entityId"].unique())
        
        # Votes
        self.total_votes = self.df_processes["votes_count"].sum()
        self.votes_evol = self.df_envelopes.groupby('vote_ts')['nullifier'].count().cumsum(axis=0)

    def plot_processes(self):
        name = "Cumulative Processes count"
        return self._plot_global_indicators(self.processes_evol, self.total_processes, name)

    def plot_entities(self):
        name = "Cumulative Entities count"
        return self._plot_global_indicators(self.entities_evol, self.total_entities, name)
    
    def plot_votes(self):
        name = "Cumulative Votes count"
        return self._plot_global_indicators(self.votes_evol, self.total_votes, name)

    
    def _plot_global_indicators(self, evol, total, name):
        fig = go.Figure(go.Indicator(
            mode = "number+delta",
            value = total,
            delta = {"reference": evol[-3], "valueformat": ".0f"},
            domain = {'y': [0, 1], 'x': [0.25, 0.75]}))

        fig.add_trace(go.Scatter(y=evol, 
                                marker_color="rgba(0, 255, 255, .8)", 
                                name=name,
                                x=evol.index,
                                mode='markers'
                            )
                    )
        fig.update_layout(title_text=name)
        return fig.show()