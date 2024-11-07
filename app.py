import streamlit as st
import numpy as np
import geojson
import pandas as pd
from pyngrok import ngrok

# Function to create a circle polygon (approximated) in GeoJSON format
def create_circle_geojson(center_lat, center_lon, radius, num_points=64):
    earth_radius = 6378137  # Earth radius in meters
    angular_distance = radius / earth_radius
    points = []
    for angle in np.linspace(0, 2 * np.pi, num_points):
        point_lat = np.arcsin(
            np.sin(np.radians(center_lat)) * np.cos(angular_distance) +
            np.cos(np.radians(center_lat)) * np.sin(angular_distance) * np.cos(angle)
        )
        point_lon = np.radians(center_lon) + np.arctan2(
            np.sin(angle) * np.sin(angular_distance) * np.cos(np.radians(center_lat)),
            np.cos(angular_distance) - np.sin(np.radians(center_lat)) * np.sin(point_lat)
        )
        points.append((np.degrees(point_lon), np.degrees(point_lat)))
    points.append(points[0])  # Closing the circle
    polygon = geojson.Polygon([points])
    return polygon

# Function to generate combined GeoJSON from a DataFrame
def generate_combined_geojson(df, radius):
    features = []
    for _, row in df.iterrows():
        try:
            # Check for missing or NaN values in latitude/longitude
            if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
                st.warning(f"Skipping row with missing coordinates: {row}")
                continue

            # Convert latitude and longitude to float and validate their ranges
            center_lat = float(row['Latitude'])
            center_lon = float(row['Longitude'])
            
            if not (-90 <= center_lat <= 90 and -180 <= center_lon <= 180):
                st.warning(f"Skipping row with out-of-range coordinates: {row}")
                continue

            # Generate circle GeoJSON
            circle_geojson = create_circle_geojson(center_lat, center_lon, radius)
            features.append(geojson.Feature(geometry=circle_geojson, properties={"Latitude": center_lat, "Longitude": center_lon}))
        except ValueError:
            st.warning(f"Skipping row with invalid data: {row}")
    return geojson.FeatureCollection(features)

# Streamlit Interface
st.title("CSV to GeoJSON Circle Generator")

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file with 'Latitude' and 'Longitude' columns", type="csv")

# Input for radius in meters
radius = st.number_input("Enter radius for circles (in meters)", min_value=1, value=25000)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        geojson_data = generate_combined_geojson(df, radius)
        geojson_str = geojson.dumps(geojson_data, indent=2)

        st.header("Generated GeoJSON")
        st.text_area("GeoJSON Output", geojson_str, height=300)
        
        st.download_button(
            label="Download GeoJSON",
            data=geojson_str,
            file_name="circles.geojson",
            mime="application/json"
        )
    else:
        st.error("CSV must contain 'Latitude' and 'Longitude' columns.")

# Start the Streamlit app and connect to ngrok
public_url = ngrok.connect(8503)
print(f"Streamlit app is running at: {public_url}")

# To run the Streamlit app manually, you can use the following in terminal:
# streamlit run app.py --server.port 8503






