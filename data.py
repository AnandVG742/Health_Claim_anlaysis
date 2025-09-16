import pandas as pd
import streamlit as st

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("enhanced_health_insurance_claims.csv")
    df["ClaimDate"] = pd.to_datetime(df["ClaimDate"], errors="coerce")
    return df

df = load_data()

# ---------------- Sidebar Filters ----------------
st.sidebar.header("Filters")

# Claim Status
status_filter = st.sidebar.multiselect(
    "Select Claim Status", options=df["ClaimStatus"].unique(), default=df["ClaimStatus"].unique()
)

# Claim Type
type_filter = st.sidebar.multiselect(
    "Select Claim Type", options=df["ClaimType"].unique(), default=df["ClaimType"].unique()
)

# Provider Specialty
specialty_filter = st.sidebar.multiselect(
    "Select Provider Specialty", options=df["ProviderSpecialty"].unique(), default=df["ProviderSpecialty"].unique()
)

# Date Range
min_date, max_date = df["ClaimDate"].min(), df["ClaimDate"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Age Range
age_min, age_max = int(df["PatientAge"].min()), int(df["PatientAge"].max())
age_range = st.sidebar.slider("Select Age Range", age_min, age_max, (age_min, age_max))

# ---------------- Apply Filters ----------------
df_filtered = df[
    (df["ClaimStatus"].isin(status_filter)) &
    (df["ClaimType"].isin(type_filter)) &
    (df["ProviderSpecialty"].isin(specialty_filter)) &
    (df["ClaimDate"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))) &
    (df["PatientAge"].between(age_range[0], age_range[1]))
]

# ---------------- KPIs ----------------
st.title("📊 Health Insurance Claims Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Claims", len(df_filtered))
with col2:
    st.metric("Total Claim Amount", f"${df_filtered['ClaimAmount'].sum():,.2f}")
with col3:
    st.metric("Avg Claim Amount", f"${df_filtered['ClaimAmount'].mean():,.2f}")

col4, col5 = st.columns(2)
with col4:
    approval_rate = (df_filtered["ClaimStatus"].eq("Approved").mean()) * 100
    st.metric("Approval Rate", f"{approval_rate:.1f}%")
with col5:
    st.metric("Unique Patients / Providers", f"{df_filtered['PatientID'].nunique()} / {df_filtered['ProviderID'].nunique()}")

# ---------------- Charts ----------------
st.header("Claims Analysis")

# Claims by Status
st.subheader("Claims by Status")
st.bar_chart(df_filtered["ClaimStatus"].value_counts())

# Claims by Type
st.subheader("Claims by Type")
st.bar_chart(df_filtered["ClaimType"].value_counts())

# Claims by Provider Specialty
st.subheader("Top 10 Provider Specialties")
specialty_counts = df_filtered["ProviderSpecialty"].value_counts().head(10)
st.bar_chart(specialty_counts)

# Claims Trend Over Time
st.subheader("Claims Trend Over Time")
claims_over_time = df_filtered.groupby(df_filtered["ClaimDate"].dt.to_period("M")).size()
claims_over_time.index = claims_over_time.index.to_timestamp()
st.line_chart(claims_over_time)

# Claims by Age Group
st.subheader("Claims by Age Group")
st.histogram = st.bar_chart(df_filtered["PatientAge"].value_counts().sort_index())
