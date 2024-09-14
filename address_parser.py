from flask import Flask, request, render_template
import googlemaps

app = Flask(__name__)

# Initialize Google Maps client
gmaps = googlemaps.Client(key='AIzaSyBMQPryqr_OhPX4lUtLBjB4YADGKJtUXkA')  # Replace with your actual API key

def parse_address(address):
    # Geocode the address
    geocode_result = gmaps.geocode(address)
    
    if not geocode_result:
        return "Address not found"

    # Extract the components
    components = geocode_result[0]['address_components']

    address_parts = {
        'Flat No.': '',
        'Floor': '',
        'Building Number': '',
        'Street': '',
        'City': '',
        'State': '',
        'Pincode': ''
    }

    for component in components:
        if 'street_number' in component['types']:
            address_parts['Building Number'] = component['long_name']
        elif 'route' in component['types']:
            address_parts['Street'] = component['long_name']
        elif 'locality' in component['types']:
            address_parts['City'] = component['long_name']
        elif 'administrative_area_level_1' in component['types']:
            address_parts['State'] = component['long_name']
        elif 'postal_code' in component['types']:
            address_parts['Pincode'] = component['long_name']

    return address_parts

@app.route('/', methods=['GET', 'POST'])
def index():
    parsed_address = None
    if request.method == 'POST':
        address = request.form['address']
        parsed_address = parse_address(address)
    
    return render_template('index.html', parsed_address=parsed_address)

if __name__ == '__main__':
    app.run(debug=True)
