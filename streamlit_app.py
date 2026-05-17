import streamlit as st
import pandas as pd
import os
import time
import requests
from datetime import datetime

# Automatically read the key from the native secrets framework securely
if "RAPIDAPI_KEY" in st.secrets:
    os.environ["RAPIDAPI_KEY"] = st.secrets["RAPIDAPI_KEY"]

st.set_page_config(page_title="APA CRM - Sales Portal", layout="wide", page_icon="💧")

DATA_FILE = "apa_crm_data.csv"

ALL_COLUMNS = [
    "Restaurant Name", "Company Name", "Cuisine/Type", "Zone/Area", "Address",
    "Latitude", "Longitude", "Map Link", "Website", "Google Rating",
    "Total Reviews", "Price Segment", "Restaurant Phone",
    "Primary Contact Name", "Primary Contact Role", "Primary Contact Phone", "Primary Contact Email",
    "Decision Maker Name", "Decision Maker Details", "Other Contact Name", "Other Contact Details",
    "Current Brand", "Bottle Type", "Acquisition Cost (Excl GST)", "Monthly Volume (Bottles)",
    "Proposed APA SKU", "Sample Delivery Date", "Agreed Margin %", "Credit Terms", "Competitor Contract Expiry",
    "Lead Source", "Salesperson Name", "Lead Status", "Last Contacted", "Interaction Summary", "Next Follow-up"
]

# FIX 6: Price level mapping from Google Places API
PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE":           "₹",
    "PRICE_LEVEL_INEXPENSIVE":    "₹",
    "PRICE_LEVEL_MODERATE":       "₹₹",
    "PRICE_LEVEL_EXPENSIVE":      "₹₹₹",
    "PRICE_LEVEL_VERY_EXPENSIVE": "₹₹₹₹",
}

# 🗺️ 15KM RADIUS MASTER GEOFENCES INDEX
NEIGHBORHOOD_CONFIG = {
    # --- HYDERABAD ---
    "Ameerpet": {"lat": 17.4375, "lng": 78.4482, "radius": 15000.0},
    "Begumpet": {"lat": 17.4447, "lng": 78.4664, "radius": 15000.0},
    "SR Nagar": {"lat": 17.4431, "lng": 78.4410, "radius": 15000.0},
    "Prakash Nagar": {"lat": 17.4442, "lng": 78.4740, "radius": 15000.0},
    "Punjagutta": {"lat": 17.4261, "lng": 78.4534, "radius": 15000.0},
    "Balkampet": {"lat": 17.4478, "lng": 78.4452, "radius": 15000.0},
    "Madhura Nagar": {"lat": 17.4395, "lng": 78.4350, "radius": 15000.0},
    "Rasoolpura": {"lat": 17.4491, "lng": 78.4836, "radius": 15000.0},
    "Sanathnagar": {"lat": 17.4566, "lng": 78.4312, "radius": 15000.0},
    "Bharat Nagar": {"lat": 17.4645, "lng": 78.4208, "radius": 15000.0},
    "Erragadda": {"lat": 17.4580, "lng": 78.4230, "radius": 15000.0},
    "Borabanda": {"lat": 17.4611, "lng": 78.3976, "radius": 15000.0},
    "Moti Nagar": {"lat": 17.4608, "lng": 78.4102, "radius": 15000.0},
    "Nehru Nagar": {"lat": 17.4495, "lng": 78.4582, "radius": 15000.0},
    "Khairatabad": {"lat": 17.4124, "lng": 78.4617, "radius": 15000.0},
    "Somajiguda": {"lat": 17.4251, "lng": 78.4595, "radius": 15000.0},
    "Raj Bhavan Road": {"lat": 17.4215, "lng": 78.4602, "radius": 15000.0},
    "Lakdikapool": {"lat": 17.4045, "lng": 78.4651, "radius": 15000.0},
    "Saifabad": {"lat": 17.4089, "lng": 78.4682, "radius": 15000.0},
    "A.C. Guards": {"lat": 17.4012, "lng": 78.4585, "radius": 15000.0},
    "Masab Tank": {"lat": 17.4018, "lng": 78.4522, "radius": 15000.0},
    "Chintal Basti": {"lat": 17.4105, "lng": 78.4542, "radius": 15000.0},
    "Musheerabad": {"lat": 17.4184, "lng": 78.4912, "radius": 15000.0},
    "Chikkadpally": {"lat": 17.4069, "lng": 78.4897, "radius": 15000.0},
    "Himayatnagar": {"lat": 17.3995, "lng": 78.4842, "radius": 15000.0},
    "Ashok Nagar": {"lat": 17.4102, "lng": 78.4862, "radius": 15000.0},
    "Domalguda": {"lat": 17.4022, "lng": 78.4805, "radius": 15000.0},
    "Hyderguda": {"lat": 17.3942, "lng": 78.4795, "radius": 15000.0},
    "Ramnagar": {"lat": 17.4208, "lng": 78.5028, "radius": 15000.0},
    "Azamabad": {"lat": 17.4162, "lng": 78.4975, "radius": 15000.0},
    "Adikmet": {"lat": 17.4144, "lng": 78.5140, "radius": 15000.0},
    "Nallakunta": {"lat": 17.3989, "lng": 78.5052, "radius": 15000.0},
    "Shanker Mutt": {"lat": 17.4008, "lng": 78.5012, "radius": 15000.0},
    "RTC X Roads": {"lat": 17.4084, "lng": 78.4939, "radius": 15000.0},
    "Vidyanagar": {"lat": 17.3945, "lng": 78.5152, "radius": 15000.0},
    "Narayanguda": {"lat": 17.3967, "lng": 78.4876, "radius": 15000.0},
    "Durgabai Deshmukh Colony": {"lat": 17.4215, "lng": 78.5202, "radius": 15000.0},
    "Central Excise Colony": {"lat": 17.3931, "lng": 78.5010, "radius": 15000.0},
    "Amberpet": {"lat": 17.3854, "lng": 78.5244, "radius": 15000.0},
    "Tilaknagar": {"lat": 17.3895, "lng": 78.5112, "radius": 15000.0},
    "Golnaka": {"lat": 17.3789, "lng": 78.5195, "radius": 15000.0},
    "Barkatpura": {"lat": 17.3924, "lng": 78.4962, "radius": 15000.0},
    "Shivam Road": {"lat": 17.3905, "lng": 78.5202, "radius": 15000.0},
    "Jamia Osmania": {"lat": 17.4168, "lng": 78.5192, "radius": 15000.0},
    "Kachiguda": {"lat": 17.3840, "lng": 78.4918, "radius": 15000.0},
    "Badichowdi": {"lat": 17.3878, "lng": 78.4862, "radius": 15000.0},
    "Nampally": {"lat": 17.3926, "lng": 78.4674, "radius": 15000.0},
    "Abids": {"lat": 17.3904, "lng": 78.4731, "radius": 15000.0},
    "Aghapura": {"lat": 17.3881, "lng": 78.4592, "radius": 15000.0},
    "Koti": {"lat": 17.3833, "lng": 78.4812, "radius": 15000.0},
    "Bank Street": {"lat": 17.3852, "lng": 78.4802, "radius": 15000.0},
    "Boggulkunta": {"lat": 17.3912, "lng": 78.4822, "radius": 15000.0},
    "Mehdipatnam": {"lat": 17.3916, "lng": 78.4326, "radius": 15000.0},
    "Karwan": {"lat": 17.3785, "lng": 78.4285, "radius": 15000.0},
    "Secunderabad": {"lat": 17.4399, "lng": 78.4983, "radius": 15000.0},
    "Chilkalguda": {"lat": 17.4322, "lng": 78.5105, "radius": 15000.0},
    "Kavadiguda": {"lat": 17.4195, "lng": 78.4862, "radius": 15000.0},
    "MG Road (James Street)": {"lat": 17.4344, "lng": 78.4901, "radius": 15000.0},
    "Minister Road": {"lat": 17.4431, "lng": 78.4831, "radius": 15000.0},
    "Mylargadda": {"lat": 17.4352, "lng": 78.5142, "radius": 15000.0},
    "Namalagundu": {"lat": 17.4305, "lng": 78.5205, "radius": 15000.0},
    "Padmarao Nagar": {"lat": 17.4278, "lng": 78.5095, "radius": 15000.0},
    "Pan Bazar": {"lat": 17.4355, "lng": 78.4930, "radius": 15000.0},
    "Paradise Circle": {"lat": 17.4434, "lng": 78.4867, "radius": 15000.0},
    "Parsigutta": {"lat": 17.4231, "lng": 78.5135, "radius": 15000.0},
    "Patny": {"lat": 17.4415, "lng": 78.4935, "radius": 15000.0},
    "Rani Gunj": {"lat": 17.4331, "lng": 78.4852, "radius": 15000.0},
    "RP Road": {"lat": 17.4362, "lng": 78.4945, "radius": 15000.0},
    "Sindhi Colony": {"lat": 17.4476, "lng": 78.4792, "radius": 15000.0},
    "Sitaphalmandi": {"lat": 17.4262, "lng": 78.5235, "radius": 15000.0},
    "Tarnaka": {"lat": 17.4294, "lng": 78.5379, "radius": 15000.0},
    "Warsiguda": {"lat": 17.4215, "lng": 78.5285, "radius": 15000.0},
    "Bowenpally": {"lat": 17.4721, "lng": 78.4722, "radius": 15000.0},
    "Karkhana": {"lat": 17.4565, "lng": 78.4922, "radius": 15000.0},
    "Marredpally": {"lat": 17.4484, "lng": 78.5085, "radius": 15000.0},
    "Sikh Village": {"lat": 17.4642, "lng": 78.4885, "radius": 15000.0},
    "Trimulgherry": {"lat": 17.4735, "lng": 78.5022, "radius": 15000.0},
    "Vikrampuri": {"lat": 17.4589, "lng": 78.4985, "radius": 15000.0},
    "Gachibowli": {"lat": 17.4401, "lng": 78.3489, "radius": 15000.0},
    "Gowlidoddi": {"lat": 17.4202, "lng": 78.3364, "radius": 15000.0},
    "Nanakramguda": {"lat": 17.4172, "lng": 78.3556, "radius": 15000.0},
    "HITEC City": {"lat": 17.4483, "lng": 78.3741, "radius": 15000.0},
    "Madhapur": {"lat": 17.4486, "lng": 78.3908, "radius": 15000.0},
    "Kondapur": {"lat": 17.4622, "lng": 78.3568, "radius": 15000.0},
    "Kothaguda": {"lat": 17.4585, "lng": 78.3644, "radius": 15000.0},
    "Kokapet": {"lat": 17.4005, "lng": 78.3278, "radius": 15000.0},
    "Narsingi": {"lat": 17.3912, "lng": 78.3612, "radius": 15000.0},
    "Jubilee Hills": {"lat": 17.4325, "lng": 78.4070, "radius": 15000.0},
    "Banjara Hills": {"lat": 17.4176, "lng": 78.4347, "radius": 15000.0},
    "Film Nagar": {"lat": 17.4121, "lng": 78.4011, "radius": 15000.0},
    "Yousufguda": {"lat": 17.4366, "lng": 78.4282, "radius": 15000.0},
    "Srinagar Colony": {"lat": 17.4374, "lng": 78.4433, "radius": 15000.0},
    "Serilingampally": {"lat": 17.4831, "lng": 78.3252, "radius": 15000.0},
    "Chanda Nagar": {"lat": 17.4931, "lng": 78.3262, "radius": 15000.0},
    "Miyapur": {"lat": 17.4965, "lng": 78.3412, "radius": 15000.0},
    "Kukatpally": {"lat": 17.4852, "lng": 78.3986, "radius": 15000.0},
    "KPHB Colony": {"lat": 17.4844, "lng": 78.3889, "radius": 15000.0},
    "Nizampet": {"lat": 17.5142, "lng": 78.3842, "radius": 15000.0},
    "Balanagar": {"lat": 17.4752, "lng": 78.4412, "radius": 15000.0},
    "Kompally": {"lat": 17.5449, "lng": 78.4754, "radius": 15000.0},
    "Alwal": {"lat": 17.5022, "lng": 78.5012, "radius": 15000.0},
    "Sainikpuri": {"lat": 17.4862, "lng": 78.5412, "radius": 15000.0},
    "Malkajgiri": {"lat": 17.4522, "lng": 78.5312, "radius": 15000.0},
    "Uppal": {"lat": 17.4022, "lng": 78.5612, "radius": 15000.0},
    "Habsiguda": {"lat": 17.4092, "lng": 78.5452, "radius": 15000.0},
    "Nacharam": {"lat": 17.4252, "lng": 78.5582, "radius": 15000.0},
    "Dilsukhnagar": {"lat": 17.3682, "lng": 78.5252, "radius": 15000.0},
    "L.B. Nagar": {"lat": 17.3456, "lng": 78.5512, "radius": 15000.0},
    "Toli Chowki": {"lat": 17.4012, "lng": 78.4012, "radius": 15000.0},
    "Attapur": {"lat": 17.3642, "lng": 78.4312, "radius": 15000.0},
    "Gandipet": {"lat": 17.3912, "lng": 78.3112, "radius": 15000.0},
    "Shamshabad": {"lat": 17.2512, "lng": 78.4312, "radius": 15000.0},

    # --- MUMBAI ---
    "Colaba": {"lat": 18.9067, "lng": 72.8147, "radius": 15000.0},
    "Nariman Point": {"lat": 18.9262, "lng": 72.8225, "radius": 15000.0},
    "Fort": {"lat": 18.9322, "lng": 72.8354, "radius": 15000.0},
    "Churchgate": {"lat": 18.9312, "lng": 72.8258, "radius": 15000.0},
    "Marine Drive": {"lat": 18.9432, "lng": 72.8231, "radius": 15000.0},
    "Malabar Hill": {"lat": 18.9543, "lng": 72.7984, "radius": 15000.0},
    "Breach Candy": {"lat": 18.9742, "lng": 72.8052, "radius": 15000.0},
    "Lower Parel": {"lat": 18.9953, "lng": 72.8300, "radius": 15000.0},
    "Parel": {"lat": 19.0022, "lng": 72.8412, "radius": 15000.0},
    "Dadar": {"lat": 19.0212, "lng": 72.8422, "radius": 15000.0},
    "Bandra West": {"lat": 19.0600, "lng": 72.8338, "radius": 15000.0},
    "Bandra East": {"lat": 19.0625, "lng": 72.8485, "radius": 15000.0},
    "Khar": {"lat": 19.0682, "lng": 72.8372, "radius": 15000.0},
    "Juhu": {"lat": 19.0985, "lng": 72.8265, "radius": 15000.0},
    "Andheri West": {"lat": 19.1197, "lng": 72.8464, "radius": 15000.0},
    "Andheri East": {"lat": 19.1152, "lng": 72.8682, "radius": 15000.0},
    "Powai": {"lat": 19.1176, "lng": 72.9060, "radius": 15000.0},
    "Goregaon West": {"lat": 19.1622, "lng": 72.8374, "radius": 15000.0},
    "Goregaon East": {"lat": 19.1692, "lng": 72.8556, "radius": 15000.0},
    "Malad West": {"lat": 19.1862, "lng": 72.8285, "radius": 15000.0},
    "Kandivali West": {"lat": 19.2062, "lng": 72.8362, "radius": 15000.0},
    "Borivali West": {"lat": 19.2322, "lng": 72.8312, "radius": 15000.0},
    "Thane West": {"lat": 19.2183, "lng": 72.9781, "radius": 15000.0},
    "Vashi": {"lat": 19.0745, "lng": 72.9978, "radius": 15000.0},
    "Nerul": {"lat": 19.0332, "lng": 73.0162, "radius": 15000.0},
    "Kharghar": {"lat": 19.0252, "lng": 73.0672, "radius": 15000.0},

    # FIX 3: Added missing city neighborhoods
    # --- DELHI ---
    "Connaught Place": {"lat": 28.6315, "lng": 77.2167, "radius": 15000.0},
    "Khan Market": {"lat": 28.5993, "lng": 77.2271, "radius": 15000.0},
    "South Ext": {"lat": 28.5706, "lng": 77.2195, "radius": 15000.0},
    "Greater Kailash (GK 1 & 2)": {"lat": 28.5501, "lng": 77.2373, "radius": 15000.0},
    "Hauz Khas Village": {"lat": 28.5494, "lng": 77.2001, "radius": 15000.0},
    "Aerocity": {"lat": 28.5562, "lng": 77.1173, "radius": 15000.0},

    # --- GURGAON ---
    "DLF Phase 3 / CyberHub": {"lat": 28.4952, "lng": 77.0888, "radius": 15000.0},
    "Golf Course Road": {"lat": 28.4726, "lng": 77.1038, "radius": 15000.0},
    "Sector 29": {"lat": 28.4719, "lng": 77.0697, "radius": 15000.0},
    "Sohna Road": {"lat": 28.4231, "lng": 77.0359, "radius": 15000.0},

    # --- NOIDA ---
    "Sector 18": {"lat": 28.5706, "lng": 77.3219, "radius": 15000.0},
    "Sector 62": {"lat": 28.6271, "lng": 77.3664, "radius": 15000.0},
    "Sector 104": {"lat": 28.5282, "lng": 77.3641, "radius": 15000.0},

    # --- BENGALURU ---
    "Indiranagar": {"lat": 12.9784, "lng": 77.6408, "radius": 15000.0},
    "Koramangala": {"lat": 12.9352, "lng": 77.6245, "radius": 15000.0},
    "UB City / Lavelle Road": {"lat": 12.9719, "lng": 77.5963, "radius": 15000.0},
    "Whitefield": {"lat": 12.9698, "lng": 77.7499, "radius": 15000.0},
    "HSR Layout": {"lat": 12.9121, "lng": 77.6446, "radius": 15000.0},

    # --- CHENNAI ---
    "Nungambakkam": {"lat": 13.0569, "lng": 80.2425, "radius": 15000.0},
    "Khader Nawaz Khan Road": {"lat": 13.0489, "lng": 80.2421, "radius": 15000.0},
    "Adyar": {"lat": 13.0012, "lng": 80.2565, "radius": 15000.0},
    "Alwarpet": {"lat": 13.0359, "lng": 80.2556, "radius": 15000.0},

    # --- PUNE ---
    "Koregaon Park": {"lat": 18.5362, "lng": 73.8936, "radius": 15000.0},
    "Kalyani Nagar": {"lat": 18.5481, "lng": 73.9011, "radius": 15000.0},
    "Baner": {"lat": 18.5590, "lng": 73.7868, "radius": 15000.0},
    "Viman Nagar": {"lat": 18.5679, "lng": 73.9143, "radius": 15000.0},

    # --- CHANDIGARH ---
    "Sector 26": {"lat": 30.7333, "lng": 76.8085, "radius": 15000.0},
    "Sector 35": {"lat": 30.7273, "lng": 76.7738, "radius": 15000.0},
    "Elante Mall Area": {"lat": 30.7059, "lng": 76.8014, "radius": 15000.0},
}

CITY_AREA_MAP = {
    "Mumbai / Greater Mumbai": [
        "Colaba", "Nariman Point", "Fort", "Churchgate", "Marine Drive", "Malabar Hill", "Breach Candy",
        "Lower Parel", "Parel", "Dadar", "Bandra West", "Bandra East", "Khar", "Juhu", "Andheri West",
        "Andheri East", "Powai", "Goregaon West", "Goregaon East", "Malad West", "Kandivali West",
        "Borivali West", "Thane West", "Vashi", "Nerul", "Kharghar"
    ],
    "Hyderabad": [
        "Ameerpet", "Begumpet", "SR Nagar", "Prakash Nagar", "Punjagutta", "Balkampet", "Madhura Nagar",
        "Rasoolpura", "Sanathnagar", "Bharat Nagar", "Erragadda", "Borabanda", "Moti Nagar", "Nehru Nagar",
        "Khairatabad", "Somajiguda", "Raj Bhavan Road", "Lakdikapool", "Saifabad", "A.C. Guards", "Masab Tank",
        "Chintal Basti", "Musheerabad", "Chikkadpally", "Himayatnagar", "Ashok Nagar", "Domalguda", "Hyderguda",
        "Ramnagar", "Azamabad", "Adikmet", "Nallakunta", "Shanker Mutt", "RTC X Roads", "Vidyanagar",
        "Narayanguda", "Durgabai Deshmukh Colony", "Central Excise Colony", "Amberpet", "Tilaknagar",
        "Golnaka", "Barkatpura", "Shivam Road", "Jamia Osmania", "Kachiguda", "Badichowdi", "Nampally",
        "Abids", "Aghapura", "Koti", "Bank Street", "Boggulkunta", "Mehdipatnam", "Karwan", "Secunderabad",
        "Chilkalguda", "Kavadiguda", "MG Road (James Street)", "Minister Road", "Mylargadda", "Namalagundu",
        "Padmarao Nagar", "Pan Bazar", "Paradise Circle", "Parsigutta", "Patny", "Rani Gunj", "RP Road",
        "Sindhi Colony", "Sitaphalmandi", "Tarnaka", "Warsiguda", "Bowenpally", "Karkhana", "Marredpally",
        "Sikh Village", "Trimulgherry", "Vikrampuri", "Gachibowli", "Gowlidoddi", "Nanakramguda", "HITEC City",
        "Madhapur", "Kondapur", "Kothaguda", "Kokapet", "Narsingi", "Jubilee Hills", "Banjara Hills",
        "Film Nagar", "Yousufguda", "Srinagar Colony", "Serilingampally", "Chanda Nagar", "Miyapur",
        "Kukatpally", "KPHB Colony", "Nizampet", "Balanagar", "Kompally", "Alwal", "Sainikpuri",
        "Malkajgiri", "Uppal", "Habsiguda", "Nacharam", "Dilsukhnagar", "L.B. Nagar", "Toli Chowki",
        "Attapur", "Gandipet", "Shamshabad"
    ],
    "Delhi": ["Connaught Place", "Khan Market", "South Ext", "Greater Kailash (GK 1 & 2)", "Hauz Khas Village", "Aerocity"],
    "Gurgaon": ["DLF Phase 3 / CyberHub", "Golf Course Road", "Sector 29", "Sohna Road"],
    "Noida": ["Sector 18", "Sector 62", "Sector 104"],
    "Bengaluru": ["Indiranagar", "Koramangala", "UB City / Lavelle Road", "Whitefield", "HSR Layout"],
    "Chennai": ["Nungambakkam", "Khader Nawaz Khan Road", "Adyar", "Alwarpet"],
    "Pune": ["Koregaon Park", "Kalyani Nagar", "Baner", "Viman Nagar"],
    "Chandigarh / Tricity": ["Sector 26", "Sector 35", "Elante Mall Area"]
}

MANAGER_PASSWORD = "APA@2024"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for col in ALL_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=ALL_COLUMNS)

df = load_data()

# FIX 5: Lat/lng validation helper
def parse_coordinate(value, field_name):
    """Returns (float, error_message). error_message is None if valid."""
    if value == "" or value is None:
        return None, None
    try:
        result = float(value)
        return result, None
    except (ValueError, TypeError):
        return None, f"⚠️ Invalid {field_name}: '{value}' is not a valid number. Pin will not appear on map."

def get_places_new_v2_leads(api_key, city, area, limit):
    leads = []
    url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:searchText"

    headers = {
        "content-type": "application/json",
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.id,places.priceLevel,places.types",
        "x-rapidapi-host": "google-map-places-new-v2.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }

    payload = {
        "textQuery": f"restaurants cafes bars bakeries fast food in {area} {city.split(' / ')[0]}",
        "languageCode": "en",
        "maxResultCount": int(limit)
    }

    if area in NEIGHBORHOOD_CONFIG:
        config = NEIGHBORHOOD_CONFIG[area]
        payload["locationBias"] = {
            "circle": {
                "center": {"latitude": config["lat"], "longitude": config["lng"]},
                "radius": config["radius"]
            }
        }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            places = response.json().get("places", [])
            for place in places:
                name = place.get("displayName", {}).get("text", "F&B Venue")
                address = place.get("formattedAddress", f"{area}, {city}")
                loc = place.get("location", {})
                lat = loc.get("latitude", "")
                lon = loc.get("longitude", "")
                rating = place.get("rating", "")
                # FIX 4: Removed random.randint — use empty string if not returned
                reviews = place.get("userRatingCount", "")
                place_id = place.get("id", "")

                # FIX 6: Derive Price Segment from priceLevel field
                raw_price_level = place.get("priceLevel", "")
                price_segment = PRICE_LEVEL_MAP.get(raw_price_level, "")

                all_tags = place.get("types", [])
                type_priority = ["restaurant", "cafe", "bar", "coffee_shop", "bakery", "fast_food_restaurant", "pub", "night_club"]
                detected_type = next((t for t in type_priority if t in all_tags), "Food Space")
                clean_type = detected_type.replace("_", " ").title()

                leads.append({
                    "Restaurant Name": name, "Cuisine/Type": clean_type, "Zone/Area": area,
                    "Address": address, "Latitude": float(lat) if lat != "" else "",
                    "Longitude": float(lon) if lon != "" else "",
                    "Map Link": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "",
                    "Google Rating": str(rating), "Total Reviews": str(reviews),
                    "Price Segment": price_segment,
                    "Lead Source": "Google Maps V2 Global Sweep", "Lead Status": "Cold Lead",
                    "Last Contacted": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    except Exception as e:
        st.error(f"Mapping Connection Issue: {str(e)}")
    return leads

# ==================== INTERFACE LAYOUT ====================
st.sidebar.markdown("### 🔐 Admin Controls")
user_password = st.sidebar.text_input("Enter Manager Password", type="password")
is_manager = (user_password == MANAGER_PASSWORD)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Pipeline Dashboard", "⚡ Quick Update / New Lead", "📥 Bulk Import CSV", "🔍 Real-Time Lead Generator"])

# -------------------- TAB 1 --------------------
with tab1:
    st.subheader("Current Pipeline")
    if df.empty:
        st.info("No data available yet. Run the harvester on Tab 4.")
    else:
        if is_manager:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Full CRM Database to CSV / Excel",
                data=csv_data,
                file_name=f"apa_pipeline_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="secure_mgr_export_btn"
            )
        else:
            st.warning("🔒 Database export features are restricted. Enter Admin Password to request spreadsheet extracts.")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_query = st.text_input("🔍 Search by Establishment Name")
        with col_f2:
            zone_filter = st.multiselect("Filter by Zone/Area", options=list(df["Zone/Area"].dropna().unique()))

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df['Restaurant Name'].str.contains(search_query, case=False, na=False)]
        if zone_filter:
            filtered_df = filtered_df[filtered_df['Zone/Area'].isin(zone_filter)]

        display_df = filtered_df.copy()
        if not is_manager:
            for col in ["Acquisition Cost (Excl GST)", "Agreed Margin %", "Monthly Volume (Bottles)"]:
                if col in display_df.columns:
                    display_df[col] = "🔒 Restricted"

        st.dataframe(display_df, use_container_width=True)

        # FIX 5: Validate coordinates before rendering map
        map_df = filtered_df[['Latitude', 'Longitude']].copy()
        map_df['latitude'] = pd.to_numeric(map_df['Latitude'], errors='coerce')
        map_df['longitude'] = pd.to_numeric(map_df['Longitude'], errors='coerce')
        map_df = map_df.dropna(subset=['latitude', 'longitude'])

        invalid_count = len(filtered_df) - len(map_df)
        if invalid_count > 0:
            st.warning(f"⚠️ {invalid_count} record(s) have missing or invalid coordinates and won't appear on the map.")

        if not map_df.empty:
            st.map(map_df[['latitude', 'longitude']], use_container_width=True)

# -------------------- TAB 2 --------------------
with tab2:
    st.subheader("Sales Rep Log Entry & Deletion Portal")
    existing_restaurants = ["-- Create New Blank Lead --"] + list(df["Restaurant Name"].dropna().unique())
    selected_rest = st.selectbox("Select Restaurant to load existing details (or leave blank for a new manual entry):", existing_restaurants)

    defaults = {col: "" for col in ALL_COLUMNS}
    if selected_rest != "-- Create New Blank Lead --":
        row_match = df[df["Restaurant Name"] == selected_rest].iloc[0]
        for col in ALL_COLUMNS:
            defaults[col] = row_match[col] if pd.notna(row_match[col]) else ""

    if selected_rest != "-- Create New Blank Lead --" and is_manager:
        if st.button("❌ Completely Delete This Entry From CRM"):
            df = df[df["Restaurant Name"] != selected_rest]
            df.to_csv(DATA_FILE, index=False)
            st.warning(f"Deleted '{selected_rest}'.")
            time.sleep(1)
            st.rerun()

    with st.form("crm_entry_form", clear_on_submit=True):
        st.markdown("### 🏛️ 1. Establishment Profile & Core Data")
        col1, col2 = st.columns(2)
        with col1:
            r_name = st.text_input("Restaurant Name *", value=defaults["Restaurant Name"])
            c_name = st.text_input("Company / Parent Group Name", value=defaults["Company Name"])
            cuisine = st.text_input("Cuisine / Establishment Type", value=defaults["Cuisine/Type"])
            zone = st.text_input("Zone / Area", value=defaults["Zone/Area"])
            address = st.text_area("Address", value=defaults["Address"])
        with col2:
            web = st.text_input("Website", value=defaults["Website"])
            r_phone = st.text_input("Restaurant Phone", value=defaults["Restaurant Phone"])
            rating = st.text_input("Google Rating", value=str(defaults["Google Rating"]))
            map_l = st.text_input("Google Maps Link", value=defaults["Map Link"])
            # FIX 5: Show existing values but label will warn on invalid
            lat_in = st.text_input("Latitude (decimal, e.g. 17.4251)", value=str(defaults["Latitude"]))
            lon_in = st.text_input("Longitude (decimal, e.g. 78.4595)", value=str(defaults["Longitude"]))

        st.markdown("### 👥 2. Internal Contact Directory")
        col3, col4 = st.columns(2)
        with col3:
            p_name = st.text_input("Primary Contact Name", value=defaults["Primary Contact Name"])
            p_role = st.text_input("Primary Contact Role", value=defaults["Primary Contact Role"])
            p_phone = st.text_input("Primary Contact Phone", value=defaults["Primary Contact Phone"])
            p_email = st.text_input("Primary Contact Email", value=defaults["Primary Contact Email"])
        with col4:
            dm_name = st.text_input("Decision Maker Name", value=defaults["Decision Maker Name"])
            dm_details = st.text_area("Decision Maker Contact Details / Notes", value=defaults["Decision Maker Details"])
            o_name = st.text_input("Other Contact Name", value=defaults["Other Contact Name"])
            o_details = st.text_area("Other Contact Details / Notes", value=defaults["Other Contact Details"])

        st.markdown("### 📊 3. Commercial Pipeline & Proposal Terms")
        col5, col6 = st.columns(2)
        with col5:
            curr_b = st.text_input("Current Water Brand In Use", value=defaults["Current Brand"])
            b_type = st.text_input("Bottle Type (Glass/Plastic/Volume)", value=defaults["Bottle Type"])
            acq_c = st.text_input("Acquisition Cost per bottle (Excl. GST)", value=str(defaults["Acquisition Cost (Excl GST)"]))
            m_vol = st.text_input("Monthly Volume (Bottles)", value=str(defaults["Monthly Volume (Bottles)"]))
            expiry = st.text_input("Competitor Contract Expiry (YYYY-MM-DD)", value=defaults["Competitor Contract Expiry"])
        with col6:
            prop_sku = st.text_input("Proposed APA SKU", value=defaults["Proposed APA SKU"])
            sample_date = st.text_input("Sample Delivery Date (YYYY-MM-DD)", value=defaults["Sample Delivery Date"])
            margin = st.text_input("Agreed Margin %", value=str(defaults["Agreed Margin %"]))
            credit = st.text_input("Credit Terms (e.g., 30 Days Net)", value=defaults["Credit Terms"])
            lead_src = st.text_input("Lead Source", value=defaults["Lead Source"] if defaults["Lead Source"] else "Manual Entry")

        st.markdown("### ⚡ 4. Activity Logs & Status Updates")
        col7, col8 = st.columns(2)
        with col7:
            salesperson = st.text_input("Salesperson Name", value=defaults["Salesperson Name"])
            status_options = ["Cold Lead", "Warm Lead", "Sample Dropped", "Tasting Scheduled", "Negotiation", "Active Client", "Lost Account"]
            current_status_idx = status_options.index(defaults["Lead Status"]) if defaults["Lead Status"] in status_options else 0
            status = st.selectbox("Lead Status", status_options, index=current_status_idx)
        with col8:
            notes = st.text_area("Interaction Notes / Summary", value=defaults["Interaction Summary"])
            next_f = st.text_input("Next Follow-up Date (YYYY-MM-DD)", value=defaults["Next Follow-up"])

        if st.form_submit_button("💾 Save & Update Lead Data") and r_name:
            # FIX 5: Validate lat/lng before saving
            lat_val, lat_err = parse_coordinate(lat_in.strip(), "Latitude")
            lon_val, lon_err = parse_coordinate(lon_in.strip(), "Longitude")

            coord_errors = [e for e in [lat_err, lon_err] if e]
            for err in coord_errors:
                st.warning(err)

            form_entry = {
                "Restaurant Name": r_name, "Company Name": c_name, "Cuisine/Type": cuisine, "Zone/Area": zone, "Address": address,
                "Website": web, "Restaurant Phone": r_phone, "Google Rating": rating, "Map Link": map_l,
                "Latitude": lat_val if lat_val is not None else "",
                "Longitude": lon_val if lon_val is not None else "",
                "Primary Contact Name": p_name, "Primary Contact Role": p_role, "Primary Contact Phone": p_phone, "Primary Contact Email": p_email,
                "Decision Maker Name": dm_name, "Decision Maker Details": dm_details, "Other Contact Name": o_name, "Other Contact Details": o_details,
                "Current Brand": curr_b, "Bottle Type": b_type, "Acquisition Cost (Excl GST)": acq_c, "Monthly Volume (Bottles)": m_vol, "Competitor Contract Expiry": expiry,
                "Proposed APA SKU": prop_sku, "Sample Delivery Date": sample_date, "Agreed Margin %": margin, "Credit Terms": credit, "Lead Source": lead_src,
                "Salesperson Name": salesperson, "Lead Status": status, "Last Contacted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Interaction Summary": notes, "Next Follow-up": next_f
            }
            if selected_rest != "-- Create New Blank Lead --":
                df = df[df["Restaurant Name"] != selected_rest]
            df = pd.concat([df, pd.DataFrame([form_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Successfully saved and updated entry for '{r_name}'!")
            st.rerun()

# -------------------- TAB 3 --------------------
with tab3:
    st.subheader("📥 Bulk Import External Scraped Leads")
    st.markdown("Drop any spreadsheet matching your core structural format here to append items directly into your dashboard index.")

    uploaded_file = st.file_uploader("Upload Scraped Leads File (CSV Format Only)", type=["csv"])

    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)
            required_check = "Restaurant Name"

            if required_check not in import_df.columns:
                st.error(f"Invalid Format Structure: The uploaded CSV document must contain at least a '{required_check}' column layout.")
            else:
                if st.button("⚡ Execute Bulk Data Append"):
                    new_rows = 0
                    imported_records = []

                    for _, row in import_df.iterrows():
                        clean_name = str(row["Restaurant Name"]).strip()
                        if clean_name not in df["Restaurant Name"].dropna().values:
                            entry = {col: "" for col in ALL_COLUMNS}
                            for col in import_df.columns:
                                if col in ALL_COLUMNS:
                                    entry[col] = row[col]
                            imported_records.append(entry)
                            new_rows += 1

                    if imported_records:
                        df = pd.concat([df, pd.DataFrame(imported_records)], ignore_index=True)
                        df.to_csv(DATA_FILE, index=False)
                        st.success(f"Success! Bulk appended {new_rows} brand new listings into your database.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("All data listings in the uploaded file already exist inside your system database.")
        except Exception as e:
            st.error(f"Parsing Failure: {str(e)}")

# -------------------- TAB 4 --------------------
with tab4:
    st.subheader("🔍 Live Google Places New V2 Harvester")
    st.markdown("Sweeps a massive 15km territory mapping out **all** restaurants, cafés, fast food joints, juice bars, bakeries, and lounges.")

    city_selected = st.selectbox("Target City Location", list(CITY_AREA_MAP.keys()))
    area_selected = st.selectbox("Micro-Neighborhood Cluster", CITY_AREA_MAP[city_selected])
    target_count = st.slider("Target extraction count (max 20 per Google Places API limit)", min_value=5, max_value=20, value=20)

    if st.button("🚀 Harvest and Sync Map Locations"):
        active_key = st.secrets.get("RAPIDAPI_KEY", "")
        if not active_key:
            st.error("Missing api host token credentials inside system vault configuration.")
        else:
            progress_bar = st.progress(0, text="Connecting to Google Places API...")
            # FIX 7: Use st.spinner for real visual feedback during the API call
            with st.spinner(f"Fetching F&B venues in {area_selected}, {city_selected}..."):
                progress_bar.progress(20, text="Request sent — awaiting response...")
                scraped_results = get_places_new_v2_leads(active_key, city_selected, area_selected, target_count)
                progress_bar.progress(60, text="Processing results...")

            new_leads_added = 0
            if scraped_results:
                scraped_data = []
                for item in scraped_results:
                    if item["Restaurant Name"].strip() not in df["Restaurant Name"].dropna().values:
                        entry = {col: "" for col in ALL_COLUMNS}
                        entry.update(item)
                        scraped_data.append(entry)
                        new_leads_added += 1
                if scraped_data:
                    df = pd.concat([df, pd.DataFrame(scraped_data)], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    progress_bar.progress(100, text="Done!")
                    st.success(f"Success! Imported {new_leads_added} new F&B targets directly into the CRM database.")
                    time.sleep(1)
                    st.rerun()
                else:
                    progress_bar.progress(100, text="Done!")
                    st.warning("All returned items already match existing records for this specific micro-cluster.")
            else:
                progress_bar.progress(100, text="Done!")
                st.error("Zero records returned. Check your RapidAPI configuration credentials.")