import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.figure_factory import create_scatterplotmatrix
pio.renderers.default = 'iframe_connected'
import pandas as pd
from datetime import timedelta
class globalIndicadors:
    creationTime_ts = "creationTime_ts"
    blocks = "blocks"
    proccess_duration_d = "proccess_duration_d"
    entityId = "entityId"
    votes_count = "votes_count"
    processId = "processId"
    weight = "weight"
    

    def __init__(self, df_processes, df_envelopes, AVG_BLOCK_TIME_SECS):
        self.df_processes = df_processes
        self.df_envelopes = df_envelopes
        self.AVG_BLOCK_TIME_SECS = AVG_BLOCK_TIME_SECS
        self._preprocess()
        self.get_global_indicators()

    def _preprocess(self):
        self._add_time_cols()
        self.MIN_KNOWN_DATE = self.df_processes["creationTime_ts"].min()
        # Needed for grouper, then dropped.
        self.df_processes['not_dup'] = 1 - self.df_processes["entityId"].duplicated()

        self.df_envelopes[self.weight] = self.df_envelopes[self.weight].astype(float)
        ### Estimate timestamp for every envelope
        self.df_envelopes["vote_ts"] = (self.df_envelopes["height"]  
                                / self.AVG_BLOCK_TIME_SECS # seconds
                                / 60 # minutes
                                / 24 # days
                                ).apply(lambda x: timedelta(days=x)) + self.MIN_KNOWN_DATE

        self.df_processes[self.blocks] = (self.df_processes["endBlock"] - self.df_processes["startBlock"])
        self.df_processes[self.proccess_duration_d] = (self.df_processes[self.blocks] 
                                                    / self.AVG_BLOCK_TIME_SECS # seconds
                                                    / 60 # minutes
                                                    / 24 # days
                                        )

        self.df_processes[self.creationTime_ts] = pd.to_datetime(self.df_processes["creationTime"])
        self.MIN_KNOWN_DATE = self.df_processes[self.creationTime_ts].min()
        self._add_votes_to_processes()

        # Set Groupers
        self.proc_day_grouper = self.df_processes.groupby(pd.Grouper(key='creationTime_ts',freq='D'))
        self.votes_day_grouper = self.df_envelopes.groupby(pd.Grouper(key='vote_ts',freq='D'))
        self.votes_day_hour_grouper = self.df_envelopes.groupby(pd.Grouper(key='vote_ts',freq='H'))
        self.votes_weekday_grouper = self.df_envelopes.groupby(self.df_envelopes['vote_ts'].dt.weekday)
        self.votes_hour_grouper = self.df_envelopes.groupby(self.df_envelopes['vote_ts'].dt.hour)

        self.votes_per_day = self.votes_day_grouper["nullifier"].count()
        self.votes_per_day_hour = self.votes_day_hour_grouper["nullifier"].count()
        self.votes_weekday = self.votes_weekday_grouper["nullifier"].count()
        self.votes_hour = self.votes_hour_grouper["nullifier"].count()


        # Aggs

        self.votes_per_process = (self.df_envelopes.groupby("process_id")["nullifier"]
                                .count()       
                                .sort_values(ascending=False)
            )

        self.votes_per_entity = (self.df_processes.groupby(self.entityId)[self.votes_count]
                                .sum()       
                                .sort_values(ascending=False)
            )
        
        self.processes_per_entity = (self.df_processes.groupby(self.entityId)[self.processId]
                                .count()       
                                .sort_values(ascending=False)
            )
    
    def plot_processes_per_entity(self):
        return self._plot_ranking(self.processes_per_entity, title="Process per Entity (log scale)")

    def plot_votes_per_process(self):
        return self._plot_ranking(self.votes_per_process, title="Votes per Processes (log scale)")
    
    def plot_votes_per_entity(self):
        return self._plot_ranking(self.votes_per_entity, title="Votes per Entity (log scale)")

    def _plot_ranking(self, s, title):
        fig = px.histogram(s, title=title, nbins=40)
        return fig.show()

    def _plot_cumulative(self, s, title):
        total_n = s.sum()
        cumsum_s = (s.sort_values()/total_n).cumsum()
        fig = px.line(cumsum_s.values, title=title)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(title="Aggregate %")
        fig.update_xaxes(title="Index")
        return fig.show()

    
    def _add_votes_to_processes(self):
        df_tmp = (self.df_envelopes.groupby("process_id")["nullifier"]
                        .count()
                        .sort_values(ascending=False)
                        .to_frame()
                        )

        votes_dict = {process_id : vote_count[0] for process_id, vote_count in df_tmp.iterrows()}
        self.df_processes["votes_count"] = (self.df_processes["processId"]
                                                .apply(lambda x: votes_dict.get(x, 0)).astype("float"))

    def _add_time_cols(self):
        self.df_processes[self.blocks] = (self.df_processes["endBlock"] - self.df_processes["startBlock"])

        
        self.df_processes[self.proccess_duration_d] = (self.df_processes[self.blocks] 
                                        / self.AVG_BLOCK_TIME_SECS # seconds
                                        / 60 # minutes
                                        / 24 # days
                                        )

        self.df_processes[self.creationTime_ts] = pd.to_datetime(self.df_processes["creationTime"])
        self.df_processes["endingTime_ts"] = (self.df_processes[self.creationTime_ts] + self.df_processes[self.proccess_duration_d].apply(lambda x: timedelta(days=x)))    
    
    def plot_votes_per_day(self):
            return self._plot_scatter_log(self.votes_per_day, "votes_per_day (log scale)", 'markers+lines')
    
    def plot_votes_per_day_hour(self):
            return self._plot_scatter_log(self.votes_per_day_hour, "votes_per_day_hour (log scale)", 'markers')

    def plot_votes_weekday(self):
            return self._plot_scatter_log(self.votes_weekday, "votes_weekday (log scale)", 'markers')

    def plot_votes_hour(self):
            return self._plot_scatter_log(self.votes_hour, "votes_hour (log scale)",'markers+lines')

    def _plot_scatter_log(self, s, title, mode):
            fig = go.Figure()
            fig.add_trace(go.Bar(x=s.index, y=s.values,
                        # mode=mode
                        )
            )
            fig.update_layout(title_text=title)
            fig.update_yaxes(type="log") 
            return fig
            
    def scatter_duration_votes(self):
        fig = px.scatter(self.df_processes, x="proccess_duration_d", y="votes_count")
        fig.update_yaxes(type="log") 
        return fig.show()

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
        self.processes_evol = self.proc_day_grouper['processId'].count().cumsum(axis=0)

        # Entities
        self.entities_evol = self.proc_day_grouper['not_dup'].sum().cumsum()
        self.df_processes.drop('not_dup', inplace=True, axis=1)
        self.total_entities = len(self.df_processes["entityId"].unique())
        
        # Votes
        self.total_votes = self.df_processes["votes_count"].sum()
        self.votes_evol = self.votes_day_grouper['nullifier'].count().cumsum(axis=0)

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
                                mode='markers+lines'
                            )
                    )
        fig.update_layout(title_text=name)
        

        return fig.show()