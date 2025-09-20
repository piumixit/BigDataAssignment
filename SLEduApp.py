import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

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
    # Read the CSV file
    df = pd.read_csv('merged_dataset.csv', thousands=',')
    
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

# Load the data
df = load_data()

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
            fig = px.bar(df.sort_values('OL_Percent_2019', ascending=True), 
                        x='OL_Percent_2019', y='District', orientation='h',
                        title='OL Pass Rate by District (2019)',
                        color='OL_Percent_2019', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(df, x='STR_2020', y='OL_Percent_2019', 
                            size='Total', color='District',
                            title='OL Pass Rate vs Student-Teacher Ratio (2020)',
                            hover_data=['District', 'STR_2020', 'OL_Percent_2019'])
            st.plotly_chart(fig, use_container_width=True)
        
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
            fig = px.bar(df.sort_values('AL_Percent_2020', ascending=True), 
                        x='AL_Percent_2020', y='District', orientation='h',
                        title='AL Eligibility Rate by District (2020)',
                        color='AL_Percent_2020', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(df, x='STR_2020', y='AL_Percent_2020', 
                            size='Total', color='District',
                            title='AL Eligibility Rate vs Student-Teacher Ratio (2020)',
                            hover_data=['District', 'STR_2020', 'AL_Percent_2020'])
            st.plotly_chart(fig, use_container_width=True)
        
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
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[2015, 2019], 
                                    y=[district_data_ol['OL_Percent_2015'].values[0], 
                                       district_data_ol['OL_Percent_2019'].values[0]],
                                    mode='lines+markers', name='OL Pass Rate'))
            fig.update_layout(title=f'OL Performance Trend: {selected_district_ol}',
                             xaxis_title='Year', yaxis_title='Pass Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            selected_district_al = st.selectbox("Select District for AL Trends", df['District'].unique(), key='al_trend')
            district_data_al = df[df['District'] == selected_district_al]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[2015, 2020], 
                                    y=[district_data_al['AL_Percent_2015'].values[0], 
                                       district_data_al['AL_Percent_2020'].values[0]],
                                    mode='lines+markers', name='AL Eligibility Rate'))
            fig.update_layout(title=f'AL Performance Trend: {selected_district_al}',
                             xaxis_title='Year', yaxis_title='Eligibility Rate (%)')
            st.plotly_chart(fig, use_container_width=True)

# Resource Allocation section
elif section == "Resource Allocation":
    st.header("Resource Allocation Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Teacher Distribution", "STR Analysis", "Enrollment Patterns"])
    
    with tab1:
        st.subheader("Teacher Distribution Across Districts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df.sort_values('Total_Teachers', ascending=False), 
                        x='Total_Teachers', y='District', orientation='h',
                        title='Total Teachers by District',
                        color='Total_Teachers', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(df, values='Total_Teachers', names='District',
                        title='Proportion of Teachers by District')
            st.plotly_chart(fig, use_container_width=True)
        
        # Teacher gender distribution
        st.subheader("Teacher Gender Distribution")
        
        gender_df = pd.DataFrame({
            'District': df['District'],
            'Male Teachers': df['Male_Teachers'],
            'Female Teachers': df['Female_Teachers']
        })
        
        fig = px.bar(gender_df.melt(id_vars='District', var_name='Gender', value_name='Count'), 
                    x='District', y='Count', color='Gender',
                    title='Teacher Gender Distribution by District',
                    barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Student-Teacher Ratio Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df.sort_values('STR_2020', ascending=False), 
                        x='STR_2020', y='District', orientation='h',
                        title='Student-Teacher Ratio by District (2020)',
                        color='STR_2020', color_continuous_scale='RdBu_r')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(df, x='Total', y='STR_2020', 
                            size='Total_Teachers', color='District',
                            title='STR vs Total Students',
                            hover_data=['District', 'Total', 'STR_2020', 'Total_Teachers'])
            st.plotly_chart(fig, use_container_width=True)
        
        # STR change over time
        st.subheader("STR Change (2015-2020)")
        df['STR_Change'] = df['STR_2020'] - df['STR_2015']
        
        fig = px.bar(df.sort_values('STR_Change', ascending=True), 
                    x='STR_Change', y='District', orientation='h',
                    title='Change in Student-Teacher Ratio (2015-2020)',
                    color='STR_Change', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Enrollment Patterns")
        
        # Prepare enrollment data
        grade_cols = [f'Grade {i}' for i in range(1, 14)] + ['Grade 11-1st', 'Grade 11 repeaters', 'Special education']
        enrollment_df = df[['District'] + grade_cols].melt(
            id_vars='District', var_name='Grade', value_name='Enrollment')
        
        # Overall enrollment by grade
        grade_totals = enrollment_df.groupby('Grade')['Enrollment'].sum().reset_index()
        
        fig = px.bar(grade_totals, x='Grade', y='Enrollment',
                    title='Total Enrollment by Grade Level')
        st.plotly_chart(fig, use_container_width=True)
        
        # Enrollment distribution by district
        selected_grade = st.selectbox("Select Grade", grade_cols)
        grade_data = df[['District', selected_grade]].sort_values(selected_grade, ascending=False)
        
        fig = px.bar(grade_data, x=selected_grade, y='District', orientation='h',
                    title=f'Enrollment in {selected_grade} by District')
        st.plotly_chart(fig, use_container_width=True)

# District Comparison section
elif section == "District Comparison":
    st.header("District Comparison")
    
    # Select districts to compare
    selected_districts = st.multiselect(
        "Select districts to compare", 
        df['District'].unique(), 
        default=[df['District'].iloc[0], df['District'].iloc[1]]
    )
    
    if len(selected_districts) >= 2:
        compare_df = df[df['District'].isin(selected_districts)]
        
        tabs = st.tabs(["Performance", "Resources", "Enrollment"])
        
        with tabs[0]:
            st.subheader("Performance Comparison")
            
            fig = make_subplots(rows=1, cols=2, subplot_titles=('OL Pass Rate', 'AL Eligibility Rate'))
            
            fig.add_trace(
                go.Bar(x=compare_df['District'], y=compare_df['OL_Percent_2019'], name='OL Pass Rate'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=compare_df['District'], y=compare_df['AL_Percent_2020'], name='AL Eligibility Rate'),
                row=1, col=2
            )
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[1]:
            st.subheader("Resource Comparison")
            
            fig = make_subplots(rows=1, cols=2, subplot_titles=('Total Teachers', 'Student-Teacher Ratio'))
            
            fig.add_trace(
                go.Bar(x=compare_df['District'], y=compare_df['Total_Teachers'], name='Teachers'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=compare_df['District'], y=compare_df['STR_2020'], name='STR'),
                row=1, col=2
            )
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Gender distribution comparison
            gender_fig = go.Figure()
            
            for district in selected_districts:
                district_data = df[df['District'] == district].iloc[0]
                gender_fig.add_trace(go.Bar(
                    name=district,
                    x=['Male', 'Female'],
                    y=[district_data['Male_Percentage'], district_data['Female_Percentage']]
                ))
            
            gender_fig.update_layout(barmode='group', title='Teacher Gender Distribution (%)')
            st.plotly_chart(gender_fig, use_container_width=True)
        
        with tabs[2]:
            st.subheader("Enrollment Comparison")
            
            # Prepare enrollment data for selected districts
            enrollment_data = compare_df[['District'] + [f'Grade {i}' for i in range(1, 14)]].melt(
                id_vars='District', var_name='Grade', value_name='Enrollment')
            
            fig = px.line(enrollment_data, x='Grade', y='Enrollment', color='District',
                         title='Enrollment Pattern by Grade')
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("Please select at least two districts for comparison.")

# Insights & Recommendations section
elif section == "Insights & Recommendations":
    st.header("Insights & Recommendations")
    
    # Identify priority districts
    priority_df = df.nlargest(5, 'Resource_Need_Index')[['District', 'STR_2020', 'Performance_Score', 'Resource_Need_Index']]
    
    st.subheader("Top 5 Priority Districts for Resource Allocation")
    st.dataframe(priority_df.style.format({
        'STR_2020': '{:.1f}',
        'Performance_Score': '{:.1f}%',
        'Resource_Need_Index': '{:.2f}'
    }).background_gradient(subset=['Resource_Need_Index'], cmap='Reds'))
    
    # Key insights
    st.subheader("Key Insights")
    
    insight1, insight2, insight3 = st.columns(3)
    
    with insight1:
        high_str = df[df['STR_2020'] > df['STR_2020'].mean() + df['STR_2020'].std()]
        st.metric("Districts with High STR (> Mean + SD)", len(high_str))
    
    with insight2:
        low_perf = df[df['Performance_Score'] < df['Performance_Score'].mean() - df['Performance_Score'].std()]
        st.metric("Districts with Low Performance (< Mean - SD)", len(low_perf))
    
    with insight3:
        high_corr = df['STR_2020'].corr(df['Performance_Score'])
        st.metric("Correlation between STR and Performance", f"{high_corr:.3f}")
    
    # Recommendations
    st.subheader("Actionable Recommendations")
    
    rec1, rec2, rec3 = st.columns(3)
    
    with rec1:
        st.info("""
        **Resource Allocation Priority:**
        - Focus on districts with high Student-Teacher Ratios and low academic performance
        - Consider redistributing teachers from over-resourced to under-resourced districts
        """)
    
    with rec2:
        st.info("""
        **Teacher Recruitment Strategy:**
        - Target male teacher recruitment in districts with gender imbalance
        - Provide incentives for teachers to work in remote/low-performing districts
        """)
    
    with rec3:
        st.info("""
        **Performance Improvement:**
        - Implement targeted academic support programs in low-performing districts
        - Share best practices from high-performing districts
        - Monitor STR changes and their impact on academic performance
        """)
    
    # Detailed district recommendations
    st.subheader("District-Specific Recommendations")
    
    for _, row in priority_df.iterrows():
        with st.expander(f"Recommendations for {row['District']}"):
            st.write(f"**Current Status:**")
            st.write(f"- Student-Teacher Ratio: {row['STR_2020']:.1f}")
            st.write(f"- Performance Score: {row['Performance_Score']:.1f}%")
            st.write(f"- Resource Need Index: {row['Resource_Need_Index']:.2f}")
            
            st.write(f"**Recommended Actions:**")
            if row['STR_2020'] > df['STR_2020'].mean():
                st.write("- Prioritize allocation of additional teachers to reduce STR")
            if row['Performance_Score'] < df['Performance_Score'].mean():
                st.write("- Implement academic intervention programs")
                st.write("- Provide teacher training focused on improving student outcomes")
            
            st.write("- Monitor progress quarterly and adjust strategies as needed")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Data Source:** Sri Lanka Education Ministry
    \n**Note:** This analysis focuses on government schools across districts.
    Student-Teacher Ratio (STR) is calculated as Total Students / Total Teachers.
    """
)

# Add some custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)
