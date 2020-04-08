#%%
import logging

logging.basicConfig(filename='covi19_dashboarder.log',
                    level=logging.ERROR, 
                    format='%(asctime)s %(message)s')
logger = logging.getLogger("covi19_dashboarder")

class Health_impact_evolution():
    """Displays data as:
        - line charts of infections and deaths evolution normalized by total population and elderly population
        - bar charts of increments of infections and deaths normalized by total population and elderly population
    """
    def __init__(self, data):
        self.data_ = data

    def get_current_deaths_confirmed_infections_impact(self, multiselection):
        try:
            import plotly.express as px

            selected_country_mask = [x in multiselection for x in self.data_.Country]
            selected_countries_data = self.data_[selected_country_mask]

            last_date = selected_countries_data.index[-1] 
            scatter_data = selected_countries_data[selected_countries_data.index == last_date]

            scatter_data['Health_impact'] = (scatter_data.Deaths/scatter_data.Confirmed).round(3)

            fig = px.scatter(scatter_data, x="Confirmed", y="Deaths", color="Health_impact",
                            size='Health_impact', hover_data=['Country'])

            fig.update_layout(margin={"r":10,"t":60,"l":10,"b":2}, height=450, width=710, showlegend=False, paper_bgcolor="#EBF2EC")
            
            return fig

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'get_current_deaths_confirmed_infections_impact', 
                        exc))

    def get_current_deaths_elderly_impact(self, multiselection, elderly_data):
        try:
            import plotly.express as px

            selected_country_mask = [x in multiselection for x in self.data_.Country]
            selected_countries_data = self.data_[selected_country_mask]

            last_date = selected_countries_data.index[-1]
            scatter_data = selected_countries_data[selected_countries_data.index == last_date]
           
            scatter_data_with_elderly = scatter_data.merge(elderly_data[['Country', 'Total_elderly_population_value']], 
                                            how='inner', on='Country')

            scatter_data_with_elderly['Health_impact_on_elderly'] = (scatter_data_with_elderly.Deaths/scatter_data_with_elderly.Total_elderly_population_value).round(3)

            fig = px.scatter(scatter_data_with_elderly, x="Total_elderly_population_value", y="Deaths", color="Health_impact_on_elderly",
                            size='Health_impact_on_elderly', hover_data=['Country'])
            
            fig.update_layout(margin={"r":10,"t":60,"l":10,"b":2}, height=450, width=710, showlegend=False, paper_bgcolor="#EBF2EC")

            return fig

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'get_current_deaths_elderly_impact', 
                        exc))
    

    def get_tests_evolution_data(self, multiselection):
        try:
            import pandas as pd 
            tests_data = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/testing/covid-testing-all-observations.csv', sep=',')

            tests_countries_df = pd.DataFrame()
            desired_cols = ['Entity', 'Date', 'Cumulative total', 'Daily change in cumulative total',
                            'Cumulative total per thousand', 'Daily change in cumulative total per thousand']

            tests_data['Country'] = tests_data.Entity.apply(lambda x: x.split('-')[0].strip())
            desired_cols = ['Country', 'Date', 'Cumulative total', 'Daily change in cumulative total',
                            'Cumulative total per thousand', 'Daily change in cumulative total per thousand']

            for country in multiselection:
                tests_data_country=tests_data[tests_data.Country==country]                

                tests_countries_df = tests_countries_df.append(tests_data_country, ignore_index=True)
            
            self.test_data_ = tests_countries_df[desired_cols]
            return tests_countries_df[desired_cols]

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'get_tests_evolution_data', exc))

    def return_tests_and_deaths_figure(self, multiselection):
        try:
            import plotly.express as px
            from page_numbers_normalized_by_population import normalized_numbers_by_population_evolution as population_num

            norm_nums_obj = population_num.Normalized_by_population_numbers_evolution(self.data_)
            population_countries_df = norm_nums_obj.get_population_data(multiselection)

            multiselection_tests_data = ['United States' if x=='US' else x for x in multiselection]
            selected_countries_tests_data = self.get_tests_evolution_data(multiselection_tests_data)

            fig = make_subplots(rows=2, cols=1, subplot_titles=("Informed tests", "Confirmed deaths"))

            for country_i in multiselection:
                country_population = population_countries_df[population_countries_df.Country==country_i]['Value']
                country_covid_data = self.data_[self.data_.Country==country_i]
                country_covid_data.Deaths=country_covid_data.Deaths.apply(lambda x: 1000*(x/country_population)).round(2)

                fig.add_trace(
                    go.Scatter(x=selected_countries_tests_data.Date, y=selected_countries_tests_data['Cumulative total'], 
                               name=country_i, mode='lines+markers+text'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=country_covid_data.date, y=country_covid_data.Deaths, name=country_i, mode='lines+markers+text'),
                    row=2, col=1
                )

            fig.update_layout(margin={"r":10,"t":60,"l":10,"b":10}, height=600, width=710, showlegend=False, paper_bgcolor="#EBF2EC") 
            return fig

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'return_tests_and_deaths_figure', exc))


    def return_tests_and_deaths_violin_figure(self, multiselection):
        try:
            import pandas as pd
            import plotly.express as px
            from page_numbers_normalized_by_population import normalized_numbers_by_population_evolution as population_num

            #norm_nums_obj = population_num.Normalized_by_population_numbers_evolution(self.data_)
            #population_countries_df = norm_nums_obj.get_population_data(multiselection)

            multiselection_tests_data = ['United States' if x=='US' else x for x in multiselection]
            selected_countries_tests_data = self.get_tests_evolution_data(multiselection_tests_data)

            selected_countries_tests_data['Cumulative total per thousand']=selected_countries_tests_data['Cumulative total per thousand'].apply(int)
            
            desired_cols = ['Date', 'Country', 'Cumulative total per thousand']
            tests_sub_data = selected_countries_tests_data[desired_cols]
            violin_tests_data = pd.DataFrame()
            '''
            for country in tests_sub_data.Country.unique():
                country_tests_violin_df = pd.DataFrame(columns=['Date', 'Country', 'Tests_per_thousand'])
                country_sub_data = tests_sub_data[tests_sub_data.Country==country]
                for date in country_sub_data.Date:
                    country_date_tests_violin_df = pd.DataFrame(columns=['Date', 'Country', 'Tests_per_thousand'])
                    country_sub_data_in_date = country_sub_data[country_sub_data.Date==date]
                    cum_per_thousand_in_date = int(country_sub_data_in_date.iloc[-1]['Cumulative total per thousand'])
                    tests_dates = [date for _ in range(cum_per_thousand_in_date)]
                    country_date_tests_violin_df['Date']=tests_dates
                    country_date_tests_violin_df['Country']=country
                    country_date_tests_violin_df['Tests_per_thousand']=cum_per_thousand_in_date
                    country_tests_violin_df=country_tests_violin_df.append(country_date_tests_violin_df)
                
                violin_tests_data=violin_tests_data.append(country_tests_violin_df)
            '''

            for country in tests_sub_data.Country.unique():
                country_tests_violin_df = pd.DataFrame(columns=['Date', 'Country', 'Tests_per_thousand', 'Violin_color'])
                country_sub_data = tests_sub_data[tests_sub_data.Country==country]
                for date in country_sub_data.Date:
                    country_date_tests_violin_df = pd.DataFrame(columns=['Date', 'Country', 'Tests_per_thousand', 'Violin_color'])
                    country_sub_data_in_date = country_sub_data[country_sub_data.Date==date]
                    cum_per_thousand_in_date = int(country_sub_data_in_date.iloc[-1]['Cumulative total per thousand'])
                    tests_dates = [date for _ in range(cum_per_thousand_in_date)]
                    country_date_tests_violin_df['Date']=tests_dates
                    country_date_tests_violin_df['Country']=country
                    country_date_tests_violin_df['Tests_per_thousand']=cum_per_thousand_in_date

                    country_tests_violin_df=country_tests_violin_df.append(country_date_tests_violin_df)
            
                country_tests_violin_df['Violin_color']=country_tests_violin_df['Tests_per_thousand'].max()
                violin_tests_data=violin_tests_data.append(country_tests_violin_df)

            import numpy as np
            import plotly.express as px

            fig = px.violin(violin_tests_data, y="Date", x="Country", #color=DEATH RATE 
                box=True,
                hover_data=['Date', 'Country'],
                title='Tests carried out per country',
                color='Violin_color') #range(0, len(violin_tests_data.Country.unique())))
            
            fig.update_layout(margin={"r":10,"t":60,"l":10,"b":10}, height=600, 
                              width=710, showlegend=False, paper_bgcolor="#EBF2EC") 
            return fig

        except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'return_tests_and_deaths_figure', exc))


'''
#%%
import pandas as pd
covid_data = pd.read_csv('https://raw.githubusercontent.com/GermanCM/Covid19_data_analyzer/master/data/covid19_ts_data.csv')
tests_data = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/testing/covid-testing-all-observations.csv', sep=',')
tests_countries_df = pd.DataFrame()
desired_cols = ['Entity', 'Date', 'Cumulative total', 'Daily change in cumulative total',
                'Cumulative total per thousand', 'Daily change in cumulative total per thousand']

tests_data['Country'] = tests_data.Entity.apply(lambda x: x.split('-')[0].strip())

#%%
import plotly.express as px
from page_numbers_normalized_by_population import normalized_numbers_by_population_evolution as population_num

multiselection = ['Germany', 'Spain', 'Italy', 'United States']
norm_nums_obj = population_num.Normalized_by_population_numbers_evolution(covid_data)
population_countries_df = norm_nums_obj.get_population_data(multiselection)
health_data_obj=Health_impact_evolution(covid_data)

multiselection_tests_data = ['United States' if x=='US' else x for x in multiselection]
selected_countries_tests_data = health_data_obj.get_tests_evolution_data(multiselection_tests_data)
selected_countries_tests_data

#%%
mask = [x in multiselection for x in tests_data.Country]
selected_countries = tests_data[mask]
selected_countries['Cumulative total per thousand']=selected_countries['Cumulative total per thousand'].apply(int)
selected_countries

desired_cols = ['Date', 'Country', 'Cumulative total per thousand']
tests_sub_data = selected_countries[desired_cols]
violin_tests_data = pd.DataFrame()
for country in tests_sub_data.Country.unique():
    country_tests_violin_df = pd.DataFrame(columns=['Date', 'Country', 'Tests_per_thousand', 'Violin_color'])
    country_sub_data = tests_sub_data[tests_sub_data.Country==country]
    for date in country_sub_data.Date:
        country_date_tests_violin_df = pd.DataFrame(columns=['Date', 'Country', 'Tests_per_thousand', 'Violin_color'])
        country_sub_data_in_date = country_sub_data[country_sub_data.Date==date]
        cum_per_thousand_in_date = int(country_sub_data_in_date['Cumulative total per thousand'])
        tests_dates = [date for _ in range(cum_per_thousand_in_date)]
        country_date_tests_violin_df['Date']=tests_dates
        country_date_tests_violin_df['Country']=country
        country_date_tests_violin_df['Tests_per_thousand']=cum_per_thousand_in_date

        country_tests_violin_df=country_tests_violin_df.append(country_date_tests_violin_df)
    
    country_tests_violin_df['Violin_color']=country_tests_violin_df['Tests_per_thousand'].max()
    violin_tests_data=violin_tests_data.append(country_tests_violin_df)

violin_tests_data

#%%
violin_tests_data['Color'] = pd.Series()
violin_tests_data[violin_tests_data.Country=='Germany']

#%%
import numpy as np
import plotly.express as px

fig = px.violin(violin_tests_data, y="Date", x="Country", #color=DEATH RATE 
                box=True,
                hover_data=['Date', 'Country'],
                title='Tests carried out per country',
                color='Violin_color') #range(0, len(violin_tests_data.Country.unique())))

fig.update_layout(showlegend=False)
fig.show()
'''


# %%
