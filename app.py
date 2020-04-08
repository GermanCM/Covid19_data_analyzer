#%%[markdown]
## COVID19 DASHBOARDS
import logging

logging.basicConfig(filename='covi19_dashboarder.log',
                    level=logging.ERROR, 
                    format='%(asctime)s %(message)s')
logger = logging.getLogger("covi19_dashboarder")
#%%
import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.title('COVID-19 data evolution')

def get_covid_data_csv(preprocessor):
    """This method retrieves the currently stored COVID19 data in the data folder; 
       also checks for any possible new data in the corresponding github repository
    
    Keyword Arguments:
        root_data_url {string} -- repository root URL (default: {DEFAULT_ROOT_DATA_URL})
    
    Returns:
        pandas dataframe -- dataset with covid dta history up to now
    """ 
    try:
        ts_all_data = preprocessor.get_current_data(ts_all_data_columns=['Country', 'Latitude', 'Longitude',
                                            'Confirmed', 'Deaths'])

        return ts_all_data
            
    except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'get_covid_data_csv', exc))

@st.cache(allow_output_mutation=True)
def load_data(preprocessor):
    try:
        data = get_covid_data_csv(preprocessor)
        return data

    except Exception as exc:
            logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'load_data', exc))
#%%
#loaded_data = load_data()

#%%
def main():
    try:
        import streamlit as st
        from data_preprocessor import preprocessor as prep
        from page_absolute_numbers import absolute_numbers_evolution as abs_evol
        from page_numbers_normalized_by_population import normalized_numbers_by_population_evolution as norm_evol
        import numpy as np

        preprocessor = prep.Preprocessor()
        data = load_data(preprocessor)
        
        page = st.sidebar.radio("Choose a page", ("Absolute numbers", "Numbers normalized by population", 
                                                  "Elderly impact", "Tests data", "Underlying health conditions & health investments"))
        
        # Default select: the top countries ordered by cumulative cases
        last_date_in_data = data.index[-1]
        last_day_data = data.loc[last_date_in_data]
        data['date'] = data.index

        top_countries_list = last_day_data.sort_values(by=['Confirmed'], ascending=False)['Country'].unique()[:3]
        default_countries_array = np.append(top_countries_list, np.array(['China']))
        default_countries_list = list(default_countries_array) 

        if page == "Absolute numbers":
            st.markdown(
                """
                ### This is a Covid19 data monitor with 2 main goals: 
                > - unifying some useful information from several data sources to get insights at a glance
                > - trying to make as fair as possible comparisons between countries evolution, with the
                    aim of getting some better understanding, and if possible learn some key factors  
                """)
            st.write(':warning: *keep in mind that these data is being collected with a high degree of urgency and surely with different criteria among countries, which could affect \
                    some conclusions drawn from it*')
            st.markdown("""
                        > The map below shows the evolution of absolute numbers of confirmed infections and deaths 
                        """)
            # MAP plot
            map_data_dict = {'Confirmed infections': 'Confirmed', 'Confirmed deaths': 'Deaths'} #, 'Confirmed recoverings': 'Recovered'}
            map_data_option = st.selectbox('Select data to show on the map', ('Confirmed infections', 'Confirmed deaths')) #, 'Confirmed recoverings'))
            
            abs_numbers_evol_obj = abs_evol.Absolute_numbers_evolution(data)
            fig_map = abs_numbers_evol_obj.return_map_evolution_figure(map_data_dict, map_data_option)

            st.write(':bulb: *Close the pages menu on the left or click on the fullscreen icon (expand symbol on the image) for a better view* ') 
                        
            st.plotly_chart(fig_map)

            # Multiselection of countries:
            country_options = list(data.Country.unique())
            st.markdown(
            """
            > The charts below show the evolution of covid19 worldwide since the beginning of February, available data: 
            > evolution of absolute numbers of confirmed infections and deaths
            > increments per day of confirmed infections and deaths
            """)

            multiselection = st.multiselect("Select countries (displayed by default the 3 top ones by number of informed infections + China as a reference):", 
                                            options=country_options, default=default_countries_list)

            st.write(':bulb: *Click on the chart option **compare data on hover** to see all countries data at once and fullscreen icon for a better view* ') 

            selected_country_mask = [x in multiselection for x in data.Country]
            selected_countries_data = data[selected_country_mask]

            # EVOLUTION LINE CHARTS
            fig_lines_chart = abs_numbers_evol_obj.return_lines_evolution_figure(selected_countries_data, multiselection)
            st.plotly_chart(fig_lines_chart)

            # INCREMENTS PER DAY
            fig_increments_bars = abs_numbers_evol_obj.return_bars_increments_evolution_figure(selected_countries_data, multiselection)
            st.plotly_chart(fig_increments_bars)

            st.write('*Now that you know the current absolute numbers, take a look at the **Numbers normalized by population** page* :mag:')

        elif page == "Numbers normalized by population":
            st.markdown("""___""")
            # Multiselection of countries:
            country_options = list(data.Country.unique())
            
            st.write(':mag: *These charts show the same values normalized by population to make a fair comparison between countries. \
            You can see here different numbers, showing the proportional impact based on their population*')

            multiselection = st.multiselect("Select countries (displayed by default the 3 top ones by number of informed infections + China as a reference):", 
                                            options=country_options, default=default_countries_list)

            st.write(':bulb: *Click on the chart option **compare data on hover** to see all countries data at once and fullscreen icon for a better view* ') 

            selected_country_mask = [x in multiselection for x in data.Country]
            selected_countries_data = data[selected_country_mask]

            norm_evol_obj = norm_evol.Normalized_by_population_numbers_evolution(data)
           
            # EVOLUTION LINE CHARTS
            fig_normalized_lines_chart = norm_evol_obj.return_normalized_lines_evolution_figure(selected_countries_data, multiselection)
            st.plotly_chart(fig_normalized_lines_chart)

            # INCREMENTS PER DAY
            st.write(':thought_balloon: *The normalized increments per day can give us a more realistic view of the proportional impact per country* ') 
            fig_normalized_increments_bars = norm_evol_obj.return_normalized_bars_increments_evolution_figure(selected_countries_data, multiselection)
            st.plotly_chart(fig_normalized_increments_bars)

       
        elif page=="Elderly impact":
            country_options = list(data.Country.unique())

            multiselection = st.multiselect("Select countries (displayed by default the 3 top ones by number of informed infections + China as a reference):", 
                                            options=country_options, default=default_countries_list)

            from page_health_data import health_data_comparer
            import pandas as pd
            
            health_data_comparer_obj = health_data_comparer.Health_impact_evolution(data)
            health_impact_ratio_fig = health_data_comparer_obj.get_current_deaths_confirmed_infections_impact(multiselection)

            st.subheader('Deaths over confirmed infections ratio')
            st.write('*The goal of this chart is to show the effectiveness on the health system per country, based only on deaths/confirmed cases ratio*')

            st.plotly_chart(health_impact_ratio_fig)

            st.write(':thought_balloon: *But we know elderly is the most vulnerable population by far, is it fair to compare countries deaths rates based on the whole population?*')

            from page_numbers_normalized_by_population import normalized_numbers_by_population_evolution as norm_evol
            
            norm_evol_obj = norm_evol.Normalized_by_population_numbers_evolution(data)
            abs_elderly_population_numbers = norm_evol_obj.get_absolute_elderly_population_numbers(multiselection)
            
            health_elderly_impact_ratio_fig = health_data_comparer_obj.get_current_deaths_elderly_impact(multiselection, abs_elderly_population_numbers)

            st.subheader('Deaths over elderly population ratio')
            st.write('*The goal of this chart is to show the effectiveness on the health system per country, based on deaths/elderly population ratio*')
            st.plotly_chart(health_elderly_impact_ratio_fig)

        elif page=="Tests data":
            from page_health_data import health_data_comparer
            import pandas as pd

            country_options = list(data.Country.unique())
            multiselection = st.multiselect("Select countries (displayed by default the 3 top ones by number of informed infections):", 
                                            options=country_options, default=default_countries_list[:2])

            health_data_comparer_obj = health_data_comparer.Health_impact_evolution(data)
            tests_and_deaths_figure = health_data_comparer_obj.return_tests_and_deaths_violin_figure(multiselection)

            st.subheader('Cumulative tests over time per country VS Cumulative deaths over time per country')
            st.write('*The goal of this chart is to show the impact of tests, and seeing a possible correlation between early tests and countries wit low deaths rates*')

            st.plotly_chart(tests_and_deaths_figure)

            #st.write(':bulb: *Click on the chart option **compare data on hover** to see all countries data at once and fullscreen icon for a better view* ') 

            selected_country_mask = [x in multiselection for x in data.Country]
            selected_countries_data = data[selected_country_mask]

            norm_evol_obj = norm_evol.Normalized_by_population_numbers_evolution(data)
           
            # EVOLUTION LINE CHARTS
            fig_normalized_lines_chart = norm_evol_obj.return_normalized_lines_evolution_figure(selected_countries_data, multiselection)
            st.plotly_chart(fig_normalized_lines_chart)


        elif page=="Underlying health conditions & health investments":
    
            #st.subheader('Infections VS Tests ratio--> NORMALIZAR!')
            
            #tests_data = pd.read_csv(r'.\external_data\tests-vs-confirmed-cases-covid-19.csv', sep=';')
            #not_nan_tests_mask = (tests_data.isna()['Total_COVID19_tests']==False)&(tests_data.isna()['Total_confirmed_cases']==False)
            #tests_data_filt = tests_data[not_nan_tests_mask]
            #tests_data_filt['Impact_ratio'] = (tests_data_filt['Total_confirmed_cases']*100/tests_data_filt['Total_COVID19_tests'])

            #import plotly.express as px

            #fig_tests = px.scatter(tests_data_filt, x="Total_COVID19_tests", 
            #                               y="Total_confirmed_cases", 
            #                               color="Impact_ratio",
            #                               size='Impact_ratio', hover_data=['Entity'])
            
            #fig_tests.update_layout(margin={"r":10,"t":60,"l":10,"b":2}, height=450, width=710, showlegend=False, paper_bgcolor="#EBF2EC") #legend=dict(x=-.18, y=1))         
            #st.plotly_chart(fig_tests)

            st.write(':construction: *Under construction, content coming soon*')
                
    except Exception as exc:
        st.write('**There was an error loading the requested data**')
        logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'main', exc))


if __name__ == "__main__":
    main()

st.markdown("""___""")

st.markdown(body="""
<a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licencia de Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />licensed under a <a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/"> Creative Commons Attribution 4.0 International License</a>
""", unsafe_allow_html=True)
