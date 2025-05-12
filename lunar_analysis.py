import pandas as pd
import numpy as np
from datetime import datetime
import geopandas as gpd

def load_lunar_data():
    df = pd.read_csv('lunar.csv')

        # Clean Eclipse Types
    
    df['Eclipse Type'] = df['Eclipse Type'].astype(str).str.strip().str.upper().str[0]
    df['Eclipse Type'] = df['Eclipse Type'].replace({
        'N':'Penumbral Eclipse',
        'P':'Partial Eclipse',
        'T':'Total Eclipse'
})

        # Rename columns for clarity
    df = df.rename(columns={
    'Catalog Number': 'Catalog-Number',
    'Calendar Date': 'Calendar-Date',
    'Eclipse Time': 'Eclipse-Time',
    'Delta T (s)': 'Delta-T(s)',
    'Lunation Number': 'Lunation-Number',
    'Saros Number': 'Saros-Number',
    'Eclipse Type': 'Eclipse-Type',
    'Quincena Solar Eclipse': 'Quincena-Solar-Eclipse',
    'Gamma': 'Gamma',
    'Penumbral Magnitude': 'Penumbral-Magnitude',
    'Umbral Magnitude': 'Umbral-Magnitude',
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'Penumbral Eclipse Duration (m)': 'Penumbral-Eclipse-Duration(m)',
    'Partial Eclipse Duration (m)': 'Partial-Eclipse-Duration(m)',
    'Total Eclipse Duration (m)': 'Total-Eclipse-Duration(m)'
})

        # Convert Penumbral, Partial, Total Eclipse Duration (in minutes) to time format
    columns = ["Penumbral-Eclipse-Duration(m)", "Partial-Eclipse-Duration(m)", "Total-Eclipse-Duration(m)"]

    def convert_minutes(duration_str):
        try:
            total_seconds = float(duration_str) * 60
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "00:00:00"

    for col in columns:
        mask = df[col] != 'Not Applicable'
        df.loc[mask, col] = df.loc[mask, col].apply(convert_minutes)

        # Handle Calendar Date to datetime
    df['Is_CE'] = ~df['Calendar-Date'].str.startswith('-')
    df['Calendar-Date-Clean'] = df['Calendar-Date'].str.strip().str.replace(r'\s+', ' ', regex=True).str.lstrip('-')
    def pad_year(date_str):
        parts = date_str.split(" ", 1)
        if len(parts) > 1 and len(parts[0]) < 4:
            parts[0] = parts[0].zfill(4)
        return " ".join(parts)
    df['Calendar-Date-Clean'] = df['Calendar-Date-Clean'].apply(pad_year)
    def safe_to_datetime(date_str, format='%Y %B %d'):
        try:
            return datetime.strptime(date_str, format)
        except:
            return None
    df['Calendar-Date-Parsed'] = df['Calendar-Date-Clean'].apply(safe_to_datetime)

        # Extract year from parsed date
    df['Year'] = df['Calendar-Date-Parsed'].apply(lambda x: x.year if pd.notnull(x) else None)

        # Convert coordinates to float
    def parse_coordinate(coord):
        try:
            value = float(coord[:-1])
            direction = coord[-1].upper()
            if direction in ('S', 'W'):
                value = -value
            return round(value, 6)
        except:
            return np.nan
    df['lat'] = df['Latitude'].apply(parse_coordinate)
    df['lon'] = df['Longitude'].apply(parse_coordinate)

        # Drop missing coordinates
    df = df.dropna(subset=['lat', 'lon'])

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lon'], df['lat']), crs='4326')
    return gdf