# Resource Allocation section
elif section == "Resource Allocation":
    st.header("Resource Allocation Analysis")
    
    st.subheader("Student-Teacher Ratio (STR) Distribution")
    if plotly_available:
        fig = px.histogram(df, x='STR_2020', nbins=20, 
                           title='Distribution of Student-Teacher Ratio (2020)', 
                           labels={'STR_2020': 'Student-Teacher Ratio (2020)'},
                           color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig, use_container_width=True)
    elif matplotlib_available:
        fig, ax = plt.subplots()
        sns.histplot(df['STR_2020'].dropna(), bins=20, ax=ax, color='blue')
        ax.set_title('Distribution of Student-Teacher Ratio (2020)')
        ax.set_xlabel('Student-Teacher Ratio (2020)')
        ax.set_ylabel('Count')
        st.pyplot(fig)
    else:
        st.write(df[['District', 'STR_2020']].sort_values('STR_2020'))

    st.subheader("Teacher Gender Distribution")
    gender_data = df[['District', 'Male_Teachers', 'Female_Teachers']].set_index('District')
    gender_data = gender_data.fillna(0)
    
    if plotly_available:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Male Teachers', x=gender_data.index, y=gender_data['Male_Teachers']))
        fig.add_trace(go.Bar(name='Female Teachers', x=gender_data.index, y=gender_data['Female_Teachers']))
        fig.update_layout(barmode='stack', title='Teacher Gender Distribution by District',
                          xaxis_title='District', yaxis_title='Number of Teachers')
        st.plotly_chart(fig, use_container_width=True)
    elif matplotlib_available:
        fig, ax = plt.subplots(figsize=(10,6))
        gender_data.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title('Teacher Gender Distribution by District')
        ax.set_xlabel('District')
        ax.set_ylabel('Number of Teachers')
        st.pyplot(fig)
    else:
        st.dataframe(gender_data)

    st.subheader("Resource Need Index")
    sorted_resource_need = df.sort_values('Resource_Need_Index', ascending=False)[['District', 'Resource_Need_Index']]
    st.dataframe(sorted_resource_need)
    
    if plotly_available:
        fig = px.bar(sorted_resource_need, x='Resource_Need_Index', y='District', orientation='h',
                     title='Resource Need Index by District', color='Resource_Need_Index',
                     color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)

# District Comparison section
elif section == "District Comparison":
    st.header("District Comparison")

    districts = df['District'].unique()
    selected_districts = st.multiselect("Select districts to compare", districts, default=districts[:3])

    if selected_districts:
        comp_df = df[df['District'].isin(selected_districts)].set_index('District')

        st.subheader("Key Metrics Comparison")
        metrics = ['Total', 'Total_Teachers', 'STR_2020', 'OL_Percent_2019', 'AL_Percent_2020', 'Resource_Need_Index']
        comp_metrics = comp_df[metrics]

        st.dataframe(comp_metrics.style.format({
            'Total': '{:,.0f}',
            'Total_Teachers': '{:,.0f}',
            'STR_2020': '{:.1f}',
            'OL_Percent_2019': '{:.1f}%',
            'AL_Percent_2020': '{:.1f}%',
            'Resource_Need_Index': '{:.2f}'
        }))

        if plotly_available:
            st.subheader("Visual Comparison")
            fig = make_subplots(rows=2, cols=1, subplot_titles=("OL Pass Rate (2019)", "AL Eligibility Rate (2020)"))
            for district in selected_districts:
                fig.add_trace(go.Bar(name=district, x=['OL Pass Rate'], y=[comp_df.loc[district, 'OL_Percent_2019']]), row=1, col=1)
                fig.add_trace(go.Bar(name=district, x=['AL Eligibility Rate'], y=[comp_df.loc[district, 'AL_Percent_2020']]), row=2, col=1)
            fig.update_layout(barmode='group', height=600)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one district to compare.")

# Insights & Recommendations section
elif section == "Insights & Recommendations":
    st.header("Insights & Recommendations")

    st.markdown("### Data-Driven District Recommendations")

    # Define thresholds
    low_ol_threshold = 60  # OL pass rate below this is considered low
    high_str_threshold = 30  # STR above this is considered high
    gender_imbalance_threshold = 60  # % of one gender above which imbalance exists

    # Districts with low OL pass rate and high STR
    low_perf_high_str = df[(df['OL_Percent_2019'] < low_ol_threshold) & (df['STR_2020'] > high_str_threshold)]

    if not low_perf_high_str.empty:
        st.subheader("Districts Needing Urgent Academic & Resource Support")
        for _, row in low_perf_high_str.iterrows():
            st.markdown(
                f"**{row['District']}** has an OL pass rate of {row['OL_Percent_2019']:.1f}% "
                f"and a high student-teacher ratio of {row['STR_2020']:.1f}. "
                "It is recommended to increase teacher recruitment and implement targeted academic programs."
            )
    else:
        st.info("No districts found with both low OL pass rates and high student-teacher ratios.")

    # Districts with gender imbalance in teachers
    gender_imbalance = df[(df['Female_Percentage'] > gender_imbalance_threshold) | (df['Male_Percentage'] > gender_imbalance_threshold)]
    if not gender_imbalance.empty:
        st.subheader("Districts with Gender Imbalance in Teaching Staff")
        for _, row in gender_imbalance.iterrows():
            dominant_gender = "female" if row['Female_Percentage'] > gender_imbalance_threshold else "male"
            st.markdown(
                f"**{row['District']}** has {row['Female_Percentage']:.1f}% female teachers "
                f"and {row['Male_Percentage']:.1f}% male teachers, indicating a strong {dominant_gender} teacher dominance. "
                "Consider policies to promote balanced gender recruitment."
            )
    else:
        st.info("No significant gender imbalance detected in teaching staff across districts.")

    # Districts showing improvement in OL performance (2015 to 2019)
    df['OL_Improvement'] = df['OL_Percent_2019'] - df['OL_Percent_2015']
    improving_districts = df[df['OL_Improvement'] > 5].sort_values('OL_Improvement', ascending=False)
    if not improving_districts.empty:
        st.subheader("Districts Showing Significant OL Performance Improvement")
        for _, row in improving_districts.iterrows():
            st.markdown(
                f"**{row['District']}** improved OL pass rates by {row['OL_Improvement']:.1f}% "
                "from 2015 to 2019. Recommend continuing current support strategies."
            )
    else:
        st.info("No districts showed significant OL pass rate improvement from 2015 to 2019.")
    
    st.markdown("""
    ### Key Insights:
    - Districts with **high Student-Teacher Ratios (STR)** generally have lower pass rates in both OL and AL exams.
    - The **Resource Need Index** highlights districts where increased teacher allocation could improve student outcomes.
    - Some districts show improving trends in exam pass rates, indicating the success of recent interventions.
    - Gender distribution among teachers varies widely; promoting gender balance could enhance teaching environments.
    
    ### Recommendations:
    1. **Targeted Resource Allocation:** Prioritize districts with high Resource Need Index scores for teacher recruitment and training.
    2. **Monitor and Support Low Performing Districts:** Implement focused academic programs in districts below performance thresholds.
    3. **Encourage Gender Balance in Teaching Staff:** Support policies that promote female teacher recruitment where underrepresented.
    4. **Continuous Data Monitoring:** Maintain up-to-date data collection to track performance trends and resource allocation impact.
    
    ### Next Steps:
    - Engage with district education officers to validate findings and tailor interventions.
    - Expand dataset to include private schools and additional years for comprehensive analysis.
    - Incorporate qualitative feedback from teachers and students for holistic understanding.
    """)

    # Overall summary recommendations
    st.markdown("""
    ### Summary Recommendations
    - Prioritize teacher allocation and academic interventions in districts with both low performance and high STR.
    - Promote gender-balanced recruitment in districts with strong gender dominance among teachers.
    - Recognize and support districts with improving performance trends to sustain momentum.
    - Maintain continuous monitoring to track progress and adjust strategies accordingly.
    """)
