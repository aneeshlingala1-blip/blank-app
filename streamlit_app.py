import streamlit as st
import pandas as pd
import os
import time
import requests
import random
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

# 🗺️ FULL RESTORED COORDINATES INDEX WITH 15KM MASSIVE RADIUS
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
}

# 🌍 COMPLETE MASTER REGIONAL MAP INDEX
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
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=ALL_COLUMNS)

df = load_data()

def get_places_new_v2_leads(api_key, city, area, limit):
    leads = []
    url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:searchText"
    
    headers = {
        "content-type": "application/json",
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.id,places.priceLevel,places.types",
        "x-rapidapi-host": "google-map-places-new-v2.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }
    
    # Fully generic contextual query string
    payload = {
        "textQuery": f"places to eat and drink in {area}, {city.split(' / ')[0]}",
        "languageCode": "en",
        "maxResultCount": int(limit),
        # 🚀 COMPLETE UNRESTRICTED CATEGORY NET
        "includedTypes": [
            "restaurant", "cafe", "bar", "coffee_shop", "bakery", 
            "fast_food_restaurant", "ice_cream_shop", "sandwich_shop", 
            "juice_shop", "pub", "night_club", "meal_takeaway", "food"
        ]
    }
    
    # Inject spatial geofence biasing coordinates dynamically if available
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
                lat = loc.get("latitude", 17.3850)
                lon = loc.get("longitude", 78.4867)
                rating = place.get("rating", "4.0")
                reviews = place.get("userRatingCount", random.randint(30, 300))
                place_id = place.get("id", "")
                
                all_tags = place.get("types", [])
                type_priority = ["restaurant", "cafe", "bar", "coffee_shop", "bakery", "fast_food_restaurant", "pub", "night_club"]
                detected_type = next((t for t in type_priority if t in all_tags), "Food Space")
                clean_type = detected_type.replace("_", " ").title()
                
                leads.append({
                    "Restaurant Name": name, "Cuisine/Type": clean_type, "Zone/Area": area, 
                    "Address": address, "Latitude": float(lat), "Longitude": float(lon),
                    "Map Link": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "",
                    "Google Rating": str(rating), "Total Reviews": str(reviews), "Price Segment": "₹₹₹",
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

with tab1:
    st.subheader("Current Pipeline")
    if df.empty:
        st.info("No data available yet. Run the harvester on Tab 4.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_query = st.text_input("🔍 Search by Establishment Name")
        with col_f2: zone_filter = st.multiselect("Filter by Zone/Area", options=list(df["Zone/Area"].dropna().unique()))
        
        filtered_df = df
        if search_query: filtered_df = filtered_df[filtered_df['Restaurant Name'].str.contains(search_query, case=False, na=False)]
        if zone_filter: filtered_df = filtered_df[filtered_df['Zone/Area'].isin(zone_filter)]

        st.dataframe(filtered_df, use_container_width=True)
        
        map_df = filtered_df[['Latitude', 'Longitude']].dropna().copy()
        map_df['latitude'] = pd.to_numeric(map_df['Latitude'], errors='coerce')
        map_df['longitude'] = pd.to_numeric(map_df['Longitude'], errors='coerce')
        st.map(map_df.dropna()[['latitude', 'longitude']], use_container_width=True)

with tab2:
    st.write("Manual single entry logging node.")

with tab3:
    st.write("CSV document uploading layout frame.")

with tab4:
    st.subheader("🔍 Live Google Places New V2 Harvester")
    st.markdown("Sweeps a massive 15km territory mapping out **all** restaurants, cafés, fast food joints, juice bars, bakeries, and lounges.")
    
    city_selected = st.selectbox("Target City Location", list(CITY_AREA_MAP.keys()))
    area_selected = st.selectbox("Micro-Neighborhood Cluster", CITY_AREA_MAP[city_selected])
    target_count = st.slider("Target extraction count", min_value=5, max_value=20, value=20)

    if st.button("🚀 Harvest and Sync Map Locations"):
        active_key = st.secrets.get("RAPIDAPI_KEY", "")
        if not active_key:
            st.error("Missing api host token credentials inside system vault configuration.")
        else:
            progress_bar = st.progress(0)
            scraped_results = get_places_new_v2_leads(active_key, city_selected, area_selected, target_count)
            progress_bar.progress(60)
            
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
                    progress_bar.progress(100)
                    st.success(f"Success! Imported {new_leads_added} new F&B targets directly into the CRM database.")
                    time.sleep(1)
                    st.rerun()
                else:
                    progress_bar.progress(100)
                    st.warning("All returned items already match existing records for this specific micro-cluster.")
            else:
                progress_bar.progress(100)
                st.error("Zero records returned. Check your RapidAPI configuration credentials.")