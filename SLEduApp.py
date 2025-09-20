import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("sri_lanka_education.csv")
    # Clean columns: remove commas if any, convert to numeric
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float, errors='ignore')
    return df

df = load_data()

st.title("Sri Lanka Education Analysis: Teacher Availability & Academic Performance")

# Sidebar filters
districts = df['District'].unique()
selected_district = st.sidebar.selectbox("Select District", districts)

# Filter data for selected district
district_data = df[df['District'] == selected_district].iloc[0]

# Enrollment visualization
st.header(f"Overview: {selected_district}")

grades = [f'Grade {i}' for i in range(1, 14)] + ['Grade 11-1st', 'Grade 11 repeaters', 'Special education']
enrollment = district_data[grades]

st.write("### Enrollment by Grade")
st.bar_chart(enrollment)

# Teacher availability
st.write("### Teacher Availability")
st.write(f"Total Teachers: {int(district_data['Total_Teachers'])}")
st.write(f"Male Teachers: {int(district_data['Male_Teachers'])} ({district_data['Male_Percentage']:.1f}%)")
st.write(f"Female Teachers: {int(district_data['Female_Teachers'])} ({district_data['Female_Percentage']:.1f}%)")

# STR
st.write("### Student-Teacher Ratio")
st.write(f"2015: {district_data['STR_2015']}")
st.write(f"2020: {district_data['STR_2020']}")

# OL results
st.write("### Academic Performance: Ordinary Level (OL)")
st.write(f"2015 OL Pass Percentage: {district_data['OL_Percent_2015']}% (Sat: {int(district_data['OL_Sat_2015'])}, Passed: {int(district_data['OL_Passed_2015'])})")
st.write(f"2019 OL Pass Percentage: {district_data['OL_Percent_2019']}% (Sat: {int(district_data['OL_Sat_2019'])}, Passed: {int(district_data['OL_Passed_2019'])})")

# AL results
st.write("### Academic Performance: Advanced Level (AL)")
st.write(f"2015 AL Pass Percentage: {district_data['AL_Percent_2015']}% (Sat: {int(district_data['AL_Sat_2015'])}, Eligible: {int(district_data['AL_Eligible_2015'])})")
st.write(f"2020 AL Pass Percentage: {district_data['AL_Percent_2020']}% (Sat: {int(district_data['AL_Sat_2020'])}, Eligible: {int(district_data['AL_Eligible_2020'])})")

# Correlations plots
st.header("Correlation between Student-Teacher Ratio and Academic Performance")

fig, ax = plt.subplots()
sns.scatterplot(data=df, x='STR_2020', y='OL_Percent_2019', ax=ax)
ax.set_xlabel("Student-Teacher Ratio 2020")
ax.set_ylabel("OL Pass Percentage 2019")
ax.set_title("OL Pass % vs STR (2020)")
st.pyplot(fig)

fig2, ax2 = plt.subplots()
sns.scatterplot(data=df, x='STR_2020', y='AL_Percent_2020', ax=ax2)
ax2.set_xlabel("Student-Teacher Ratio 2020")
ax2.set_ylabel("AL Pass Percentage 2020")
ax2.set_title("AL Pass % vs STR (2020)")
st.pyplot(fig2)

# Highlight problematic districts
st.header("Districts with High STR & Low Academic Performance")

threshold_str = st.sidebar.slider("Max Acceptable STR", min_value=10.0, max_value=40.0, value=25.0)
threshold_pass = st.sidebar.slider("Minimum Pass Rate (%)", min_value=30, max_value=100, value=70)

problematic = df[(df['STR_2020'] > threshold_str) & ((df['OL_Percent_2019'] < threshold_pass) | (df['AL_Percent_2020'] < threshold_pass))]

st.dataframe(problematic[['District', 'STR_2020', 'OL_Percent_2019', 'AL_Percent_2020']])

st.write("""
### Recommendations:
- Allocate more teachers to districts with high STR and low pass rates.
- Investigate underlying causes of low teacher availability or high student enrollment.
- Monitor gender distribution of teachers to support diversity.
- Plan resource allocation based on enrollment trends.
""")
