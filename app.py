#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install streamlit ngrok')


# In[4]:


get_ipython().system('pip install pyngrok')


# In[5]:


get_ipython().run_cell_magic('writefile', 'app.py', 'import streamlit as st\nimport numpy as np\nimport geojson\nimport pandas as pd\n\n# Function to create a circle polygon (approximated) in GeoJSON format\ndef create_circle_geojson(center_lat, center_lon, radius, num_points=64):\n    earth_radius = 6378137\n    angular_distance = radius / earth_radius\n    points = []\n    for angle in np.linspace(0, 2 * np.pi, num_points):\n        point_lat = np.arcsin(\n            np.sin(np.radians(center_lat)) * np.cos(angular_distance) +\n            np.cos(np.radians(center_lat)) * np.sin(angular_distance) * np.cos(angle)\n        )\n        point_lon = np.radians(center_lon) + np.arctan2(\n            np.sin(angle) * np.sin(angular_distance) * np.cos(np.radians(center_lat)),\n            np.cos(angular_distance) - np.sin(np.radians(center_lat)) * np.sin(point_lat)\n        )\n        points.append((np.degrees(point_lon), np.degrees(point_lat)))\n    points.append(points[0])\n    polygon = geojson.Polygon([points])\n    return polygon\n\n# Function to generate combined GeoJSON from a DataFrame\ndef generate_combined_geojson(df, radius):\n    features = []\n    for _, row in df.iterrows():\n        try:\n            # Check for missing or NaN values in latitude/longitude\n            if pd.isna(row[\'Latitude\']) or pd.isna(row[\'Longitude\']):\n                st.warning(f"Skipping row with missing coordinates: {row}")\n                continue\n\n            # Convert latitude and longitude to float and validate their ranges\n            center_lat = float(row[\'Latitude\'])\n            center_lon = float(row[\'Longitude\'])\n            \n            if not (-90 <= center_lat <= 90 and -180 <= center_lon <= 180):\n                st.warning(f"Skipping row with out-of-range coordinates: {row}")\n                continue\n\n            # Generate circle GeoJSON\n            circle_geojson = create_circle_geojson(center_lat, center_lon, radius)\n            features.append(geojson.Feature(geometry=circle_geojson, properties={"Latitude": center_lat, "Longitude": center_lon}))\n        except ValueError:\n            st.warning(f"Skipping row with invalid data: {row}")\n    return geojson.FeatureCollection(features)\n\n# Streamlit Interface\nst.title("CSV to GeoJSON Circle Generator")\n\n# Upload CSV\nuploaded_file = st.file_uploader("Upload a CSV file with \'Latitude\' and \'Longitude\' columns", type="csv")\n\n# Input for radius in meters\nradius = st.number_input("Enter radius for circles (in meters)", min_value=1, value=25000)\n\nif uploaded_file:\n    df = pd.read_csv(uploaded_file)\n    if \'Latitude\' in df.columns and \'Longitude\' in df.columns:\n        geojson_data = generate_combined_geojson(df, radius)\n        geojson_str = geojson.dumps(geojson_data, indent=2)\n\n        st.header("Generated GeoJSON")\n        st.text_area("GeoJSON Output", geojson_str, height=300)\n        \n        st.download_button(\n            label="Download GeoJSON",\n            data=geojson_str,\n            file_name="circles.geojson",\n            mime="application/json"\n        )\n    else:\n        st.error("CSV must contain \'Latitude\' and \'Longitude\' columns.")\n')


# In[6]:


get_ipython().system('ngrok config add-authtoken 2oTQlOql8oyegJVQsexeFjtaO9c_3rUigWYQFZ1DMhwEmAUoq')


# In[ ]:


get_ipython().system('streamlit run app.py --server.port 8503')


# In[ ]:


from pyngrok import ngrok
public_url = ngrok.connect(8503)
print("Streamlit app is running at:", public_url)


# In[ ]:




