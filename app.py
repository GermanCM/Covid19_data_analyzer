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
                                                  "Deaths impact", "Tests data", "Underlying health conditions",
                                                  "Health investment"))
        
        # Default select: the top countries ordered by cumulative cases
        last_date_in_data = data.index[-1]
        last_day_data = data.loc[last_date_in_data]
        data['date'] = data.index

        top_countries_list = last_day_data.sort_values(by=['Confirmed'], ascending=False)['Country'].unique()[:5]
        default_countries_list = list(top_countries_list) 
        top_countries_list_elderly = last_day_data.sort_values(by=['Deaths'], ascending=False)['Country'].unique()[:10]
        default_countries_list_elderly = list(top_countries_list_elderly) 
        top_countries_list_tests = last_day_data.sort_values(by=['Deaths'], ascending=False)['Country'].unique()[:8]
        default_countries_list_tests = list(top_countries_list_tests)

        if page == "Absolute numbers":
            st.markdown(
                """
                ### This is a Covid19 data monitor with 2 main goals: 
                > - unifying some useful information from several data sources to get insights at a glance
                > - trying to make as fair as possible comparisons between countries evolution and not comparing just absolute numbers, 
                    with the aim of getting some better understanding, and analyze some possible relevant factors  
                """)
            st.write(':warning: *keep in mind these data are being collected with a high degree of urgency and surely with different criteria among countries, which could affect \
                    some conclusions drawn from it*')
            st.markdown("""
                        > The map below shows the evolution of absolute numbers of confirmed infections and deaths. As we can see, it has actually become a pandemic due to the spread over the continents (below the pandemic definition).  
                        <a href="https://en.wikipedia.org/wiki/Pandemic"> Pandemic definition</a>""", unsafe_allow_html=True)
            #st.markdown(body="""<a href="https://en.wikipedia.org/wiki/Pandemic"> Pandemic definition</a>""", unsafe_allow_html=True)

            # MAP plot
            map_data_dict = {'Confirmed infections': 'Confirmed', 'Confirmed deaths': 'Deaths'} 
            map_data_option = st.selectbox('Select data to show on the map', ('Confirmed infections', 'Confirmed deaths')) 
            
            abs_numbers_evol_obj = abs_evol.Absolute_numbers_evolution(data)
            fig_map = abs_numbers_evol_obj.return_map_evolution_figure(map_data_dict, map_data_option)

            st.write(':bulb: *Click on the __play__ icon to see the evolution. Close the pages menu on the left or click on the fullscreen icon for a better view* ') 
                        
            st.plotly_chart(fig_map)

            # Multiselection of countries:
            country_options = list(data.Country.unique())
            st.markdown(
            """
            > The charts below show the evolution of covid19 worldwide since the beginning of February, available data: 
            > evolution of absolute numbers of confirmed infections and deaths
            > increments per day of confirmed infections and deaths
            """)

            multiselection = st.multiselect("Select countries (displayed by default the 5 top ones by number of informed infections):", 
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

            multiselection = st.multiselect("Select countries (displayed by default the 3 top ones by number of informed infections):", 
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
            st.write(':warning: *Data is shown as informed by the Johns Hopkins University via its github repository with no correction made. Do not hesitate to contact via the channels shown at the footnotes*')
            fig_normalized_increments_bars = norm_evol_obj.return_normalized_bars_increments_evolution_figure(selected_countries_data, multiselection)
            st.plotly_chart(fig_normalized_increments_bars)

       
        elif page=="Deaths impact":

            country_options = list(data.Country.unique())

            multiselection_elderly = st.multiselect("Select countries (displayed by default the 3 top ones by number of informed infections):", #+ China as a reference):", 
                                            options=country_options, default=default_countries_list_elderly)

            from page_health_data import health_data_comparer
            import pandas as pd
            
            health_data_comparer_obj = health_data_comparer.Health_impact_evolution(data)
            health_impact_ratio_fig = health_data_comparer_obj.get_current_deaths_confirmed_infections_impact(multiselection_elderly)

            st.subheader('Deaths over confirmed infections ratio')
            st.write('*The goal of this chart is to show the effectiveness of the health system per country, based only on deaths/confirmed cases ratio*')
            st.write(':pencil: *Definition:*')
            st.markdown("""$$health\_impact = {deaths \over confirmed\_infections}$$""")

            st.plotly_chart(health_impact_ratio_fig)

            st.write(':thought_balloon: *But we know elderly is the most vulnerable population by far, is it fair to compare countries deaths rates based on the whole population?*')

            from page_numbers_normalized_by_population import normalized_numbers_by_population_evolution as norm_evol
            
            norm_evol_obj = norm_evol.Normalized_by_population_numbers_evolution(data)
            abs_elderly_population_numbers = norm_evol_obj.get_absolute_elderly_population_numbers(multiselection_elderly)
            
            health_elderly_impact_ratio_fig = health_data_comparer_obj.get_current_deaths_elderly_impact(multiselection_elderly, abs_elderly_population_numbers)

            st.subheader('Impact on the elderly population')
            st.write('*The goal of this chart is to show the effectiveness on the health system per country, based on deaths/elderly population ratio*')
            st.write(':pencil: *Definitions:*')
            st.markdown("""$$elderly\_population = {population\_80\_years\_old\_and\_over}$$  ,  $$elderly\_health\_impact = {deaths \over elderly\_population}$$""")
            st.plotly_chart(health_elderly_impact_ratio_fig)

            #st.write(':thought_balloon: *As we could expect, the real impact *')

        elif page=="Tests data":
            from page_health_data import health_data_comparer
            import pandas as pd

            country_options = list(data.Country.unique())
            multiselection_tests = st.multiselect("Select countries (displayed by default the 4 top ones by number of informed infections):", 
                                            options=country_options, default=default_countries_list_tests)

            health_data_comparer_obj = health_data_comparer.Health_impact_evolution(data)
            violin_tests_data_figure = health_data_comparer_obj.return_tests_and_deaths_violin_figure(multiselection_tests)

            st.subheader('Cumulative tests over time per country VS Cumulative deaths over time per country')
            st.write('*The goal of this chart is to show the impact of tests, and seeing a possible correlation between early tests and countries with low deaths rates; the width of each country violin is proportional the number of tests carried out at that date on the y-axis*')
            st.write(':bulb: *The width of each country violin represents the ratio of tests made the corresponding date on the y axis*') 
            st.write(':warning: *Not all countries have officially informed tests data yet*')
            st.plotly_chart(violin_tests_data_figure)

            #st.write(':bulb: *Click on the chart option **compare data on hover** to see all countries data at once and fullscreen icon for a better view* ') 

            selected_country_mask = [x in multiselection_tests for x in data.Country]
            selected_countries_data = data[selected_country_mask]

            norm_evol_obj = norm_evol.Normalized_by_population_numbers_evolution(data)
           
            # EVOLUTION LINE CHARTS
            fig_normalized_lines_chart = norm_evol_obj.return_normalized_lines_evolution_figure(selected_countries_data, multiselection_tests)
            st.plotly_chart(fig_normalized_lines_chart)


        elif page=="Underlying health conditions":
            from page_health_data import health_data_comparer

            country_options = list(data.Country.unique())
            multiselection_health_conditions = st.multiselect("Select countries:", options=country_options, default=default_countries_list_tests)
            
            health_data_comparer_obj = health_data_comparer.Health_impact_evolution(data)
            deaths_vs_respiratory_morbidity_fig = health_data_comparer_obj.return_deaths_vs_respiratory_morbidity_fig(multiselection_health_conditions)

            st.subheader('Deaths rate VS Underlying health conditions')
            st.write('*The goal of this chart is to show the influence of underlying respiratory deaths rate on Covid19 deaths per country*')
            st.write('*On the x-axis, you can see the respiratory deaths rate per country, and the death rate due to covid on the y-axis*')
            st.write(':bulb: *The bigger and yellower a bubble is, the higher the deaths rate is. Can we see any possible correlation? You can add more countries via the Select countries search box*') 
            st.write(':warning: *Not all countries have officially informed underlying health conditions*')

            st.plotly_chart(deaths_vs_respiratory_morbidity_fig)

            st.write('*More info coming about investments on health system per country*')

        elif page=="Health investment":
            from page_health_data import health_data_comparer

            country_options = list(data.Country.unique())
            multiselection_health_conditions = st.multiselect("Select countries:", options=country_options, default=default_countries_list_tests)
            
            health_data_comparer_obj = health_data_comparer.Health_impact_evolution(data)
            deaths_vs_respiratory_morbidity_fig = health_data_comparer_obj.return_deaths_vs_health_investment_share_fig(multiselection_health_conditions)

            st.subheader('Deaths rate VS Investments on health sector')
            st.write('*The goal of this chart is to show the influence of health investments per country on Covid19 deaths per country.*')
            st.write('*On the x-axis, you can see the share of gross domestic product for the health sector per country, and the death rate due to covid on the y-axis*')
            st.write(':bulb: *The bigger and yellower a bubble is, the higher the deaths rate is. Can we see any possible correlation? You can add mopre countries via the Select countries search box*') 

            st.plotly_chart(deaths_vs_respiratory_morbidity_fig)
                
    except Exception as exc:
        st.write('**There was an error loading the requested data**')
        logger.exception('raised exception at {}: {}'.format(logger.name+'.'+ 'main', exc))

#%%
if __name__ == "__main__":
    main()

st.write(':information_source: *data sources: *') 
st.markdown(body="""Covid19 data evolution: <a href="https://github.com/CSSEGISandData/COVID-19"> Data Repository by Johns Hopkins CSSE</a> """, unsafe_allow_html=True)
st.markdown(body="""External data sources: <a href="https://ourworldindata.org/"> ourworldindata.org</a>, <a href="https://stats.oecd.org/"> stats.oecd.org</a> """, unsafe_allow_html=True)

st.markdown("""___""")

st.markdown(body="""
<a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />Licensed under a <a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/"> Creative Commons Attribution 4.0 International License</a>
""", unsafe_allow_html=True)

st.markdown(body="""
GitHub content: <a href="https://github.com/GermanCM/Covid19_data_analyzer"> GermanCM github repository</a>
""", unsafe_allow_html=True)

st.markdown(body="""
Contact info: <a href="https://www.linkedin.com/in/german-cm/"> LinkedIn account</a>
""", unsafe_allow_html=True)