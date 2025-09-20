import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_option('deprecation.showPyplotGlobalUse', False)

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/piumixit/BigDataAssignment/main/data/merged_dataset.csv"
    df = pd.read_csv(url)
    # Clean columns if needed, remove commas in numeric columns, convert to numeric
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace(',', '').replace('NULL', '').fillna('0')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

st.title("Sri Lanka Education Performance Dashboard")
st.markdown("""
Improving student academic performance and resource allocation in government schools by analyzing enrollment, teacher availability, and exam results across districts.
""")

# Sidebar filters
districts = df['District'].unique()
selected_district = st.sidebar.selectbox("Select District", districts)
selected_data = df[df['District'] == selected_district]

# Show district summary
st.header(f"Summary for {selected_district}")
total_students = selected_data['Total'].values[0]
total_teachers = selected_data['Total_Teachers'].values[0]
str_2020 = selected_data['STR_2020'].values[0]
ol_pass_percent_2019 = selected_data['OL_Percent_2019'].values[0]

st.markdown(f"""
- Total Students: **{total_students:,}**
- Total Teachers: **{total_teachers:,}**
- Student-Teacher Ratio (2020): **{str_2020}**
- O-Level Pass Percentage (2019): **{ol_pass_percent_2019}%**
""")

# Visualize enrollment trends across grades
grades = ['Grade 1','Grade 2','Grade 3','Grade 4','Grade 5','Grade 6','Grade 7','Grade 8','Grade 9','Grade 10','Grade 11-1st','Grade 11 repeaters','Grade 12','Grade 13']

st.subheader("Enrollment by Grade")
enrollment = selected_data[grades].iloc[0]
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=grades, y=enrollment, ax=ax)
plt.xticks(rotation=45)
plt.ylabel('Number of Students')
st.pyplot(fig)

# Correlation heatmap for entire dataset (interactive)
st.header("Correlation Analysis (All Districts)")
numeric_cols = ['Total', 'Total_Teachers', 'STR_2020', 'OL_Percent_2019', 'OL_Percent_2015', 'AL_Percent_2015', 'AL_Percent_2020']
corr = df[numeric_cols].corr()

fig2, ax2 = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax2)
st.pyplot(fig2)

st.markdown("""
### Insights:
- Check positive/negative correlations between student-teacher ratio and exam performance.
- Identify districts with low pass percentages and high STR to optimize resource allocation.
""")

# Identify districts with low performance and high STR
st.header("Districts Needing Attention")

low_performance = df[(df['OL_Percent_2019'] < 60) & (df['STR_2020'] > 20)][['District','OL_Percent_2019','STR_2020']]
st.dataframe(low_performance)

st.markdown("""
Districts with **O-Level pass percentage below 60%** and **Student-Teacher Ratio above 20** are potential focus areas for resource reallocation.
""")

# Suggestion box
st.header("Recommendations")

if not low_performance.empty:
    st.write("""
    - Allocate more teachers to districts with high student-teacher ratios and low pass rates.
    - Monitor enrollment trends to predict future staffing needs.
    - Invest in targeted academic interventions in low performing districts.
    """)
else:
    st.write("No critical districts identified based on current criteria.")

