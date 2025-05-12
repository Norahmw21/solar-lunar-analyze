import pandas as pd
import numpy as np
from datetime import datetime
import geopandas as gpd

def load_solar_data():
    df = pd.read_csv('solar.csv')

    # Clean Eclipse Types
    df['Eclipse Type'] = df['Eclipse Type'].replace({
        'P': 'Partial eclipse', 'A': 'Annular eclipse', 'T': 'Total eclipse', 'H': 'Hybrid eclipse',
        'Pb': 'Partial eclipse', 'Pe': 'Partial eclipse', 'Am': 'Annular eclipse',
        'Tm': 'Total eclipse', 'An': 'Annular eclipse', 'A+': 'Annular eclipse',
        'A-': 'Annular eclipse', 'H3': 'Hybrid eclipse', 'As': 'Annular eclipse',
        'H2': 'Hybrid eclipse', 'Hm': 'Hybrid eclipse', 'T-': 'Total eclipse',
        'Tn': 'Total eclipse', 'Ts': 'Total eclipse', 'T+': 'Total eclipse'
    })

    # Rename columns for clarity
    df = df.rename(columns={
        'Catalog Number': 'Catalog-Number', 'Calendar Date': 'Calendar-Date',
        'Eclipse Time': 'Eclipse-Time', 'Delta T (s)': 'Delta-T(s)',
        'Lunation Number': 'Lunation-Number', 'Saros Number': 'Saros-Number',
        'Eclipse Type': 'Eclipse-Type', 'Gamma': 'Gamma',
        'Eclipse Magnitude': 'Eclipse-Magnitude', 'Latitude': 'Latitude',
        'Longitude': 'Longitude', 'Sun Altitude': 'Sun-Altitude',
        'Sun Azimuth': 'Sun-Azimuth', 'Path Width (km)': 'Path-Width(km)',
        'Central Duration': 'Central-Duration'
    })

    # Handle missing or invalid values
    df[['Path-Width(km)', 'Central-Duration']] = df[['Path-Width(km)', 'Central-Duration']].fillna("Not Applicable")
    df[['Path-Width(km)', 'Central-Duration']] = df[['Path-Width(km)', 'Central-Duration']].replace('-', 'Not Applicable')

    # Convert Central-Duration to time format
    mask = df['Central-Duration'] != 'Not Applicable'
    def convert_duration(duration_str):
        try:
            minutes = int(duration_str.split('m')[0])
            seconds = int(duration_str.split('m')[1].replace('s', ''))
            return f"{0:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "00:00:00"
    df.loc[mask, 'Central-Duration'] = df.loc[mask, 'Central-Duration'].apply(convert_duration)

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
