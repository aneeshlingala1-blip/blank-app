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

# Page configuration for a clean layout
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

# 🌍 EXHAUSTIVE HYDERABAD & MUMBAI REGIONAL MASTER INDEXES
CITY_AREA_MAP = {
    "Mumbai / Greater Mumbai": [
        "Colaba", "Nariman Point", "Fort", "Churchgate", "Marine Drive", "Malabar Hill", "Breach Candy", 
        "Grant Road", "Byculla", "Mazagaon", "Mahalaxmi", "Lower Parel", "Parel", "Dadar", "Matunga", 
        "Sion", "Mahim", "Wadala", "Prabhadevi", "Dharavi", "Chunabhatti", "Bandra West", "Bandra East", 
        "Khar", "Santacruz West", "Santacruz East", "Juhu", "Vile Parle West", "Vile Parle East", 
        "Andheri West", "Andheri East", "Versova", "Jogeshwari West", "Jogeshwari East", "Goregaon West", 
        "Goregaon East", "Malad West", "Malad East", "Kandivali West", "Kandivali East", "Borivali West", 
        "Borivali East", "Dahisar", "Kurla", "Chembur", "Ghatkopar West", "Ghatkopar East", "Vikhroli", 
        "Powai", "Bhandup", "Mulund West", "Mulund East", "Govandi", "Mankhurd", "Kanjurmarg", "Mira Road", 
        "Bhayandar West", "Bhayandar East", "Kashimira", "Uttan", "Vasai West", "Vasai East", "Nalasopara West", 
        "Nalasopara East", "Sopara", "Vasai Road", "Thane West", "Thane East", "Ghodbunder Road", "Majiwada", 
        "Kopri", "Naupada", "Wagle Estate", "Teen Hath Naka", "Hiranandani Estate", "Pokhran Road", "Manpada", 
        "Upvan / Vasant Vihar", "Vashi", "Nerul", "CBD Belapur", "Kharghar", "Airoli", "Ghansoli", 
        "Kopar Khairane", "Sanpada", "Juinagar", "Seawoods", "Panvel", "Ulwe", "Dronagiri", "Taloja", 
        "Kamothe", "Kalamboli", "Turbhe", "Roadpali", "Kalyan West", "Kalyan East", "Dombivli West", 
        "Dombivli East", "Ulhasnagar", "Ambernath", "Badlapur", "Titwala", "Shahad", "Bhiwandi", 
        "Murbad", "Shahapur", "Wada", "Palghar", "Boisar", "Karjat", "Khopoli", "Pen"
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
        "Sindhi Colony", "Sitaphalmandi", "Tarnaka", "Warsiguda", "Addagutta", "Tukaramgate", "Kalasiguda", 
        "Secunderabad Cantonment", "Bowenpally", "Karkhana", "Marredpally", "Sikh Village", "Trimulgherry", 
        "Vikrampuri", "Gachibowli", "Gowlidoddi", "Nanakramguda", "HITEC City", "Madhapur", "Kondapur", 
        "Kothaguda", "Kokapet", "Narsingi", "Jubilee Hills", "Banjara Hills", "Film Nagar", "Yousufguda", 
        "Srinagar Colony", "Serilingampally", "Chanda Nagar", "Allwyn Colony", "Hafeezpet", "Madinaguda", 
        "Miyapur", "Maktha Mahaboobpet", "Kukatpally", "Bachupally", "KPHB Colony", "Nizampet", "Pragathi Nagar", 
        "Moosapet", "Mallampet", "Patancheru", "BHEL Township", "RC Puram", "Ameenpur", "Beeramguda", 
        "Kistareddypet", "IDA Bollaram", "Medical Devices Park", "Afzal Gunj", "Aliabad", "Alijah Kotla", 
        "Asif Nagar", "Azampura", "Barkas", "Bazarghat", "Begum Bazaar", "Chaderghat", "Chanchalguda", 
        "Chandrayan Gutta", "Chatta Bazaar", "Dabirpura", "Dar‑ul‑Shifa", "Dhoolpet", "Edi Bazar", 
        "Falaknuma", "Malakpet", "Moghalpura", "Jahanuma", "Laad Bazaar", "Lal Darwaza", "Langar Houz", 
        "Madina", "Maharajgunj", "Mehboob ki Mehendi", "Mir Alam Tank", "Mozamjahi Market", "Nawab Saheb Kunta", 
        "Nayapul", "Noorkhan Bazar", "Pisal Banda", "Purana Pul", "Putlibowli", "Rein Bazar", "Santoshnagar", 
        "Shahran Market", "Shah Ali Banda", "Sultan Bazar", "Udden Gadda", "Uppuguda", "Yakutpura", 
        "Owaiy Colony", "Kereemuddin House", "Balanagar", "Fateh Nagar", "Ferozguda", "Old Bowenpally", 
        "Hasmathpet", "Suchitra Center", "Quthbullapur", "Jeedimetla", "Jagadgirigutta", "Suraram", 
        "Pet Basheerabad", "Kompally", "Maisammaguda", "Medchal", "Kandlakoya", "Alwal", "Lothkunta", 
        "Old Alwal", "Macha Bollaram", "Venkatapuram", "Shamirpet", "Malkajgiri", "Anandbagh", "Ammuguda", 
        "Gautham Nagar", "Kakatiya Nagar", "Vinayak Nagar", "Moula‑Ali", "Neredmet", "Old Neredmet", 
        "Safilguda", "Sainikpuri", "Yapral", "Kapra", "A.S. Rao Nagar", "ECIL X‑Roads", "Kamala Nagar", 
        "Kushaiguda", "Cherlapally", "Keesara", "Nagaram", "Dammaiguda", "Jawaharnagar", "Rampally", 
        "Cheriyal", "Uppal", "Habsiguda", "Ramanthapur", "Boduppal", "Nagole", "Nacharam", "Ghatkesar", 
        "Peerzadiguda", "Chengicherla", "Pocharam", "Mallapur", "Narapally", "Medipally", "Dilsukhnagar", 
        "Kothapet", "Gaddiannaram", "Moosarambagh", "Chaitanyapuri", "L.B. Nagar", "Bairamalguda", 
        "Chintalakunta", "Vanasthalipuram", "Hastinapuram", "Saroornagar", "Badangpet", "Balapur", 
        "Champapet", "Jillelguda", "Karmanghat", "Lingojiguda", "Meerpet", "Sanghi Nagar", "Hayathnagar", 
        "Osman Nagar", "Ibrahimpatnam", "Toli Chowki", "Gudimalkapur", "Mallepally", "Padmanabha Nagar Colony", 
        "Red Hills", "Shaikpet", "Rajendranagar", "Attapur", "Bandlaguda", "Gandipet", "Kismatpur", 
        "Ring Road", "Puppalguda", "Kotapet", "Chevella", "Moinabad", "Shamshabad", "Rajiv Gandhi International Airport", 
        "Umdanagar", "Shadnagar"
    ],
    "Delhi": [
        "Connaught Place", "Khan Market", "South Ext", "Greater Kailash (GK 1 & 2)", 
        "Hauz Khas Village", "Aerocity", "Vasant Kunj", "Saket", "Rajouri Garden", 
        "Chanakyapuri", "Karol Bagh", "Dwarka", "Rohini", "Pitampura", "Civil Lines", "Chandni Chowk"
    ],
    "Gurgaon": [
        "DLF Phase 3 / CyberHub", "Golf Course Road", "Sector 29", "Sohna Road", "Ambience Island", 
        "DLF Phase 1", "DLF Phase 2", "DLF Phase 4", "DLF Phase 5", "Golf Course Extension Road"
    ],
    "Noida": [
        "Sector 18", "Sector 62", "Noida Extension (Sector 4)", "Sector 137", "Sector 15", 
        "Sector 16", "Sector 104", "Sector 110", "Sector 128 (Wish Town)", "Noida Expressway"
    ],
    "Bengaluru": [
        "Indiranagar", "Koramangala", "UB City / Lavelle Road", "MG Road / Brigade Road", 
        "Jayanagar", "Whitefield", "HSR Layout", "Sadashivanagar", "Malleshwaram", 
        "Rajajinagar", "Frazer Town", "Kalyan Nagar", "Bellandur", "Electronic City", "JP Nagar"
    ],
    "Chennai": [
        "Nungambakkam", "Khader Nawaz Khan Road", "Adyar", "Alwarpet", "Anna Nagar", 
        "OMR (Old Mahabalipuram Road)", "ECR (East Coast Road)", "T-Nagar", "Mylapore", "Royapettah"
    ],
    "Pune": [
        "Koregaon Park", "Kalyani Nagar", "Kothrud", "Baner", "Viman Nagar", "Hinjewadi", 
        "Shivajinagar", "FC Road", "JM Road", "Camp", "MG Road Pune", "Balewadi High Street"
    ],
    "Chandigarh / Tricity": [
        "Sector 26", "Sector 35", "Sector 7", "Sector 8", "Sector 9", "Sector 17", 
        "Elante Mall Area", "Phase 3B2 (Mohali)", "MDC Sector 5 (Panchkula)", "Zirakpur"
    ]
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

# 🌐 COMPLETE UNRESTRICTED DATA EXTRACTION NODE
def get_places_new_v2_leads(api_key, city, area, limit):
    leads = []
    url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:searchText"
    
    headers = {
        "content-type": "application/json",
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.id,places.priceLevel,places.primaryType,places.types",
        "x-rapidapi-host": "google-map-places-new-v2.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }
    
    city_defaults = {
        "mumbai": (19.0760, 72.8777), "hyderabad": (17.3850, 78.4867), "delhi": (28.6139, 77.2090),
        "gurgaon": (28.4595, 77.0266), "noida": (28.5355, 77.3910), "bengaluru": (12.9716, 77.5946),
        "chennai": (13.0827, 80.2707), "pune": (18.5204, 73.8567), "chandigarh": (30.7333, 76.7794)
    }
    
    clean_city_name = city.split(" / ")[0].strip().lower()
    target_lat, target_lon = city_defaults.get(clean_city_name, (19.0760, 72.8777))
    
    # Combined broad search queries ensuring QSR chains and cafes fall right into the data grid loop
    payload = {
        "textQuery": f"restaurants cafes bars fast food chains mcdonalds starbucks dining joints eateries in {area}, {city.split(' / ')[0]}",
        "languageCode": "en",
        "maxResultCount": limit,
        "locationBias": {
            "circle": {
                "center": {"latitude": target_lat, "longitude": target_lon},
                "radius": 9000.0
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            places = response.json().get("places", [])
            for place in places:
                name = place.get("displayName", {}).get("text", "Food & Beverage Venue")
                address = place.get("formattedAddress", f"{area}, {city}, India")
                loc = place.get("location", {})
                lat = loc.get("latitude", target_lat)
                lon = loc.get("longitude", target_lon)
                rating = place.get("rating", "4.2")
                reviews = place.get("userRatingCount", random.randint(50, 500))
                place_id = place.get("id", "")
                
                # Unfiltered metadata tag analyzer captures all variations without exception
                all_tags = place.get("types", [])
                primary_tag = place.get("primaryType", "restaurant")
                local_specialty = next((t for t in all_tags if any(k in t for k in ["restaurant", "cafe", "bar", "bakery", "food", "coffee", "shop", "establishment"])), primary_tag)
                clean_type = local_specialty.replace("_", " ").title()
                
                g_price = place.get("priceLevel", "PRICE_LEVEL_MODERATE")
                price_symbols = {"PRICE_LEVEL_LOW": "₹", "PRICE_LEVEL_MODERATE": "₹₹", "PRICE_LEVEL_EXPENSIVE": "₹₹₹", "PRICE_LEVEL_VERY_EXPENSIVE": "₹₹₹₹"}
                final_price = price_symbols.get(g_price, "₹₹")
                
                leads.append({
                    "Restaurant Name": name, "Company Name": "", "Cuisine/Type": clean_type,
                    "Zone/Area": area, "Address": address, "Latitude": float(lat), "Longitude": float(lon),
                    "Map Link": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else f"http://maps.google.com/?q={lat},{lon}",
                    "Website": "", "Google Rating": str(rating), "Total Reviews": str(reviews), "Price Segment": final_price, "Restaurant Phone": "",
                    "Lead Source": "Google Maps Platform (All-Inclusive)", "Lead Status": "Cold Lead", "Last Contacted": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    except Exception as e:
        st.error(f"API Mapping Refusal: {str(e)}")
    return leads

# ==================== STREAMLIT INTERFACE RENDERING ====================

st.sidebar.markdown("### 🔐 Admin Controls")
user_password = st.sidebar.text_input("Enter Manager Password", type="password")
is_manager = (user_password == MANAGER_PASSWORD)

if is_manager:
    st.sidebar.success("Manager Access Granted")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Pipeline Dashboard", "⚡ Quick Update / New Lead", "📥 Bulk Import CSV", "🔍 Real-Time Lead Generator"])

# ==================== TAB 1 ====================
with tab1:
    st.subheader("Current Pipeline")
    if df.empty:
        st.info("The CRM is empty. Use Tab 4 to generate targets.")
    else:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1: search_query = st.text_input("🔍 Search by Restaurant")
        with col_f2: status_filter = st.multiselect("Filter by Status", options=list(df["Lead Status"].dropna().unique()))
        with col_f3: zone_filter = st.multiselect("Filter by Zone/Area", options=list(df["Zone/Area"].dropna().unique()))
        
        filtered_df = df
        if search_query: filtered_df = filtered_df[filtered_df['Restaurant Name'].str.contains(search_query, case=False, na=False)]
        if status_filter: filtered_df = filtered_df[filtered_df['Lead Status'].isin(status_filter)]
        if zone_filter: filtered_df = filtered_df[filtered_df['Zone/Area'].isin(zone_filter)]
            
        display_df = filtered_df.copy()
        if not is_manager:
            for col in ["Acquisition Cost (Excl GST)", "Agreed Margin %", "Monthly Volume (Bottles)"]:
                if col in display_df.columns: display_df[col] = "🔒 Restricted"
        st.dataframe(display_df, use_container_width=True)
        
        if not filtered_df.empty:
            map_df = filtered_df[['Latitude', 'Longitude']].dropna()
            map_df['Latitude'] = pd.to_numeric(map_df['Latitude'], errors='coerce')
            map_df['Longitude'] = pd.to_numeric(map_df['Longitude'], errors='coerce')
            st.map(map_df.dropna().rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'}), use_container_width=True)

# ==================== TAB 2 ====================
with tab2:
    st.subheader("Sales Rep Log Entry & Deletion Portal")
    existing_restaurants = ["-- Create New Blank Lead --"] + list(df["Restaurant Name"].dropna().unique())
    selected_rest = st.selectbox("Select Restaurant to load existing details:", existing_restaurants)
    
    defaults = {col: "" for col in ALL_COLUMNS}
    if selected_rest != "-- Create New Blank Lead --":
        row_match = df[df["Restaurant Name"] == selected_rest].iloc[0]
        for col in ALL_COLUMNS: 
            defaults[col] = row_match[col] if pd.notna(row_match[col]) else ""

    if selected_rest != "-- Create New Blank Lead --":
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
            lat_in = st.text_input("Latitude", value=str(defaults["Latitude"]))
            lon_in = st.text_input("Longitude", value=str(defaults["Longitude"]))

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
            form_entry = {}
            form_entry.update({
                "Restaurant Name": r_name, "Company Name": c_name, "Cuisine/Type": cuisine, "Zone/Area": zone, "Address": address,
                "Website": web, "Restaurant Phone": r_phone, "Google Rating": rating, "Map Link": map_l, "Latitude": lat_in, "Longitude": lon_in,
                "Primary Contact Name": p_name, "Primary Contact Role": p_role, "Primary Contact Phone": p_phone, "Primary Contact Email": p_email,
                "Decision Maker Name": dm_name, "Decision Maker Details": dm_details, "Other Contact Name": o_name, "Other Contact Details": o_details,
                "Current Brand": curr_b, "Bottle Type": b_type, "Acquisition Cost (Excl GST)": acq_c, "Monthly Volume (Bottles)": m_vol, "Competitor Contract Expiry": expiry,
                "Proposed APA SKU": prop_sku, "Sample Delivery Date": sample_date, "Agreed Margin %": margin, "Credit Terms": credit, "Lead Source": lead_src,
                "Salesperson Name": salesperson, "Lead Status": status, "Last Contacted": datetime.now().strftime("%Y-%m-%d %H:%M"), "Interaction Summary": notes, "Next Follow-up": next_f
            })
            if selected_rest != "-- Create New Blank Lead --": 
                df = df[df["Restaurant Name"] != selected_rest]
            df = pd.concat([df, pd.DataFrame([form_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Successfully saved and updated entry for '{r_name}'!")
            st.rerun()

# ==================== TAB 3 ====================
with tab3:
    st.subheader("Bulk Import Google Maps / Zomato Scraped Data")
    if not is_manager: st.warning("🔒 Bulk importing via CSV is restricted to Managers.")

# ==================== TAB 4 ====================
with tab4:
    st.subheader("🔍 Live Google Places New V2 Harvester")
    st.markdown("Integrates deep semantic payloads via the specialized Google Map Places (New V2) endpoints.")
    
    saved_key = st.secrets.get("RAPIDAPI_KEY", "")
    if saved_key:
        st.success("🔒 System Key Found & Locked Automatically from workspace storage.")
        active_key = saved_key
    else:
        active_key = st.text_input("🔑 Enter Your RapidAPI Key", type="password")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: city_selected = st.selectbox("Target City Location", list(CITY_AREA_MAP.keys()))
    with col_s2: area_selected = st.selectbox("Micro-Neighborhood Cluster", CITY_AREA_MAP[city_selected])
        
    target_count = st.slider("Target extraction count", min_value=5, max_value=20, value=10, step=5)

    if st.button("🚀 Harvest and Sync Map Locations"):
        if not active_key:
            st.error("Please supply a valid key variable to execute search loops.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("Delivering all-inclusive layout structural payloads to V2 data nodes...")
            progress_bar.progress(30)
            
            scraped_results = get_places_new_v2_leads(active_key, city_selected, area_selected, target_count)
            progress_bar.progress(70)
            
            new_leads_added = 0
            if scraped_results:
                scraped_data = []
                for item in scraped_results:
                    clean_name = item["Restaurant Name"].strip()
                    if clean_name not in df["Restaurant Name"].dropna().values:
                        entry = {col: "" for col in ALL_COLUMNS}
                        entry.update(item)
                        scraped_data.append(entry)
                        new_leads_added += 1
                        
                if scraped_data:
                    df = pd.concat([df, pd.DataFrame(scraped_data)], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    progress_bar.progress(100)
                    st.success(f"Success! Imported {new_leads_added} brand new un-restricted food & beverage listings perfectly.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    progress_bar.progress(100)
                    st.warning("All returned food asset listings for this cluster already exist in your system database.")
            else:
                progress_bar.progress(100)
                st.error("Zero records parsed. Verify your billing authorization status on the RapidAPI panel dashboard.")
            status_text.empty()