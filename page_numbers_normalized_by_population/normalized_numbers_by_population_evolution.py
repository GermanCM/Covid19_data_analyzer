#%%
import logging

logging.basicConfig(filename='covi19_dashboarder.log',
                    level=logging.ERROR, 
                    format='%(asctime)s %(message)s')
logger = logging.getLogger("covi19_dashboarder")

class Normalized_by_population_numbers_evolution():
    """Displays data as:
        - line charts of infections and deaths evolution normalized by total population and elderly population
        - bar charts of increments of infections and deaths normalized by total population and elderly population
    """
    def __init__(self, data):
        self.data_ = data
        self.population_data_ = None

    def get_population_data(self, multiselection):
        try:
            import pandas as pd 
            demographic_data = pd.read_csv('https://raw.githubusercontent.com/GermanCM/Covid19_data_analyzer/master/external_data/demographic_population.csv', sep=',')
            population_countries_df = pd.DataFrame()
            desired_cols = ['Country', 'SEX', 'AGE', 'TIME' , 'Value']

            for country in multiselection:
                demographic_data_country=demographic_data[demographic_data.Country==country]
                most_recent_year=demographic_data_country.TIME.max()
                most_recent_data_mask=demographic_data_country.TIME==most_recent_year
                total_population_age_mask=demographic_data_country.AGE=='TOTAL' 
                total_population_sex_mask=demographic_data_country.SEX=='T'

                country_demographic_data=demographic_data_country[(total_population_age_mask)&(most_recent_data_mask)&\
                                          (total_population_sex_mask)]
                country_demographic_data.Value=country_demographic_data.Value.apply(int)

                population_countries_df = population_countries_df.append(country_demographic_data, ignore_index=True)
            
            self.population_data_ = population_countries_df[desired_cols]
            return population_countries_df[desired_cols]

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'get_population_data', exc))

    def get_elderly_population_data(self, multiselection):
        try:
            import pandas as pd 
            elderly_demographic_data = pd.read_csv('https://raw.githubusercontent.com/GermanCM/Covid19_data_analyzer/master/external_data/demographic_age_over_65.csv', sep=',')
            elderly_population_countries_df = pd.DataFrame()
            desired_columns = ['Variable', 'Measure', 'Country', 'Year', 'Value']

            for country in multiselection:
                elderly_demographic_data_country=elderly_demographic_data[elderly_demographic_data['Country']==country]
                most_recent_year=elderly_demographic_data_country['Year'].max()
                most_recent_data_mask=elderly_demographic_data_country['Year']==most_recent_year
                total_population_age_mask=elderly_demographic_data_country['Variable']=='Population: 80 years old and over' 
                total_population_measure_mask=elderly_demographic_data_country['Measure']=='% of total population'

                elderly_country_demographic_data=elderly_demographic_data_country[(total_population_age_mask)&(most_recent_data_mask)&\
                                          (total_population_measure_mask)]
                elderly_country_demographic_data.Value=elderly_country_demographic_data.Value.apply(int)

                elderly_population_countries_df = elderly_population_countries_df.append(elderly_country_demographic_data, ignore_index=True)
            
            self.elderly_population_data_ = elderly_population_countries_df[desired_columns]
            return elderly_population_countries_df[desired_columns]

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'get_elderly_population_data', exc))

    def get_absolute_elderly_population_numbers(self, multiselection):
        try:
            import pandas as pd

            pop_data = self.get_population_data(multiselection)
            elderly_pop_data = self.get_elderly_population_data(multiselection)

            elderly_pop_data['Total_elderly_population_value'] = pd.Series()
            elderly_pop_data

            for country in elderly_pop_data.Country:
                country_total_pop_mask = pop_data.Country==country
                elderly_pop_data_mask = elderly_pop_data.Country==country
                desired_index = elderly_pop_data[elderly_pop_data_mask].index

                country_total_pop_value = pop_data[country_total_pop_mask].Value
                elderly_pop_data_percentage = elderly_pop_data[elderly_pop_data_mask].Value 

                elderly_pop_data.loc[desired_index,'Total_elderly_population_value']=\
                    int(((elderly_pop_data_percentage*country_total_pop_value)/100))

            return elderly_pop_data

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'get_absolute_elderly_population_numbers', exc))

    
    def return_normalized_lines_evolution_figure(self, selected_countries_data, multiselection):
        try:
            from plotly.subplots import make_subplots
            import plotly.graph_objects as go
            import numpy as np
            import pandas as pd 

            population_countries_df = self.get_population_data(multiselection)
        
            fig = make_subplots(rows=2, cols=1, subplot_titles=("Confirmed cases normalized by population", "Deaths normalized by population"))

            for country_i in population_countries_df.Country.values:
                country_population = population_countries_df[population_countries_df.Country==country_i]['Value']
                country_data = selected_countries_data[selected_countries_data.Country==country_i]
                
                country_data.Confirmed=country_data.Confirmed.apply(lambda x: 1000*(x/country_population)).round(2)
                country_data.Deaths=country_data.Deaths.apply(lambda x: 1000*(x/country_population)).round(2)

                fig.add_trace(
                    go.Scatter(x=country_data.date, y=country_data.Confirmed, name=country_i, mode='lines+markers+text'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=country_data.date, y=country_data.Deaths, name=country_i, mode='lines+markers+text'),
                    row=2, col=1
                )

            fig.update_layout(margin={"r":10,"t":60,"l":10,"b":10}, height=600, width=710, showlegend=False, paper_bgcolor="#EBF2EC") 
            return fig

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'return_normalized_lines_evolution_figure', exc))


    def return_normalized_bars_increments_evolution_figure(self, selected_countries_data, multiselection):
        try:
            from plotly.subplots import make_subplots
            import plotly.graph_objects as go
            import numpy as np
            import pandas as pd 

            population_countries_df = self.get_population_data(multiselection)

            fig = make_subplots(rows=2, cols=1, subplot_titles=("New confirmed infections normalized by population per day", 
                                                                "New deaths normalized by population per day"))
            
            for country_i in multiselection:
                country_population = population_countries_df[population_countries_df.Country==country_i]['Value']
                country_data = selected_countries_data[selected_countries_data.Country==country_i]

                country_data.Confirmed=country_data.Confirmed.apply(lambda x: 10000*(x/country_population)).round(2)
                country_data.Deaths=country_data.Deaths.apply(lambda x: 10000*(x/country_population)).round(2)

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

