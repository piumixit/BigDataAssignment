import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    plotly_available = True
except ImportError:
    plotly_available = False
    st.warning("Plotly is not available. Some visualizations may be limited.")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    matplotlib_available = True
except ImportError:
    matplotlib_available = False
    st.warning("Matplotlib/Seaborn is not available. Some visualizations may be limited.")

# Set page configuration
st.set_page_config(
    page_title="Education Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and preprocess data
@st.cache_data
def load_data():
    try:
        # Read the CSV file
        df = pd.read_csv('data/merged_dataset.csv', thousands=',')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Convert numeric columns to appropriate types
        numeric_cols = ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6', 
                       'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11-1st', 
                       'Grade 11 repeaters', 'Grade 12', 'Grade 13', 'Special education', 
                       'Total', 'Total_Teachers', 'Male_Teachers', 'Female_Teachers',
                       'Male_Percentage', 'Female_Percentage', 'STR_2015', 'STR_2020',
                       'OL_Sat_2015', 'OL_Passed_2015', 'OL_Percent_2015', 'OL_Sat_2019',
                       'OL_Passed_2019', 'OL_Percent_2019', 'AL_Sat_2015', 'AL_Eligible_2015',
                       'AL_Percent_2015', 'AL_Sat_2020', 'AL_Eligible_2020', 'AL_Percent_2020']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate performance indicators
        df['Performance_Score'] = (df['OL_Percent_2019'] + df['AL_Percent_2020']) / 2
        df['Resource_Need_Index'] = df['STR_2020'] * (100 - df['Performance_Score']) / 100
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
df = load_data()

# Check if data loaded successfully
if df.empty:
    st.error("Failed to load data. Please check if merged_dataset.csv is in the correct location.")
    st.stop()

# App title
st.title("📊 Student Academic Performance & Resource Allocation Analysis")
st.markdown("""
This dashboard analyzes student academic performance, teacher allocation, and enrollment trends across districts in Sri Lanka.
Identify districts with low performance and investigate relationships with student-teacher ratios and enrollment patterns.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", 
                          ["Overview", "Performance Analysis", "Resource Allocation", 
                           "District Comparison", "Insights & Recommendations"])

# Overview section
if section == "Overview":
    st.header("Dataset Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Districts", len(df))
        st.metric("Total Students", f"{df['Total'].sum():,}")
        
    with col2:
        st.metric("Total Teachers", f"{df['Total_Teachers'].sum():,}")
        st.metric("Average Student-Teacher Ratio (2020)", f"{df['STR_2020'].mean():.1f}")
    
    with col3:
        st.metric("Average OL Pass Rate (2019)", f"{df['OL_Percent_2019'].mean():.1f}%")
        st.metric("Average AL Eligibility Rate (2020)", f"{df['AL_Percent_2020'].mean():.1f}%")
    
    st.subheader("District Summary")
    st.dataframe(df[['District', 'Total', 'Total_Teachers', 'STR_2020', 
                    'OL_Percent_2019', 'AL_Percent_2020']].sort_values('Total', ascending=False))

# Performance Analysis section
elif section == "Performance Analysis":
    st.header("Academic Performance Analysis")
    
    tab1, tab2, tab3 = st.tabs(["OL Performance", "AL Performance", "Performance Trends"])
    
    with tab1:
        st.subheader("Ordinary Level (OL) Exam Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if plotly_available:
                fig = px.bar(df.sort_values('OL_Percent_2019', ascending=True), 
                            x='OL_Percent_2019', y='District', orientation='h',
                            title='OL Pass Rate by District (2019)',
                            color='OL_Percent_2019', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'OL_Percent_2019']].sort_values('OL_Percent_2019', ascending=True))
        
        with col2:
            if plotly_available:
                fig = px.scatter(df, x='STR_2020', y='OL_Percent_2019', 
                                size='Total', color='District',
                                title='OL Pass Rate vs Student-Teacher Ratio (2020)',
                                hover_data=['District', 'STR_2020', 'OL_Percent_2019'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'STR_2020', 'OL_Percent_2019', 'Total']])
        
        # Low performing districts
        low_perf_threshold = st.slider("Low performance threshold (%)", 40, 80, 60)
        low_perf_districts = df[df['OL_Percent_2019'] < low_perf_threshold]
        
        if not low_perf_districts.empty:
            st.subheader(f"Districts with OL Pass Rate Below {low_perf_threshold}%")
            st.dataframe(low_perf_districts[['District', 'OL_Percent_2019', 'STR_2020', 'Total_Teachers']])
        else:
            st.info(f"No districts with OL pass rate below {low_perf_threshold}%")
    
    with tab2:
        st.subheader("Advanced Level (AL) Exam Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if plotly_available:
                fig = px.bar(df.sort_values('AL_Percent_2020', ascending=True), 
                            x='AL_Percent_2020', y='District', orientation='h',
                            title='AL Eligibility Rate by District (2020)',
                            color='AL_Percent_2020', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'AL_Percent_2020']].sort_values('AL_Percent_2020', ascending=True))
        
        with col2:
            if plotly_available:
                fig = px.scatter(df, x='STR_2020', y='AL_Percent_2020', 
                                size='Total', color='District',
                                title='AL Eligibility Rate vs Student-Teacher Ratio (2020)',
                                hover_data=['District', 'STR_2020', 'AL_Percent_2020'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'STR_2020', 'AL_Percent_2020', 'Total']])
        
        # Correlation analysis
        corr_ol_str = df['OL_Percent_2019'].corr(df['STR_2020'])
        corr_al_str = df['AL_Percent_2020'].corr(df['STR_2020'])
        
        st.metric("Correlation: OL Pass Rate vs STR", f"{corr_ol_str:.3f}")
        st.metric("Correlation: AL Eligibility Rate vs STR", f"{corr_al_str:.3f}")
    
    with tab3:
        st.subheader("Performance Trends Over Time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_district_ol = st.selectbox("Select District for OL Trends", df['District'].unique(), key='ol_trend')
            district_data_ol = df[df['District'] == selected_district_ol]
            
            if plotly_available:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=[2015, 2019], 
                                        y=[district_data_ol['OL_Percent_2015'].values[0], 
                                           district_data_ol['OL_Percent_2019'].values[0]],
                                        mode='lines+markers', name='OL Pass Rate'))
                fig.update_layout(title=f'OL Performance Trend: {selected_district_ol}',
                                 xaxis_title='Year', yaxis_title='Pass Rate (%)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(f"OL Pass Rate for {selected_district_ol}:")
                st.write(f"2015: {district_data_ol['OL_Percent_2015'].values[0]:.1f}%")
                st.write(f"2019: {district_data_ol['OL_Percent_2019'].values[0]:.1f}%")
        
        with col2:
            selected_district_al = st.selectbox("Select District for AL Trends", df['District'].unique(), key='al_trend')
            district_data_al = df[df['District'] == selected_district_al]
            
            if plotly_available:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=[2015, 2020], 
                                        y=[district_data_al['AL_Percent_2015'].values[0], 
                                           district_data_al['AL_Percent_2020'].values[0]],
                                        mode='lines+markers', name='AL Eligibility Rate'))
                fig.update_layout(title=f'AL Performance Trend: {selected_district_al}',
                                 xaxis_title='Year', yaxis_title='Eligibility Rate (%)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(f"AL Eligibility Rate for {selected_district_al}:")
                st.write(f"2015: {district_data_al['AL_Percent_2015'].values[0]:.1f}%")
                st.write(f"2020: {district_data_al['AL_Percent_2020'].values[0]:.1f}%")

# Continue with the rest of the app sections...

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Data Source:** Sri Lanka Education Ministry
    \n**Note:** This analysis focuses on government schools across districts.
    Student-Teacher Ratio (STR) is calculated as Total Students / Total Teachers.
    """
)
