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
        
        # Define all possible numeric columns
        possible_numeric_cols = [
            'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6', 
            'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11-1st', 
            'Grade 11 repeaters', 'Grade 12', 'Grade 13', 'Special education', 
            'Total', 'Total_Teachers', 'Male_Teachers', 'Female_Teachers',
            'Male_Percentage', 'Female_Percentage', 'STR_2015', 'STR_2020',
            'OL_Sat_2015', 'OL_Passed_2015', 'OL_Percent_2015', 'OL_Sat_2019',
            'OL_Passed_2019', 'OL_Percent_2019', 'AL_Sat_2015', 'AL_Eligible_2015',
            'AL_Percent_2015', 'AL_Sat_2020', 'AL_Eligible_2020', 'AL_Percent_2020'
        ]
        
        # Convert only columns that exist in the dataframe
        numeric_cols = [col for col in possible_numeric_cols if col in df.columns]
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate performance indicators if the required columns exist
        if 'OL_Percent_2019' in df.columns and 'AL_Percent_2020' in df.columns:
            df['Performance_Score'] = (df['OL_Percent_2019'] + df['AL_Percent_2020']) / 2
        
        if 'STR_2020' in df.columns and 'Performance_Score' in df.columns:
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

# Check for required columns
required_cols = ['District', 'Total', 'Total_Teachers']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Missing required columns: {', '.join(missing_cols)}")
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
        if 'STR_2020' in df.columns:
            st.metric("Average Student-Teacher Ratio (2020)", f"{df['STR_2020'].mean():.1f}")
        else:
            st.metric("Average Student-Teacher Ratio", "N/A")
    
    with col3:
        if 'OL_Percent_2019' in df.columns:
            st.metric("Average OL Pass Rate (2019)", f"{df['OL_Percent_2019'].mean():.1f}%")
        else:
            st.metric("Average OL Pass Rate", "N/A")
            
        if 'AL_Percent_2020' in df.columns:
            st.metric("Average AL Eligibility Rate (2020)", f"{df['AL_Percent_2020'].mean():.1f}%")
        else:
            st.metric("Average AL Eligibility Rate", "N/A")
    
    st.subheader("District Summary")
    
    # Select columns that actually exist
    display_cols = ['District', 'Total', 'Total_Teachers']
    if 'STR_2020' in df.columns:
        display_cols.append('STR_2020')
    if 'OL_Percent_2019' in df.columns:
        display_cols.append('OL_Percent_2019')
    if 'AL_Percent_2020' in df.columns:
        display_cols.append('AL_Percent_2020')
    
    st.dataframe(df[display_cols].sort_values('Total', ascending=False))

# Performance Analysis section
elif section == "Performance Analysis":
    st.header("Academic Performance Analysis")
    
    # Check if we have the required performance columns
    if 'OL_Percent_2019' not in df.columns or 'AL_Percent_2020' not in df.columns:
        st.warning("Performance data is not available in the dataset.")
        st.stop()
    
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
            if plotly_available and 'STR_2020' in df.columns:
                fig = px.scatter(df, x='STR_2020', y='OL_Percent_2019', 
                                size='Total', color='District',
                                title='OL Pass Rate vs Student-Teacher Ratio (2020)',
                                hover_data=['District', 'STR_2020', 'OL_Percent_2019'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'OL_Percent_2019', 'Total']])
        
        # Low performing districts
        low_perf_threshold = st.slider("Low performance threshold (%)", 40, 80, 60)
        low_perf_districts = df[df['OL_Percent_2019'] < low_perf_threshold]
        
        if not low_perf_districts.empty:
            st.subheader(f"Districts with OL Pass Rate Below {low_perf_threshold}%")
            low_perf_cols = ['District', 'OL_Percent_2019']
            if 'STR_2020' in df.columns:
                low_perf_cols.append('STR_2020')
            low_perf_cols.append('Total_Teachers')
            
            st.dataframe(low_perf_districts[low_perf_cols])
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
            if plotly_available and 'STR_2020' in df.columns:
                fig = px.scatter(df, x='STR_2020', y='AL_Percent_2020', 
                                size='Total', color='District',
                                title='AL Eligibility Rate vs Student-Teacher Ratio (2020)',
                                hover_data=['District', 'STR_2020', 'AL_Percent_2020'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'AL_Percent_2020', 'Total']])
        
        # Correlation analysis
        if 'STR_2020' in df.columns:
            corr_ol_str = df['OL_Percent_2019'].corr(df['STR_2020'])
            corr_al_str = df['AL_Percent_2020'].corr(df['STR_2020'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Correlation: OL Pass Rate vs STR", f"{corr_ol_str:.3f}")
            with col2:
                st.metric("Correlation: AL Eligibility Rate vs STR", f"{corr_al_str:.3f}")
    
    with tab3:
        st.subheader("Performance Trends Over Time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'OL_Percent_2015' in df.columns and 'OL_Percent_2019' in df.columns:
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
            else:
                st.warning("OL trend data is not available.")
        
        with col2:
            if 'AL_Percent_2015' in df.columns and 'AL_Percent_2020' in df.columns:
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
            else:
                st.warning("AL trend data is not available.")

# Resource Allocation section
elif section == "Resource Allocation":
    st.header("Resource Allocation Analysis")
    
    tab1, tab2 = st.tabs(["Teacher Distribution", "Resource Need Index"])
    
    with tab1:
        st.subheader("Teacher Distribution Across Districts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if plotly_available:
                fig = px.bar(df.sort_values('Total_Teachers', ascending=False), 
                            x='Total_Teachers', y='District', orientation='h',
                            title='Total Teachers by District',
                            color='Total_Teachers')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'Total_Teachers']].sort_values('Total_Teachers', ascending=False))
        
        with col2:
            if plotly_available and 'STR_2020' in df.columns:
                fig = px.bar(df.sort_values('STR_2020', ascending=False), 
                            x='STR_2020', y='District', orientation='h',
                            title='Student-Teacher Ratio by District (2020)',
                            color='STR_2020', color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df[['District', 'STR_2020']].sort_values('STR_2020', ascending=False))
        
        # High STR districts
        if 'STR_2020' in df.columns:
            high_str_threshold = st.slider("High STR threshold", 15, 35, 25)
            high_str_districts = df[df['STR_2020'] > high_str_threshold]
            
            if not high_str_districts.empty:
                st.subheader(f"Districts with STR Above {high_str_threshold}")
                st.dataframe(high_str_districts[['District', 'STR_2020', 'Total', 'Total_Teachers']])
            else:
                st.info(f"No districts with STR above {high_str_threshold}")
    
    with tab2:
        st.subheader("Resource Need Index")
        
        if 'Resource_Need_Index' not in df.columns:
            st.warning("Resource Need Index could not be calculated. Required data is missing.")
        else:
            st.markdown("""
            **Resource Need Index** is calculated as: STR_2020 × (100 - Performance_Score) / 100
            \nHigher values indicate districts that may need more resources (teachers) due to high STR and low performance.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if plotly_available:
                    fig = px.bar(df.sort_values('Resource_Need_Index', ascending=False), 
                                x='Resource_Need_Index', y='District', orientation='h',
                                title='Resource Need Index by District',
                                color='Resource_Need_Index')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(df[['District', 'Resource_Need_Index']].sort_values('Resource_Need_Index', ascending=False))
            
            with col2:
                if plotly_available:
                    fig = px.scatter(df, x='STR_2020', y='Performance_Score', 
                                    size='Total', color='Resource_Need_Index',
                                    title='Performance vs STR (Size = Total Students)',
                                    hover_data=['District', 'STR_2020', 'Performance_Score', 'Resource_Need_Index'])
                    st.plotly_chart(fig, use_container_width=True)
            
            # High need districts
            high_need_threshold = st.slider("High need threshold", 
                                          min_value=float(df['Resource_Need_Index'].min()), 
                                          max_value=float(df['Resource_Need_Index'].max()),
                                          value=float(df['Resource_Need_Index'].quantile(0.75)))
            
            high_need_districts = df[df['Resource_Need_Index'] > high_need_threshold]
            
            if not high_need_districts.empty:
                st.subheader(f"Districts with High Resource Need (Index > {high_need_threshold:.1f})")
                st.dataframe(high_need_districts[['District', 'Resource_Need_Index', 'STR_2020', 'Performance_Score']])
            else:
                st.info(f"No districts with Resource Need Index above {high_need_threshold:.1f}")

# District Comparison section
elif section == "District Comparison":
    st.header("District Comparison")
    
    # Select districts to compare
    districts = st.multiselect("Select districts to compare", df['District'].unique(), default=df['District'].unique()[:3])
    
    if not districts:
        st.warning("Please select at least one district.")
    else:
        comparison_df = df[df['District'].isin(districts)]
        
        # Select metrics to compare
        metrics = st.multiselect("Select metrics to compare", 
                                ['Total', 'Total_Teachers', 'STR_2020', 'OL_Percent_2019', 'AL_Percent_2020', 'Performance_Score'],
                                default=['Total', 'STR_2020', 'Performance_Score'])
        
        if not metrics:
            st.warning("Please select at least one metric.")
        else:
            # Create comparison table
            st.subheader("Comparison Table")
            st.dataframe(comparison_df[['District'] + metrics].set_index('District').T)
            
            # Create radar chart for comparison if Plotly is available
            if plotly_available and len(metrics) > 1:
                st.subheader("Radar Chart Comparison")
                
                # Normalize data for radar chart
                normalized_df = comparison_df[['District'] + metrics].copy()
                for metric in metrics:
                    if metric in normalized_df.columns:
                        max_val = normalized_df[metric].max()
                        min_val = normalized_df[metric].min()
                        if max_val != min_val:  # Avoid division by zero
                            normalized_df[metric] = (normalized_df[metric] - min_val) / (max_val - min_val)
                
                fig = go.Figure()
                
                for _, row in normalized_df.iterrows():
                    fig.add_trace(go.Scatterpolar(
                        r=[row[metric] for metric in metrics],
                        theta=metrics,
                        fill='toself',
                        name=row['District']
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )),
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)

# Insights & Recommendations section
elif section == "Insights & Recommendations":
    st.header("Insights & Recommendations")
    
    # Calculate key insights
    if 'Performance_Score' in df.columns and 'STR_2020' in df.columns:
        # Top performing districts
        top_performers = df.nlargest(3, 'Performance_Score')[['District', 'Performance_Score', 'STR_2020']]
        
        # Lowest performing districts
        low_performers = df.nsmallest(3, 'Performance_Score')[['District', 'Performance_Score', 'STR_2020']]
        
        # Highest STR districts
        high_str = df.nlargest(3, 'STR_2020')[['District', 'STR_2020', 'Performance_Score']]
        
        # Correlation between STR and performance
        corr = df['STR_2020'].corr(df['Performance_Score'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Performing Districts")
            for i, (_, row) in enumerate(top_performers.iterrows(), 1):
                st.write(f"{i}. **{row['District']}** (Score: {row['Performance_Score']:.1f}, STR: {row['STR_2020']:.1f})")
            
            st.subheader("Highest Student-Teacher Ratios")
            for i, (_, row) in enumerate(high_str.iterrows(), 1):
                st.write(f"{i}. **{row['District']}** (STR: {row['STR_2020']:.1f}, Score: {row['Performance_Score']:.1f})")
        
        with col2:
            st.subheader("Lowest Performing Districts")
            for i, (_, row) in enumerate(low_performers.iterrows(), 1):
                st.write(f"{i}. **{row['District']}** (Score: {row['Performance_Score']:.1f}, STR: {row['STR_2020']:.1f})")
            
            st.metric("Correlation between STR and Performance", f"{corr:.3f}")
            if corr < -0.3:
                st.info("Strong negative correlation: Higher STR tends to associate with lower performance")
            elif corr > 0.3:
                st.warning("Strong positive correlation: Higher STR tends to associate with higher performance")
            else:
                st.info("Weak correlation: No strong relationship between STR and performance")
    
    # Recommendations
    st.subheader("Recommendations")
    
    st.markdown("""
    1. **Resource Allocation**: Prioritize districts with high Resource Need Index for additional teachers and resources
    2. **Performance Improvement**: Implement targeted programs in low-performing districts
    3. **Best Practices Sharing**: Encourage knowledge transfer from high-performing to low-performing districts
    4. **Monitoring**: Track performance trends over time to evaluate intervention effectiveness
    5. **Infrastructure Investment**: Consider additional classrooms and facilities in high-STR districts
    """)
    
    # Export functionality
    if st.button("Generate Summary Report"):
        # Create a simple text report
        report = f"""
        EDUCATION PERFORMANCE DASHBOARD - SUMMARY REPORT
        Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}
        
        Total Districts: {len(df)}
        Total Students: {df['Total'].sum():,}
        Total Teachers: {df['Total_Teachers'].sum():,}
        
        Average Performance Score: {df['Performance_Score'].mean():.1f}%
        Average Student-Teacher Ratio: {df['STR_2020'].mean():.1f}
        
        Top 3 Performing Districts:
        {top_performers.to_string(index=False)}
        
        Bottom 3 Performing Districts:
        {low_performers.to_string(index=False)}
        
        Districts with Highest STR:
        {high_str.to_string(index=False)}
        """
        
        st.download_button(
            label="Download Report",
            data=report,
            file_name="education_performance_report.txt",
            mime="text/plain"
        )

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Data Source:** Sri Lanka Education Ministry
    \n**Note:** This analysis focuses on government schools across districts.
    Student-Teacher Ratio (STR) is calculated as Total Students / Total Teachers.
    """
)
