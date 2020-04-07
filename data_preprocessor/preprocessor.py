#%%
class Preprocessor():
    def __init__(self):
        from pathlib import Path
        
        self.current_data_confirmed_ = None
        self.current_data_deaths_ = None
        self.path_ = Path('.\data')

    def change_date_format(self, x):
        try:
            date_elements = x.split('/')
            year = '20'+date_elements[2]
            day = ('0' + date_elements[1]) if (int(date_elements[1])+1) <11 else date_elements[1]
            month = ('0' + date_elements[0]) if int(date_elements[0])<11 else date_elements[0]

            return year+'-'+month+'-'+day
        except Exception as exc:
            return exc

    def get_current_data(self, ts_all_data_columns):
        try:
            from datetime import datetime, timedelta
            from tqdm import tqdm
            import pandas as pd
            import numpy as np
            '''
            ### Dataframe a rellenar 
            ts_all_data = pd.DataFrame(columns=['Country', 'Latitude', 'Longitude',
                                                'Confirmed', 'Deaths'])
            '''
            ####################TIME SERIES FILES
            DATA_PATH_CONFIRMED = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
            DATA_PATH_DEATHS = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
            #DATA_PATH_RECOVERED = 'https://raw.githubusercontent.com/GermanCM/COVID-19/my_updated_master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
            
            self.current_data_confirmed_ = pd.read_csv(filepath_or_buffer=DATA_PATH_CONFIRMED, sep=',')
            self.current_data_deaths_ = pd.read_csv(filepath_or_buffer=DATA_PATH_DEATHS, sep=',')
            #current_data_recovered = pd.read_csv(filepath_or_buffer=DATA_PATH_RECOVERED, sep=',')

            ts_all_data = pd.DataFrame(columns=ts_all_data_columns)
            time_columns = self.current_data_confirmed_.columns[4:]
            date_new_names = pd.Series(time_columns).apply(self.change_date_format).values

            today_date = datetime.today().date()
            #current_data = pd.read_csv('\covid19_ts_data.csv')
            current_data = pd.read_csv(self.path_ / 'covid19_ts_data.csv')
            current_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True) 
            current_data.set_index('Date', inplace=True)
            last_date_in_data = current_data.index[-1] 

            # convert string last_date to datetime
            last_date_array = last_date_in_data.split('-')
            last_date_year = int(last_date_array[0])
            last_date_month = int(last_date_array[1])
            last_date_day = int(last_date_array[2])
            last_date_in_data=datetime(year=last_date_year, month=last_date_month, day=last_date_day).date()

            if last_date_in_data < (today_date+timedelta(days=-1)):
                country_with_colonies=list([])
                country_with_provinces=list([])
                unique_countries = self.current_data_confirmed_['Country/Region'].unique()
                countries_regions = self.current_data_confirmed_['Country/Region']
                while last_date_in_data < (today_date+timedelta(days=-1)):    
                    for country in unique_countries:
                        if len(self.current_data_confirmed_[[country in x for x in countries_regions]])>1:
                            country_provinces = np.array(self.current_data_confirmed_[[country in x for x in countries_regions]]['Province/State'].values)
                            if pd.isnull(country_provinces).any():
                                country_with_colonies.append(country)
                            else:
                                country_with_provinces.append(country)

                    rest_of_countries = [x for x in unique_countries if ((x not in country_with_colonies)&(x not in country_with_provinces))]

                    #country_with_colonies
                    for country in tqdm(rest_of_countries):
                        # CONFIRMED INFECTIONS DATA
                        this_country_CONFIRMED_data_mask=self.current_data_confirmed_['Country/Region']==country
                        this_country_CONFIRMED_data = self.current_data_confirmed_[this_country_CONFIRMED_data_mask]
                        #por cada país (esto es, cada columna numérica correspondiente a país/región)
                        this_country_ts_CONFIRMED_values = this_country_CONFIRMED_data[this_country_CONFIRMED_data.columns[4:]].T
                        this_country_ts_CONFIRMED_values.index = date_new_names

                        # CONFIRMED DEATHS DATA
                        this_country_DEATHS_data_mask=self.current_data_deaths_['Country/Region']==country
                        this_country_DEATHS_data = self.current_data_deaths_[this_country_DEATHS_data_mask]
                        #por cada país (esto es, cada columna numérica correspondiente a país/región)
                        this_country_ts_DEATHS_values = this_country_DEATHS_data[this_country_DEATHS_data.columns[4:]].T
                        this_country_ts_DEATHS_values.index = date_new_names
                        
                        ts_country_data=pd.DataFrame(index=date_new_names)
                        ts_country_data['Country']=country
                        #country_mask = self.current_data_confirmed_['Country/Region']==country_name
                        ts_country_data['Latitude']=this_country_CONFIRMED_data['Lat'].iloc[0]
                        ts_country_data['Longitude']=this_country_CONFIRMED_data['Long'].iloc[0]

                        ts_country_data['Confirmed']=this_country_ts_CONFIRMED_values
                        ts_country_data['Deaths']=this_country_ts_DEATHS_values
                        #ts_country_data['Recovered']=ts_recovered_values[countries_dict[country]]
                        
                        ts_all_data = ts_all_data.append(ts_country_data)

                    #%%
                    from tqdm import tqdm
                    #country_with_colonies
                    for country in tqdm(country_with_colonies):
                        # we only get country data whose province/region is null 
                        # CONFIRMED INFECTIONS DATA
                        this_country_with_colonies_CONFIRMED_data_mask=self.current_data_confirmed_['Country/Region']==country
                        this_country_with_colonies_CONFIRMED_data = self.current_data_confirmed_[this_country_with_colonies_CONFIRMED_data_mask]
                        main_country_CONFIRMED_data_mask=pd.isna(this_country_with_colonies_CONFIRMED_data['Province/State']) 
                        this_country_CONFIRMED_data=this_country_with_colonies_CONFIRMED_data[main_country_CONFIRMED_data_mask]

                        #por cada país (esto es, cada columna numérica correspondiente a país/región)
                        this_country_ts_CONFIRMED_values = this_country_CONFIRMED_data[this_country_CONFIRMED_data.columns[4:]].T
                        this_country_ts_CONFIRMED_values.index = date_new_names
                        # CONFIRMED DEATHS DATA
                        this_country_with_colonies_DEATHS_data_mask=self.current_data_deaths_['Country/Region']==country
                        this_country_with_colonies_DEATHS_data = self.current_data_deaths_[this_country_with_colonies_DEATHS_data_mask]
                        main_country_DEATHS_data_mask=pd.isna(this_country_with_colonies_DEATHS_data['Province/State']) 
                        this_country_DEATHS_data=this_country_with_colonies_DEATHS_data[main_country_DEATHS_data_mask]

                        #por cada país (esto es, cada columna numérica correspondiente a país/región)
                        this_country_ts_DEATHS_values = this_country_DEATHS_data[this_country_DEATHS_data.columns[4:]].T
                        this_country_ts_DEATHS_values.index = date_new_names
                        
                        ts_country_data=pd.DataFrame(index=date_new_names)
                        ts_country_data['Country']=country
                        #country_mask = self.current_data_confirmed_['Country/Region']==country_name
                        ts_country_data['Latitude']=this_country_CONFIRMED_data['Lat'].iloc[0]
                        ts_country_data['Longitude']=this_country_CONFIRMED_data['Long'].iloc[0]

                        ts_country_data['Confirmed']=this_country_ts_CONFIRMED_values
                        ts_country_data['Deaths']=this_country_ts_DEATHS_values
                        #ts_country_data['Recovered']=ts_recovered_values[countries_dict[country]]
                        
                        ts_all_data = ts_all_data.append(ts_country_data)

                    #%%
                    #country_with_provinces
                    for country in tqdm(country_with_provinces):
                        coordinates_dict = {'China': {'Latitude': 40.1824,'Longitude': 116.4142}, 
                                        'Australia': {'Latitude': -35.4735, 'Longitude': 149.0124},	
                                        'Canada': {'Latitude': 49.2827, 'Longitude': -123.1207}}	
                        # we only get country data whose province/region is null 
                        # CONFIRMED INFECTIONS DATA
                        this_country_with_colonies_CONFIRMED_data_mask=self.current_data_confirmed_['Country/Region']==country
                        this_country_with_colonies_CONFIRMED_data = self.current_data_confirmed_[this_country_with_colonies_CONFIRMED_data_mask]
                        #main_country_CONFIRMED_data_mask=pd.isna(this_country_with_colonies_CONFIRMED_data['Province/State']) 
                        this_country_CONFIRMED_data=this_country_with_colonies_CONFIRMED_data.groupby(by='Country/Region').sum()

                        #por cada país (esto es, cada columna numérica correspondiente a país/región)
                        this_country_ts_CONFIRMED_values = this_country_CONFIRMED_data[this_country_CONFIRMED_data.columns[2:]].T
                        this_country_ts_CONFIRMED_values.index = date_new_names
                        # CONFIRMED DEATHS DATA
                        this_country_with_colonies_DEATHS_data_mask=self.current_data_deaths_['Country/Region']==country
                        this_country_with_colonies_DEATHS_data = self.current_data_deaths_[this_country_with_colonies_DEATHS_data_mask]
                        #main_country_DEATHS_data_mask=pd.isna(this_country_with_colonies_DEATHS_data['Province/State']) 
                        this_country_DEATHS_data=this_country_with_colonies_DEATHS_data.groupby(by='Country/Region').sum()
                        
                        #por cada país (esto es, cada columna numérica correspondiente a país/región)
                        this_country_ts_DEATHS_values = this_country_DEATHS_data[this_country_DEATHS_data.columns[2:]].T
                        this_country_ts_DEATHS_values.index = date_new_names
                        
                        ts_country_data=pd.DataFrame(index=date_new_names)
                        ts_country_data['Country']=country
                        #country_mask = self.current_data_confirmed_['Country/Region']==country_name
                        ts_country_data['Latitude']=coordinates_dict[country]['Latitude']
                        ts_country_data['Longitude']=coordinates_dict[country]['Longitude']

                        ts_country_data['Confirmed']=this_country_ts_CONFIRMED_values
                        ts_country_data['Deaths']=this_country_ts_DEATHS_values
                        #ts_country_data['Recovered']=ts_recovered_values[countries_dict[country]]
                        
                        ts_all_data = ts_all_data.append(ts_country_data)

                    ts_all_data.to_csv(path_or_buf=r'..\data\covid19_ts_data.csv')

                    last_date_in_data = datetime(ts_all_data.index[-1])

                return ts_all_data

            else:
                current_data = pd.read_csv(self.path_ / 'covid19_ts_data.csv')
                current_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True) 
                current_data.set_index('Date', inplace=True)

                return current_data

        except Exception:
            current_data = pd.read_csv(self.path_ / 'covid19_ts_data.csv')
            current_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True) 
            current_data.set_index('Date', inplace=True)

            return current_data
