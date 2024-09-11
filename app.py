from flask import Flask, render_template, request, jsonify
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import requests
from geopy.distance import geodesic


app = Flask(__name__)

# Load and prepare the dataset
df = pd.read_csv('SKLM.csv')
df = df.dropna(subset=['Latitude', 'Longitude'])

# Ensure Latitude and Longitude are valid
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df = df[(df['Latitude'].between(-90, 90)) & (df['Longitude'].between(-180, 180))]

# Google Geocoding API
def geocode_address_google(address, api_key):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': api_key}
    response = requests.get(base_url, params=params)
    results = response.json()

    if results['status'] == 'OK':
        location = results['results'][0]['geometry']['location']
        lat, lng = location['lat'], location['lng']

        # Validate the lat/lon returned by the API
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return lat, lng
        else:
            return None, None
    else:
        return None, None

# Find nearest BO based on coordinates
def find_nearest_bo(lat, lon, df):
    nearest_bo = None
    min_distance = float('inf')

    for i, row in df[df['OfficeType'] == 'BO'].iterrows():
        bo_location = (row['Latitude'], row['Longitude'])
        distance = geodesic((lat, lon), bo_location).km

        if distance < min_distance:
            min_distance = distance
            nearest_bo = row

    return nearest_bo, min_distance

# Find PO with matching Pincode based on the coordinates
def find_po_by_pincode(pincode, df):
    po_row = df[(df['OfficeType'] == 'PO') & (df['Pincode'] == pincode)]
    return po_row

# Home route to render the form
@app.route('/')
def index():
    return render_template('index.html')

# API to handle form submission and process data
@app.route('/get_map', methods=['POST'])
def get_map():
    user_address = request.form['address']
    api_key = 'AIzaSyBMQPryqr_OhPX4lUtLBjB4YADGKJtUXkA'
    
    user_lat, user_lon = geocode_address_google(user_address, api_key)

    if user_lat is not None and user_lon is not None:
        map_center = [user_lat, user_lon]
        mymap = folium.Map(location=map_center, zoom_start=12)

        # Mark user's location
        folium.Marker(
            location=[user_lat, user_lon],
            popup="Your Location",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mymap)

        # Find nearest BO
        nearest_bo, distance_to_bo = find_nearest_bo(user_lat, user_lon, df)

        if nearest_bo is not None:
            folium.Marker(
                location=[nearest_bo['Latitude'], nearest_bo['Longitude']],
                popup=f"Nearest BO: {nearest_bo['OfficeName']} (Distance: {distance_to_bo:.2f} km)",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(mymap)

            # Find PO with the same Pincode as the nearest BO
            po_row = find_po_by_pincode(nearest_bo['Pincode'], df)
            
            if not po_row.empty:
                po = po_row.iloc[0]  # Take the first PO if there are multiple
                folium.Marker(
                    location=[po['Latitude'], po['Longitude']],
                    popup=f"PO for BO's Pincode: {po['OfficeName']} (Pincode: {po['Pincode']})",
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(mymap)

        # Save to HTML and return it as a response
        mymap.save('templates/map.html')
        return render_template('map.html')
    else:
        return jsonify({'error': 'Address not found or invalid coordinates.'}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
