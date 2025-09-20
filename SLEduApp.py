import streamlit as st
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, avg
import plotly.express as px

# Initialize Spark
spark = SparkSession.builder.appName("SL_Education_Analysis").getOrCreate()

@st.cache_data
def load_data(file_path):
    df = spark.read.option("header", True).csv(file_path)
    numeric_cols = [c for c in df.columns if c not in ['District', 'Sex', 'Gender']]
    for col_name in numeric_cols:
        df = df.withColumn(col_name, regexp_replace(col(col_name), ",", "").cast("float"))
    return df

# Analysis functions
def calculate_correlations(df, col1, col2):
    return df.stat.corr(col1, col2)

def identify_low_performance_districts(df, pass_col="OL_Percent_2019", threshold=None):
    if threshold is None:
        threshold = df.select(avg(pass_col)).collect()[0][0]
    low_perf_df = df.filter(col(pass_col) < threshold).select("District", pass_col).toPandas()
    return low_perf_df, threshold

def enrollment_teacher_summary(df):
    summary = df.select(
        "District",
        col("Total").alias("Total_Enrollment"),
        col("Total_Teachers"),
        col("STR_2020")
    ).toPandas()
    return summary

# Visualization functions
def plot_str_vs_pass(df_pandas):
    fig = px.scatter(df_pandas, x="STR_2020", y="OL_Percent_2019",
                     hover_name="District",
                     title="Student Teacher Ratio vs OL Pass Percentage (2019)",
                     labels={"STR_2020": "Student Teacher Ratio (2020)",
                             "OL_Percent_2019": "OL Pass Percentage (2019)"})
    return fig

def plot_enrollment_bar(df_pandas):
    fig = px.bar(df_pandas.sort_values("Total_Enrollment", ascending=False),
                 x="District", y="Total_Enrollment",
                 title="Enrollment by District",
                 labels={"Total_Enrollment": "Total Enrollment"})
    return fig

# Main app starts here
st.title("Sri Lanka Education Dashboard")

data_path = "data/merged_dataset.csv"
df = load_data(data_path)

# Sidebar filters
districts = [row['District'] for row in df.select("District").distinct().collect()]
selected_district = st.sidebar.selectbox("Select District", ["All"] + districts)

# Show correlations
corr_str_pass = calculate_correlations(df, "STR_2020", "OL_Percent_2019")
st.write(f"**Correlation between Student-Teacher Ratio (2020) and OL Pass % (2019):** {corr_str_pass:.2f}")

# Identify low performing districts
low_perf_df, threshold = identify_low_performance_districts(df)
st.subheader(f"Districts with OL Pass % below average ({threshold:.2f}%)")
st.dataframe(low_perf_df)

# Enrollment summary
summary_df = enrollment_teacher_summary(df)

# Filter summary if district selected
if selected_district != "All":
    summary_df = summary_df[summary_df["District"] == selected_district]

st.subheader("Enrollment and Teacher Summary")
st.dataframe(summary_df)

# Plot enrollment bar (all districts)
if selected_district == "All":
    st.plotly_chart(plot_enrollment_bar(summary_df))

# Plot STR vs OL Pass % scatter plot
st.plotly_chart(plot_str_vs_pass(df.toPandas()))
