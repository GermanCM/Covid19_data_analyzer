import logging

logging.basicConfig(filename='covi19_dashboarder.log',
                    level=logging.ERROR, 
                    format='%(asctime)s %(message)s')
logger = logging.getLogger("covi19_dashboarder")

class Absolute_numbers_evolution():
    """Displays data as:
        - global evolution of confirmed infections, deaths and recoverings on a world map
        - line charts of infections and deaths evolution
        - bar charts of increments of infections and deaths
    """
    def __init__(self, data):
        self.data_ = data

    def return_map_evolution_figure(self, map_data_dict, map_data_option):
        try:
            import plotly.express as px  

            self.data_['Date_col'] = self.data_.index
            grouped_geodf = self.data_.groupby(['Date_col', 'Country'])[map_data_dict[map_data_option]].max() 
            grouped_geodf = grouped_geodf.reset_index()
            grouped_geodf['Ratio'] = grouped_geodf[map_data_dict[map_data_option]].pow(0.2).round(1)

            fig_map = px.scatter_geo(grouped_geodf, locations="Country", locationmode='country names', 
                                color=map_data_dict[map_data_option], size='Ratio', hover_name="Country", 
                                range_color= [0, 1500], 
                                projection="natural earth", animation_frame="Date_col", 
                                title='COVID-19: Spread Over Time', color_continuous_scale="portland")

            fig_map.update_layout(margin={"r":10,"t":60,"l":0,"b":2},  
                height=500, width=710, 
                paper_bgcolor="#EBF2EC",
                legend=dict(x=0, y=0.1))
                
            return fig_map

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'return_map_evolution_figure', exc))

    def return_lines_evolution_figure(self, selected_countries_data, multiselection):
        try:
            from plotly.subplots import make_subplots
            import plotly.graph_objects as go

            fig = make_subplots(rows=2, cols=1, subplot_titles=("Confirmed cases", "Deaths"))

            for country_i in multiselection:
                country_data = selected_countries_data[selected_countries_data.Country==country_i]

                fig.add_trace(
                    go.Scatter(x=country_data.date, y=country_data.Confirmed, name=country_i, mode='lines+markers+text'), #, hoverinfo = 'all'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=country_data.date, y=country_data.Deaths, name=country_i, mode='lines+markers+text'),
                    row=2, col=1
                )

            fig.update_layout(margin={"r":10,"t":60,"l":10,"b":10}, height=600, width=710, showlegend=False, paper_bgcolor="#EBF2EC") #, legend=dict(x=-.18, y=1))
            return fig

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'return_lines_evolution_figure', exc))


    def return_bars_increments_evolution_figure(self, selected_countries_data, multiselection):
        try:
            import plotly.graph_objs as go
            from plotly.subplots import make_subplots

            import streamlit as st

            fig = make_subplots(rows=2, cols=1, subplot_titles=("New confirmed infections per day", "New deaths per day"))
            
            for country_i in multiselection:
                country_data = selected_countries_data[selected_countries_data.Country==country_i]
                #confirmed new infections
                country_confirmed_shift = country_data['Confirmed'].shift(periods=1)

                country_data['Day_increment'] = country_data['Confirmed'] - country_confirmed_shift
                
                #confirmed new deaths
                country_deaths_shift = country_data['Deaths'].shift(periods=1)
                country_data['Day_deaths'] = country_data['Deaths'] - country_deaths_shift

                trace_country_cases = go.Bar(
                            x = country_data['date'],
                            y = country_data['Day_increment'],
                            name=country_i
                )
                fig.add_trace(
                    trace_country_cases,
                    row=1, col=1
                )
                trace_country_deaths = go.Bar(
                            x = country_data['date'],
                            y = country_data['Day_deaths'],
                            name=country_i
                )
                fig.add_trace(
                    trace_country_deaths,
                    row=2, col=1
                )

            fig.update_layout(margin={"r":10,"t":60,"l":10,"b":10}, height=600, width=710, showlegend=False, paper_bgcolor="#EBF2EC") #legend=dict(x=-.18, y=1))
            return fig

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'return_bars_increments_evolution_figure', exc))