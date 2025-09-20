import streamlit as st
from pyspark.sql import SparkSession

# Initialize Spark session
@st.cache_resource
def init_spark():
    spark = SparkSession.builder \
        .appName("Streamlit PySpark Test") \
        .getOrCreate()
    return spark

spark = init_spark()

st.title("PySpark Analysis in Streamlit")

# Load CSV from local repo path (adjust path as needed)
csv_path = "data/merged_dataset.csv"  # put your csv file here in the repo under data/

try:
    df = spark.read.option("header", True).csv(csv_path)
    st.write("Data loaded successfully:")
    st.write(df.limit(5).toPandas())  # Show sample in Streamlit

    # Simple aggregation example: count rows by a column (adjust column name)
    agg_col = df.columns[0]  # just use first column for demo
    agg_df = df.groupBy(agg_col).count()

    st.write(f"Aggregation by '{agg_col}':")
    st.write(agg_df.toPandas())

except Exception as e:
    st.error(f"Error loading or processing data: {e}")
