import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    import plotly.graph_objects as go
    plotly_available = True
except ImportError:
    plotly_available = False
    st.warning("Plotly is not available. Visualizations will be limited.")

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
        df = pd.read_csv('data/merged_dataset.csv', thousands=',')
        df.columns = df.columns.str.strip()
        
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
        
        df['Performance_Score'] = (df['OL_Percent_2019'] + df['AL_Percent_2020']) / 2
        df['Resource_Need_Index'] = df['STR_2020'] * (100 - df['Performance_Score']) / 100
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Failed to load data. Please ensure 'merged_dataset.csv' is available.")
    st.stop()

st.title("📊 Student Academic Performance & Resource Allocation Analysis")
st.markdown("Analyzing education performance, resource allocation, and enrollment trends across districts in Sri Lanka.")

st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Overview", "Performance Analysis", "Resource Allocation", "District Comparison", "Insights & Recommendations"])

# 1. Overview
if section == "Overview":
    st.header("Dataset Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Districts", len(df))
        st.metric("Total Students", f"{df['Total'].sum():,}")
    with col2:
        st.metric("Total Teachers", f"{df['Total_Teachers'].sum():,}")
        st.metric("Avg STR (2020)", f"{df['STR_2020'].mean():.1f}")
    with col3:
        st.metric("Avg OL Pass Rate (2019)", f"{df['OL_Percent_2019'].mean():.1f}%")
        st.metric("Avg AL Eligibility Rate (2020)", f"{df['AL_Percent_2020'].mean():.1f}%")
    st.subheader("District Summary")
    st.dataframe(df[['District', 'Total', 'Total_Teachers', 'STR_2020', 'OL_Percent_2019', 'AL_Percent_2020']])

# 2. Performance Analysis
elif section == "Performance Analysis":
    st.header("Academic Performance Analysis")
    tab1, tab2, tab3 = st.tabs(["OL Performance", "AL Performance", "Performance Trends"])

    with tab1:
        st.subheader("OL Exam Performance")
        if plotly_available:
            fig = px.bar(df.sort_values('OL_Percent_2019'), x='OL_Percent_2019', y='District', orientation='h',
                         color='OL_Percent_2019', title='OL Pass Rate by District (2019)',
                         color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
        low_perf_threshold = st.slider("Low performance threshold (%)", 40, 80, 60)
        low_perf_districts = df[df['OL_Percent_2019'] < low_perf_threshold]
        if not low_perf_districts.empty:
            st.subheader(f"Districts with OL Pass Rate Below {low_perf_threshold}%")
            st.dataframe(low_perf_districts[['District', 'OL_Percent_2019', 'STR_2020']])
    
    with tab2:
        st.subheader("AL Exam Performance")
        if plotly_available:
            fig = px.bar(df.sort_values('AL_Percent_2020'), x='AL_Percent_2020', y='District', orientation='h',
                         color='AL_Percent_2020', title='AL Eligibility Rate by District (2020)',
                         color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Performance Trends")
        col1, col2 = st.columns(2)
        with col1:
            district = st.selectbox("District for OL Trend", df['District'].unique())
            data = df[df['District'] == district].iloc[0]
            if plotly_available:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=[2015, 2019], y=[data['OL_Percent_2015'], data['OL_Percent_2019']], name='OL Pass Rate'))
                fig.update_layout(title=f"{district} - OL Trend", xaxis_title="Year", yaxis_title="Pass Rate (%)")
                st.plotly_chart(fig)
        with col2:
            district = st.selectbox("District for AL Trend", df['District'].unique())
            data = df[df['District'] == district].iloc[0]
            if plotly_available:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=[2015, 2020], y=[data['AL_Percent_2015'], data['AL_Percent_2020']], name='AL Eligibility'))
                fig.update_layout(title=f"{district} - AL Trend", xaxis_title="Year", yaxis_title="Rate (%)")
                st.plotly_chart(fig)

# 3. Resource Allocation
# elif section == "Resource Allocation":
#     st.header("Resource Allocation Analysis")
#     st.subheader("STR vs Performance")
#     if plotly_available:
#         fig = px.scatter(df, x='STR_2020', y='Performance_Score', size='Total',
#                          color='District', hover_data=['OL_Percent_2019', 'AL_Percent_2020'])
#         st.plotly_chart(fig)

#     st.subheader("High STR & Low Performance Districts")
#     high_str_low_perf = df[(df['STR_2020'] > 30) & (df['Performance_Score'] < 60)]
#     st.dataframe(high_str_low_perf[['District', 'STR_2020', 'Performance_Score', 'Total_Teachers']])

# # 4. District Comparison
# elif section == "District Comparison":
#     st.header("District Comparison")
#     col1, col2 = st.columns(2)
#     with col1:
#         dist1 = st.selectbox("Select District 1", df['District'].unique())
#     with col2:
#         dist2 = st.selectbox("Select District 2", df['District'].unique(), index=1)

#     d1 = df[df['District'] == dist1].iloc[0]
#     d2 = df[df['District'] == dist2].iloc[0]

#     metrics = ['OL_Percent_2019', 'AL_Percent_2020', 'Performance_Score', 'STR_2020']
#     data = pd.DataFrame({
#         'Metric': metrics,
#         dist1: [d1[m] for m in metrics],
#         dist2: [d2[m] for m in metrics]
#     })
#     st.dataframe(data)

# 4. District Comparison      
elif section == "District Comparison":
    st.header("District Comparison")
    col1, col2 = st.columns(2)
    with col1:
        dist1 = st.selectbox("Select District 1", df['District'].unique())
    with col2:
        dist2 = st.selectbox("Select District 2", df['District'].unique(), index=1)

    d1 = df[df['District'] == dist1].iloc[0]
    d2 = df[df['District'] == dist2].iloc[0]

    metrics = ['OL_Percent_2019', 'AL_Percent_2020', 'Performance_Score', 'STR_2020']
    data = pd.DataFrame({
        'Metric': metrics,
        dist1: [d1[m] for m in metrics],
        dist2: [d2[m] for m in metrics]
    })
    st.dataframe(data)
    
# 5. Insights & Recommendations
elif section == "Insights & Recommendations":
    st.header("📌 Insights & Recommendations")

    st.subheader("Lowest Performing Districts(Performance Score is less than 50")
    low_perf = df[df['Performance_Score'] < 50].sort_values('Performance_Score')
    if not low_perf.empty:
        st.dataframe(low_perf[['District', 'Performance_Score']])
        d = low_perf.iloc[0]
        st.markdown(f"👉 **{d['District']}** has the lowest score: **{d['Performance_Score']:.1f}**.")
        
    st.subheader("Lowest Performing Districts(Performance Score is less than 60")
    low_perf = df[df['Performance_Score'] < 60].sort_values('Performance_Score')
    if not low_perf.empty:
        st.dataframe(low_perf[['District', 'Performance_Score']])
        d = low_perf.iloc[0]
        st.markdown(f"👉 **{d['District']}** has the lowest score: **{d['Performance_Score']:.1f}**.")
    
    st.subheader("High STR & Low Performance")
    prob = df[(df['STR_2020'] > 30) & (df['Performance_Score'] < 60)]
    st.dataframe(prob[['District', 'STR_2020', 'Performance_Score']])

    st.subheader("Low Performance, Low STR")
    good = df[(df['STR_2020'] < 20) & (df['Performance_Score'] < 60)]
    st.dataframe(good[['District', 'STR_2020', 'Performance_Score']])

    st.subheader("High Performance, Low STR")
    good = df[(df['STR_2020'] < 20) & (df['Performance_Score'] > 70)]
    st.dataframe(good[['District', 'STR_2020', 'Performance_Score']])

    st.subheader("Teacher Allocation vs Performance")
    corr = df['Total_Teachers'].corr(df['Performance_Score'])
    st.metric("Correlation", f"{corr:.2f}")
    if plotly_available:
        fig = px.scatter(df, x='Total_Teachers', y='Performance_Score', color='District', size='Total')
        st.plotly_chart(fig)

    st.subheader("📌 General Recommendations")
    st.markdown("""
    - 🎯 Focus support on districts with **Performance Score < 50**.
    - 👩‍🏫 Reduce **Student-Teacher Ratios > 30** in underperforming districts.
    - 📚 Invest in **teacher training** and **after-school programs**.
    - 🔁 Replicate best practices from **high-performing, low STR** districts.
    - 📈 Use data to **optimize resource allocation**.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Data Source: Ministry of Education, Sri Lanka")
