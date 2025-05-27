import streamlit as st
import geopandas as gpd
import pandas as pd
from solar_analysis import load_solar_data
from lunar_analysis import load_lunar_data 

st.set_page_config(page_title="Eclipse Explorer", layout="wide")

st.title("🌘 Eclipse Explorer Dashboard")

st.sidebar.header("🔍 Filter Options")

eclipse_type = st.sidebar.radio("Choose Eclipse Type", ["Solar", "Lunar"])

@st.cache_data
def load_data(eclipse_type):
    if eclipse_type == "Solar":
        return load_solar_data()
    else:
        return load_lunar_data()

df = load_data(eclipse_type)

era = st.sidebar.selectbox("Select Era", ["CE", "BCE"])

# view all the data set year chosen lunar or solar then,  either by CE or BCE
view_all_years = st.sidebar.checkbox("Show All Years", value=False)

# option for the user for a specific year
if not view_all_years:
    year = st.sidebar.number_input("Select Year", min_value=-3000, max_value=3000, value=2000, step=1)

# Filter data
is_ce = era.upper() == 'CE'
if view_all_years:
    filtered_df = df[df['Year'].notna() & (df['Is_CE'] == is_ce)]
else:
    filtered_df = df[df['Year'].notna() & (df['Is_CE'] == is_ce) & (df['Year'] == year)]

# Display 
if filtered_df.empty:
    st.warning(f"No {eclipse_type.lower()} eclipse events found for the selected filter.")
else:
    if view_all_years:
        st.success(f"{len(filtered_df)} {eclipse_type.lower()} eclipse events found across all years in {era}.")
    else:
        st.success(f"{len(filtered_df)} {eclipse_type.lower()} eclipse events found for year {year} {era}.")

    st.map(filtered_df)

    # tabel info
    st.subheader("📄 Eclipse Data Table")
    if eclipse_type == "Solar":
        st.dataframe(filtered_df[[
            "Calendar-Date", "Eclipse-Type", "Eclipse-Magnitude", "Central-Duration",
            "Path-Width(km)", "Latitude", "Longitude", "Gamma"
        ]])
    else:  # Lunar
        st.dataframe(filtered_df[[
            "Calendar-Date", "Eclipse-Type", "Latitude", "Longitude", "Gamma",
            "Umbral-Magnitude", "Penumbral-Magnitude"
        ]])

    # Charts based on eclipse type
    if eclipse_type == "Solar":
        st.subheader("📊 Eclipse Type Distribution")
        eclipse_type_counts = filtered_df['Eclipse-Type'].value_counts()
        st.bar_chart(eclipse_type_counts)

        st.subheader("☀️ Eclipse Magnitude Distribution")
        st.line_chart(filtered_df[['Eclipse-Magnitude']].astype(float))

        st.subheader("🌐 Gamma Value Distribution")
        gamma_values = pd.to_numeric(filtered_df['Gamma'], errors='coerce').dropna()
        if not gamma_values.empty:
            st.line_chart(gamma_values)
        else:
            st.info("No valid Gamma data available.")

        st.subheader("📍 Path Width Distribution (if available)")
        valid_widths = pd.to_numeric(filtered_df['Path-Width(km)'], errors='coerce').dropna()
        if not valid_widths.empty:
            st.area_chart(valid_widths)
        else:
            st.info("No valid path width data available.")

    elif eclipse_type == "Lunar":
        st.subheader("📊 Eclipse Type Distribution")
        eclipse_type_counts = filtered_df['Eclipse-Type'].value_counts()
        st.bar_chart(eclipse_type_counts)

        st.subheader("🌑 Umbral Magnitude Distribution")
        umbral_magnitude = pd.to_numeric(filtered_df['Umbral-Magnitude'], errors='coerce').dropna()
        if not umbral_magnitude.empty:
            st.line_chart(umbral_magnitude)
        else:
            st.info("No valid Umbral Magnitude data available.")

        st.subheader("🌘 Penumbral Magnitude Distribution")
        penumbral_magnitude = pd.to_numeric(filtered_df['Penumbral-Magnitude'], errors='coerce').dropna()
        if not penumbral_magnitude.empty:
            st.area_chart(penumbral_magnitude)
        else:
            st.info("No valid Penumbral Magnitude data available.")

        st.subheader("🌐 Gamma Value Distribution")
        gamma_values = pd.to_numeric(filtered_df['Gamma'], errors='coerce').dropna()
        if not gamma_values.empty:
            st.line_chart(gamma_values)
        else:
            st.info("No valid Gamma data available.")
