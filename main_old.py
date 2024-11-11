import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
# from datetime import datetime
import plotly.express as px
import random  # Importing the random module
from datetime import timedelta, datetime

# import psycopg2

# Setting up Page Config
st.set_page_config(page_title="Jobs Canada Dashboard", layout="wide")

# Simulated Data
def load_data():
    # Generate a date range to establish a consistent number of rows
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq='M')
    num_entries = len(dates)  # This ensures consistency across all arrays

    # Generate random data for each column
    data = {
        'date': dates,
        'demand_increase': np.random.randint(0, 20, num_entries),
        'num_companies': np.random.randint(5, 15, num_entries),
        'num_jobs': np.random.randint(20, 50, num_entries),
        'skills': np.random.choice(['Python', 'SQL', 'R', 'Spark', 'Tableau'], num_entries),
        'soft_skills': np.random.choice(['Communications', 'Esprit d_equipe', 'Autonomie', 'Rigeure', 'Dynamise'], num_entries),
        'ville_offre_last_Q': np.random.choice(['Montréal', 'Toronto', 'Calgary', 'Sherbrooke', 'Laval'], num_entries),
        'locations': np.random.choice(['Quebec', 'Ontario', 'Alberta', 'British Columbia'], num_entries),
        'sectors': np.random.choice(['Finance', 'IT', 'Healthcare', 'Education', 'Retail'], num_entries),
        
        # New fields
        'title': np.random.choice([
            'Data Analyst', 'Data Engineer', 'Data Scientist', 
            'Machine Learning Engineer', 'Business Intelligence Analyst'
        ], num_entries),
        
        'hourly_rate': np.random.randint(40, 100, num_entries),  # hourly rate between $40 - $100
        
        'link': [f"https://jobportal.com/job/{random.randint(1000, 9999)}" for _ in range(num_entries)],
        
        'posted_date': [datetime.now() - timedelta(days=random.randint(0, 365)) for _ in range(num_entries)]
    }
    
    # Convert to DataFrame
    return pd.DataFrame(data)

# Loading data
df = load_data()

#######################################################################
# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
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
# selected_job_role = st.sidebar.selectbox("Select Job Role", ["Data Analyst", "Data Engineer", "Data Scientist"])
# selected_province = st.sidebar.selectbox("Select Province", df['locations'].unique())
# selected_date_range = st.sidebar.date_input("Select Period", [datetime(2024, 1, 1), datetime(2024, 12, 31)])

# Page Navigation
# st.sidebar.title("Navigate Pages")
# page = st.sidebar.radio("Choose a page:", ["Overview", "Demand Analysis", "Regional Distribution"])
annual_salary_range = np.random.randint(90000, 150000)
demand_increase = np.random.randint(5, 15)
demand_increase_delta=format_number(demand_increase)
num_companies = np.random.randint(5, 15)
num_jobs = np.random.randint(20, 50)


# selected_date_range2=st.date_input("Select Period2", [datetime(2024, 1, 1), datetime(2024, 12, 31)])
page = st.sidebar.radio("Choose a page:", ["Overview", "Demand Analysis", "Regional Distribution"])
# page = st.selectbox("Choose a page:", ["Overview", "Demand Analysis", "Regional Distribution"])




# Page 1: Overview
if page == "Overview":
    st.title("Overview of Job Market in Canada")
    ov_filter_col = st.columns((1.5,3.5, 1.5, 1.5), gap='medium')
    with ov_filter_col[0]:
        
        
        selected_date_range = st.date_input("Select Period", [datetime(2024, 1, 1), datetime(2024, 12, 31)])
                                        
    with ov_filter_col[2]:
        selected_province = st.selectbox("Select Province", df['locations'].unique())
        
    with ov_filter_col[3]:
        selected_job_role = st.selectbox("Select Job Role", ["Data Analyst", "Data Engineer", "Data Scientist"])
    
    col = st.columns((2, 6), gap='medium')
    

        
    with col[0]:
        st.metric("Annual Salary Range", "90$ K - 150$ K")
        
        # Language Proficiency
        st.subheader("Languages Required")
        language_data = pd.DataFrame({
            'Language': ['English', 'French', 'Other'],
            'Proportion': [65, 25, 10]
        })
        # st.pie_chart(language_data, values='Proportion', names='Language')
        fig_language = px.pie(language_data, values='Proportion', names='Language', title="Languages Required")
        # Displaying the plotly pie chart
        st.plotly_chart(fig_language)
        
        # # Mode de travail
        # st.subheader("Mode de travail")
        # work_mode = pd.DataFrame({
        #     'Language': ['Télétravail', 'Hybride', 'Sur site'],
        #     'Proportion': [50, 35, 15]
        # })
        # fig_work_mode = px.pie(work_mode, values='Proportion', names='Mode', title="Work mode")
        # # Displaying the plotly pie chart
        # st.plotly_chart(fig_work_mode)
        # Mode de travail
        st.subheader("Niveau d'étude exigé")
        education_level = pd.DataFrame({
        'Level': ['Maitrise', 'Baccalauréat', 'DEC', 'PHD'],
            'Proportion': [45, 35, 15, 5]
        })
        fig_education_level = px.pie(education_level, values='Proportion', names='Level', title="Niveau d'étude exigé")
        # Displaying the plotly pie chart
        st.plotly_chart(fig_education_level)
        
        
    with col[1]:
        # Displaying Main KPIs
        col1, col2, col3 = st.columns(3)
        
        col1.metric(label="Demand Increase", value=demand_increase, delta=demand_increase_delta)
        col2.metric("Number of Companies", value=num_companies,delta=demand_increase_delta)
        col3.metric("Number of Companies", value=num_jobs,delta=demand_increase_delta)
        # st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)
        
        
        line2_col = st.columns((4, 4), gap='medium')
        with line2_col[0]:
            st.subheader("Soft Skills")
            # soft_skill_counts = pd.DataFrame({
            #     'Soft_skills': df['soft_skills'],
            #     'Count': np.random.randint(10, 80, len(df['soft_skills']))
            # })
            # st.bar_chart(soft_skill_counts, x='Soft_skills', y='Count')
            # Competency Analysis
            competency_data = pd.DataFrame({
                'Competency': ['Communication', 'Teamwork', 'Autonomy', 'Creativity', 'Flexibility'],
                'Requirement': np.random.randint(10, 80, 5)
            })
            st.bar_chart(competency_data, x='Competency', y='Requirement')
            # ville_offre_last_Q
        with line2_col[1]:
            # st.subheader("Job Openings Over Time")
            # demand_chart = alt.Chart(df).mark_line().encode(
            #     x='date:T',
            #     y='demand_increase:Q',
            #     tooltip=['date', 'demand_increase']
            # ).properties(width=600)
            # st.altair_chart(demand_chart)
            st.subheader("Les 5 villes qui ont plus d'offres sur le dernier trimestre")
            soft_skill_counts = pd.DataFrame({
                'ville_offre_last_Q': df['ville_offre_last_Q'],
                'Count': np.random.randint(10, 80, len(df['soft_skills']))
            })
            st.bar_chart(soft_skill_counts, x='ville_offre_last_Q', y='Count')
        # Skills Required
        # st.subheader("Skills Required")
        # skill_counts = pd.DataFrame({
        #     'Skill': df['skills'],
        #     'Count': np.random.randint(10, 70, len(df['skills']))
        # })
        # st.bar_chart(skill_counts, x='Skill', y='Count')
        
        #Job listings
        st.subheader("Job Listings")
        job_listings = df[['title', 'sectors', 'hourly_rate', 'link']]
        
        st.table(job_listings)
        
        # # Language Proficiency
        # st.subheader("Languages Required")
        # language_data = pd.DataFrame({
        #     'Language': ['English', 'French', 'Other'],
        #     'Proportion': [65, 25, 10]
        # })
        # # st.pie_chart(language_data, values='Proportion', names='Language')
        # fig = px.pie(language_data, values='Proportion', names='Language', title="Languages Required")
        # # Displaying the plotly pie chart
        # st.plotly_chart(fig)



# Page 2: Demand Analysis
elif page == "Demand Analysis":
    st.title("Demand Analysis")
    da_filter_col = st.columns((1.5,3.5, 1.5, 1.5), gap='medium')
    with da_filter_col[0]:
        
        
        selected_date_range = st.date_input("Select Period", [datetime(2024, 1, 1), datetime(2024, 12, 31)])
                                        
    with da_filter_col[2]:
        selected_province = st.selectbox("Select Province", df['locations'].unique())
        
    with da_filter_col[3]:
        selected_job_role = st.selectbox("Select Job Role", ["Data Analyst", "Data Engineer", "Data Scientist"])
    
    col = st.columns((2, 6), gap='medium')
    

        
    with col[0]:
        st.metric("Annual Salary Range", "90$ K - 150$ K")
        
        # Mode de travail
        st.subheader("Mode de travail")
        work_mode = pd.DataFrame({
            'Work_mode': ['Télétravail', 'Hybride', 'Sur site'],
            'Proportion': [50, 35, 15]
        })
        fig_work_mode = px.pie(work_mode, values='Proportion', names='Work_mode', title="Work mode")
        # Displaying the plotly pie chart
        st.plotly_chart(fig_work_mode)
        # Niveau d'expertise
        st.subheader("Niveau d'expertise demandé")
        expertise_level = pd.DataFrame({
        'Level': ['Stagiaire', 'Junior', 'Senior', 'Consultant'],
            'Proportion': [45, 35, 15, 5]
        })
        fig_expertise_level = px.pie(expertise_level, values='Proportion', names='Level', title="Niveau expertise demandé")
        # Displaying the plotly pie chart
        st.plotly_chart(fig_expertise_level)
        
        
    with col[1]:
        # Displaying Main KPIs
        col1, col2, col3 = st.columns(3)
        
        col1.metric(label="Demand Increase", value=demand_increase, delta=demand_increase_delta)
        col2.metric("Number of Companies", value=num_companies,delta=demand_increase_delta)
        col3.metric("Number of Companies", value=num_jobs,delta=demand_increase_delta)
        # st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)
        
        
        line2_col = st.columns((4, 4), gap='medium')
        with line2_col[0]:
            # st.subheader("Soft Skills")
            # soft_skill_counts = pd.DataFrame({
            #     'Soft_skills': df['soft_skills'],
            #     'Count': np.random.randint(10, 80, len(df['soft_skills']))
            # })
            # st.bar_chart(soft_skill_counts, x='Soft_skills', y='Count')
            
            # Monthly Demand Evolution
            st.subheader("Job Openings Over Time")
            demand_chart = alt.Chart(df).mark_line().encode(
                x='date:T',
                y='demand_increase:Q',
                tooltip=['date', 'demand_increase']
            ).properties(width=600)
            st.altair_chart(demand_chart)
            # ville_offre_last_Q
        with line2_col[1]:
            # st.subheader("Job Openings Over Time")
            # demand_chart = alt.Chart(df).mark_line().encode(
            #     x='date:T',
            #     y='demand_increase:Q',
            #     tooltip=['date', 'demand_increase']
            # ).properties(width=600)
            # st.altair_chart(demand_chart)
            
            # Skills Required
            st.subheader("Skills Required")
            skill_counts = pd.DataFrame({
                'Skill': df['skills'],
                'Count': np.random.randint(10, 70, len(df['skills']))
            })
            st.bar_chart(skill_counts, x='Skill', y='Count')
        
        
        line3_col = st.columns((4, 4), gap='medium')
        with line3_col[0]:
            # Job Distribution by Sector
            # choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
            # st.plotly_chart(choropleth, use_container_width=True)
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
            st.subheader("Number of Jobs by Sector")
            sector_data = pd.DataFrame({
                'Sector': df['sectors'],
                'Job Openings': np.random.randint(1000, 20000, len(df['sectors']))
            })
            st.bar_chart(sector_data, x='Sector', y='Job Openings')
            

    


# Page 3: Regional Distribution
elif page == "Regional Distribution":
    st.title("Regional and Sectoral Distribution")
    
    # Job Distribution by Location
    st.subheader("Job Distribution in Canada")
    # Placeholder for map chart. Streamlit's pydeck_chart can be used with actual geospatial data.
    map_data = pd.DataFrame({
        'lat': [45.4215, 43.65107, 51.0447, 53.5461],
        'lon': [-75.6972, -79.347015, -114.0719, -113.4938],
        'city': ['Ottawa', 'Toronto', 'Calgary', 'Edmonton']
    })
    st.map(map_data)

    
