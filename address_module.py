from flask import Blueprint, render_template, request
import spacy
import re

# Load spaCy's English language model
nlp = spacy.load('en_core_web_sm')

# Define Blueprint for the submodule
address_bp = Blueprint('address_bp', __name__)

# Function to extract address components using spaCy
def extract_address_components(address):
    doc = nlp(address)
    components = {
        'Door No.': '',
        'Office or House': '',
        'Street or Landmark': '',
        'City': '',
        'District': '',
        'Pincode': ''
    }
    
    for ent in doc.ents:
        if ent.label_ == "CARDINAL":
            components['Door No.'] = ent.text
        elif ent.label_ == "GPE":
            if not components['City']:
                components['City'] = ent.text
            elif not components['District']:
                components['District'] = ent.text
        elif ent.label_ == "LOC":
            if not components['Street or Landmark']:
                components['Street or Landmark'] = ent.text
        elif ent.label_ == "ORG":
            components['Office or House'] = ent.text
        elif ent.label_ == "FAC":
            if not components['Office or House']:
                components['Office or House'] = ent.text

    pincode_match = re.search(r'\b\d{6}\b', address)
    if pincode_match:
        components['Pincode'] = pincode_match.group(0)

    return components


# Route for handling map retrieval (on clicking "Find")
@address_bp.route('/get_map', methods=['POST'])
def get_map():
    address = request.form['address']
    map_url = f"https://maps.google.com/?q={address.replace(' ', '+')}&output=embed"  # Example placeholder
    return render_template('index.html', map=map_url)

# Route for handling address arrangement using NLP (on clicking "Arrange")
@address_bp.route('/arrange_address', methods=['POST'])
def arrange_address():
    address = request.form['address']
    arranged_address = extract_address_components(address)
    return render_template('index.html', arranged_address=arranged_address)
