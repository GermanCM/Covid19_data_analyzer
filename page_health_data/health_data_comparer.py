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
            