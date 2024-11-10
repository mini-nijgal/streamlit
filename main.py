import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import random  # Importing the random module
from datetime import timedelta, datetime
import psycopg2
from load_data import load_data 
from load_data import load_json_to_dataframe
import os
# import folium


# Setting up Page Config
st.set_page_config(page_title="Jobs Canada Dashboard", layout="wide")



# Loading data
data = load_json_to_dataframe("data/job_data.json")

#######################################################################
# Calcul du trimestre précédent basé sur la date sélectionnée
def get_previous_quarter(date):
    quarter = (date.month - 1) // 3
    start_month = (quarter - 1) * 3 + 1 if quarter > 0 else 10
    start_year = date.year if quarter > 0 else date.year - 1
    start_date = pd.Timestamp(start_year, start_month, 1)
    end_date = pd.Timestamp(start_year, start_month + 2, 1) + pd.offsets.MonthEnd(1)
    return start_date, end_date


def create_pie_chart(dataframe, column, title,show_title=True):
    # Check if the column contains any data
    if dataframe[column].dropna().empty:
        return "No data available"
    
    # Split the specified column by ', ' for multivalued cells, explode into rows, count occurrences
    data_counts = dataframe[column].str.split(', ').explode().value_counts().reset_index()
    data_counts.columns = ['Category', 'Count']
    
    # Check if there are any counts after the explode operation
    if data_counts.empty:
        return "No data available"
    
    # Generate the pie chart
    if show_title:
        fig = px.pie(data_counts, values='Count', names='Category', title=title)
    else:
        fig = px.pie(data_counts, values='Count', names='Category')
    
    return fig

def create_bar_chart(dataframe, column, title, nb='all',show_title=True):
    # Check if the column contains any data
    if dataframe[column].dropna().empty:
        return "No data available"
    
    # Split the specified column by ', ' for multivalued cells and explode into rows
    exploded_data = dataframe[column].str.split(', ').explode().dropna()

    # If there is no data after the explode (i.e., all rows were empty or invalid)
    if exploded_data.empty:
        return "No data available"
    
    # Count occurrences of unique values in the exploded column
    data_counts = exploded_data.value_counts().reset_index()
    data_counts.columns = ['Category', 'Count']
    
    # Filter the data based on 'nb' parameter
    if nb != 'all':
        data_counts = data_counts.head(nb)  # Get top 'nb' categories
    
    # Generate the bar chart with or without title
    if show_title:
        fig = px.bar(data_counts, x='Category', y='Count', title=title, labels={'Category': column, 'Count': 'Count'})
    else:
        fig = px.bar(data_counts, x='Category', y='Count', labels={'Category': column, 'Count': 'Count'})

    return fig

def create_line_chart(dataframe):
    # fonction a améliorer
    """
    Fonction qui retourne un graphique en ligne montrant l'évolution des offres d'emploi de façon mensuelle.
    
    Paramètres :
    - dataframe : La dataframe contenant les données des offres d'emploi filtrées avec une colonne de dates.
    
    Retour :
    - Un graphique Altair représentant l'évolution mensuelle des offres d'emploi.
    """
    
    # Extraire l'année et le mois pour le regroupement
    dataframe['YearMonth'] = dataframe['date'].dt.to_period('M').dt.to_timestamp()

    # Regrouper par mois et compter le nombre d'offres
    df_monthly = dataframe.groupby('YearMonth').size().reset_index(name="Job Openings")

    # Créer un graphique en ligne avec Altair
    demand_chart = alt.Chart(df_monthly).mark_line().encode(
        x='YearMonth:T',
        y='Job Openings:Q',
        tooltip=['YearMonth', 'Job Openings']
    ).properties(
        title="Job Openings Over Time (Monthly)",
        width=600
    )

    return demand_chart

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# User filter
def user_filter():
    filter_col = st.columns((1.5,3.5, 1.5, 1.5), gap='medium')
    with filter_col[0]:
        selected_date_range = st.date_input("Select Period", [datetime(2024, 1, 1), datetime(2024, 12, 31)])

    with filter_col[2]:
        selected_province = st.selectbox("Select Province", data['locations'].unique())
        
    with filter_col[3]:
        selected_job_role = st.selectbox("Select Job Role", ["Data Analyst", "Data Engineer", "Data Scientist"])
    return selected_date_range, selected_province, selected_job_role


# Choropleth map
def make_choropleth2(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(input_df[input_column])),
                               scope="usa",  # Utilisation du geojson pour délimiter les provinces canadiennes
                               labels={input_column: input_column.capitalize()}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

def make_choropleth(input_df, input_id, input_column, input_color_theme):
    """
    Fonction pour créer une carte choroplèthe pour le Canada.
    
    Paramètres:
    - input_df : DataFrame contenant les données des provinces canadiennes.
    - input_id : Nom de la colonne représentant les identifiants des provinces.
    - input_column : Nom de la colonne contenant les valeurs à visualiser (ex: population, revenus, etc.).
    - input_color_theme : Thème de couleur pour la carte (ex: 'Viridis', 'Cividis', etc.).
    
    Retourne:
    - Une carte choroplèthe.
    """
    # Charger le fichier GeoJSON des provinces du Canada
    # Vous pouvez obtenir ce fichier depuis une source publique, par exemple sur GitHub ou d'autres plateformes.
    canada_geojson_url = "https://raw.githubusercontent.com/marcopeix/streamlit-population-canada/master/data/canada.geojson"

    # Créer la carte choroplèthe avec Plotly Express
    choropleth = px.choropleth(input_df, 
                               locations=input_id, 
                               color=input_column, 
                               geojson=canada_geojson_url,
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(input_df[input_column])),
                            #    scope="africa",  # Utilisation du geojson pour délimiter les provinces canadiennes
                               labels={input_column: input_column.capitalize()}
                              )

    # Mettre à jour le layout
    choropleth.update_geos(fitbounds="locations", visible=False)
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )

    return choropleth

#######################################################################

# Sidebar Filters
st.sidebar.header("Filter Options")



# selected_date_range2=st.date_input("Select Period2", [datetime(2024, 1, 1), datetime(2024, 12, 31)])
page = st.sidebar.radio("Choose a page:", ["Home", "Page1", "Page2"])
# page = st.selectbox("Choose a page:", ["Page1", "Page1", "Page2"])

if page != "Home": # If the page is not the home page, display the title
    st.title(page)
    selected_date_range, selected_province, selected_job_role = user_filter()

    # Vérifier que le range de dates contient une date de fin
    if len(selected_date_range) < 2 or selected_date_range[1] == 'null':
        #pd.Timestamp.today() or datetime(2024, 12, 31)
        selected_date_range = [selected_date_range[0],pd.Timestamp.today()]

    # Filter data based on the selected date range
    # Convert selected date range to datetime64 to match the data['date'] dtype
    selected_start_date = pd.to_datetime(selected_date_range[0])
    selected_end_date = pd.to_datetime(selected_date_range[1])
    # Filter data based on user selections
    filtered_data = data[
        (data['date'] >= selected_start_date) & 
        (data['date'] <= selected_end_date) &
        (data['locations'] == selected_province) &
        (data['title'] == selected_job_role)
    ]

    # Calculate minimum and maximum salary from the filtered data
    min_salary = filtered_data['salary'].min() if not filtered_data.empty else 0
    max_salary = filtered_data['salary'].max() if not filtered_data.empty else 0
else:
    filter_col = st.columns((1.5,3.5, 1.5, 1.5), gap='medium')
    with filter_col[0]:
        selected_date_range = st.date_input("Select Period", [datetime(2024, 1, 1), datetime(2024, 12, 31)])
    with filter_col[3]:
        selected_job_role = st.selectbox("Select Job Role", ["Data Analyst", "Data Engineer", "Data Scientist"])
        
    # Vérifier que le range de dates contient une date de fin
    if len(selected_date_range) < 2 or selected_date_range[1] == 'null':
        #pd.Timestamp.today() or datetime(2024, 12, 31)
        selected_date_range = [selected_date_range[0],pd.Timestamp.today()]
        
    selected_start_date = pd.to_datetime(selected_date_range[0])
    selected_end_date = pd.to_datetime(selected_date_range[1])
    # Filter data based on user selections
    filtered_data = data[
        (data['date'] >= selected_start_date) & 
        (data['date'] <= selected_end_date) &
        (data['title'] == selected_job_role)
    ]

# Page 1: Overview
if page == "Page1":
    #User Filter
    
    col = st.columns((2, 6), gap='medium')
    with col[0]:
        
        st.metric("Annual Salary Range", f"{format_number(min_salary)} - {format_number(max_salary)}")
        
        # Visualisation des langues requises
        st.subheader("Languages Required")
        fig_language = create_pie_chart(filtered_data, 'language', "Languages Required",show_title=False)
        if isinstance(fig_language, str) and fig_language == "No data available":
            st.write(fig_language)  # This will display the message in Streamlit or print it in the console
        else:
            st.plotly_chart(fig_language) 

        # Niveau d'étude exigé
        st.subheader("Niveau d'étude exigé")
        
        fig_education_level = create_pie_chart(filtered_data, 'education_level', "Niveau d'étude exigé",show_title=False)

        if isinstance(fig_education_level, str) and fig_education_level == "No data available":
            st.write(fig_education_level)  # This will display the message in Streamlit or print it in the console
        else:
            st.plotly_chart(fig_education_level) 
        
        
    with col[1]:
        # Displaying Main KPIs
        col1, col2, col3 = st.columns(3)
        
        col1.metric(label="Demand Increase", value=filtered_data['num_jobs'].sum(), delta=format_number(filtered_data['num_jobs'].sum()))
        col2.metric("Number of Companies", value=filtered_data['company'].nunique(), delta=format_number(filtered_data['company'].nunique()))
        col3.metric("Number of Jobs",value=filtered_data['num_jobs'].sum(), delta=format_number(filtered_data['num_jobs'].sum()))
        
        
        line2_col = st.columns((4, 4), gap='medium')
        with line2_col[0]:
            st.subheader("Soft Skills")
            
            # Competency Analysis
            fig_soft_skills = create_bar_chart(filtered_data, 'soft_skills', "All Skills Distribution", nb='all', show_title=False)

            if isinstance(fig_soft_skills, str) and fig_soft_skills == "No data available":
                st.write(fig_soft_skills)  # If no data is available, show the message
            else:
                st.plotly_chart(fig_soft_skills)  # Display the bar chart if data is available
                
        with line2_col[1]:
            # Display the results in a bar chart
            st.subheader("Les 5 villes qui ont plus d'offres sur la période sélectionnée")
            
            fig_city_counts = create_bar_chart(filtered_data, 'ville_offre_last_Q', "All Skills Distribution", nb=5, show_title=False)

            if isinstance(fig_city_counts, str) and fig_city_counts == "No data available":
                st.write(fig_city_counts)  # If no data is available, show the message
            else:
                st.plotly_chart(fig_city_counts)

        search_term = st.text_input("Search a for job", "")
        if search_term:
            jobs_listing_data = filtered_data[filtered_data.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        else:
            jobs_listing_data = filtered_data
        
        # Liste des offres d'emploi
        st.subheader("Job Listings")
        # st.dataframe(jobs_listing_data[['title', 'sectors', 'salary', 'link']]) # Display the job listings in a dataframe
        st.table(jobs_listing_data[['title', 'sectors', 'salary', 'link']])



# Page 2: Page2
elif page == "Page2":
    col = st.columns((2, 6), gap='medium')
        
    with col[0]:
        st.metric("Annual Salary Range", "90$ K - 150$ K")
        
        # Mode de travail
        # Calculer la proportion de chaque mode de travail dans les données
        st.subheader("Mode de travail")
        fig_work_mode = create_pie_chart(filtered_data, 'work_mode', "Mode de travail",show_title=False)
        if isinstance(fig_work_mode, str) and fig_work_mode == "No data available":
            st.write(fig_work_mode)  # This will display the message in Streamlit or print it in the console
        else:
            st.plotly_chart(fig_work_mode) 
    
        # Niveau d'expertise
        
        # Afficher le graphique
        st.subheader("Niveau d'expertise exigé")
        fig_expertise_level = create_pie_chart(filtered_data, 'education_level', "Niveau d'expertise exigé",show_title=False)
        if isinstance(fig_expertise_level, str) and fig_expertise_level == "No data available":
            st.write(fig_expertise_level)  # This will display the message in Streamlit or print it in the console
        else:
            st.plotly_chart(fig_expertise_level) 
        
        
    with col[1]:
        # Displaying Main KPIs
        col1, col2, col3 = st.columns(3)
        
        col1.metric(label="Demand Increase", value=filtered_data['num_jobs'].sum(), delta=format_number(filtered_data['num_jobs'].sum()))
        col2.metric("Number of Companies", value=filtered_data['company'].nunique(), delta=format_number(filtered_data['company'].nunique()))
        col3.metric("Number of Jobs",value=filtered_data['num_jobs'].sum(), delta=format_number(filtered_data['num_jobs'].sum()))
        
        
        line2_col = st.columns((4, 4), gap='medium')
        with line2_col[0]:
            
            # Chart des ouvertures d'emploi dans le temps
            st.subheader("Job Openings Over Time")
            # demand_chart = alt.Chart(data).mark_line().encode(
            #     x='date:T',
            #     y='demand_increase:Q',
            #     tooltip=['date', 'demand_increase']
            # )
            fig_demand_chart = create_line_chart(filtered_data)
            st.altair_chart(fig_demand_chart)

        with line2_col[1]:

            
            # Skills Required
            # Chart des compétences requises
            st.subheader("Skills Required")
            fig_skills = create_bar_chart(filtered_data, 'skills', "All Skills Distribution", nb='all', show_title=False)
            if isinstance(fig_skills, str) and fig_skills == "No data available":
                st.write(fig_skills)  # If no data is available, show the message
            else:
                st.plotly_chart(fig_skills)  # Display the bar chart if data is available
        
        line3_col = st.columns((4, 4), gap='medium')
        with line3_col[0]:
            # Job Distribution by Location
            st.subheader("Job Distribution in Canada")
            # Placeholder for map chart. Streamlit's pydeck_chart can be used with actual geospatial data.
            map_data = pd.DataFrame({
                'lat': [45.4215, 43.65107, 51.0447, 53.5461],
                'lon': [-75.6972, -79.347015, -114.0719, -113.4938],
                'city': ['Ottawa', 'Toronto', 'Calgary', 'Edmonton']
            })
            st.map(map_data)
        with line3_col[1]:
            
            # Job Distribution by Sector
            st.subheader("Job Distribution by Sector")
            
            # Calculer le nombre d'offres d'emploi par secteur
            sector_data = filtered_data['sectors'].value_counts().reset_index()
            sector_data.columns = ['Sector', 'Job Openings']

            # Créer un graphique à barres
            fig_sector = px.bar(sector_data, x='Sector', y='Job Openings', title="Job Distribution by Sector", 
                                labels={'Sector': 'Sector', 'Job Openings': 'Number of Jobs'}, 
                                color='Job Openings', 
                                color_continuous_scale='Viridis')

            # Afficher le graphique
            st.plotly_chart(fig_sector)


# Page 0 : acceuil: Home
elif page == "Home":

    # st.header("La plateforme qu'il vous faut pour planifier votre carriere professionnelle....")
    
    st.title("Jobs Canada🍁")
    rd_line2_col = st.columns((4, 4), gap='medium')
    with rd_line2_col[0]:
        # Job Distribution by Location
        st.subheader("Repartition des offres sur le territoire Canadien")
        # Placeholder for map chart. Streamlit's pydeck_chart can be used with actual geospatial data.
        map_data = pd.DataFrame({
            'lat': [45.4215, 43.65107, 51.0447, 53.5461],
            'lon': [-75.6972, -79.347015, -114.0719, -113.4938],
            'city': ['Ottawa', 'Toronto', 'Calgary', 'Edmonton']
        })
        st.map(map_data)

    # Affichage de la carte dans Streamlit ou autre environnement
    # st.plotly_chart(choropleth_map)
    with rd_line2_col[1]:
        
        # Visualisation des provinces
        st.subheader("Provinces Distribution")
        fig_provinces = create_pie_chart(filtered_data, 'locations', "Provinces",show_title=False)
        if isinstance(fig_provinces, str) and fig_provinces == "No data available":
            st.write(fig_provinces)  # This will display the message in Streamlit or print it in the console
        else:
            st.plotly_chart(fig_provinces)


# cur.close()
# conn.close()