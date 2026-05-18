import streamlit as st
import pandas as pd
import os
import time
import requests
import pydeck as pdk
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode
from streamlit_gsheets import GSheetsConnection

if "RAPIDAPI_KEY" in st.secrets:
    os.environ["RAPIDAPI_KEY"] = st.secrets["RAPIDAPI_KEY"]

st.set_page_config(page_title="APA CRM - Sales Portal", layout="wide", page_icon="💧")

# Establish live connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

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

PRICE_LEVEL_MAP = {
    "PRICE_LEVEL_FREE":           "₹",
    "PRICE_LEVEL_INEXPENSIVE":    "₹",
    "PRICE_LEVEL_MODERATE":       "₹₹",
    "PRICE_LEVEL_EXPENSIVE":      "₹₹₹",
    "PRICE_LEVEL_VERY_EXPENSIVE": "₹₹₹₹",
}

# --- NEIGHBORHOOD COORDINATE CONFIGURATIONS ---
NEIGHBORHOOD_CONFIG = {
    "Ameerpet": {"lat": 17.4375, "lng": 78.4482}, "Begumpet": {"lat": 17.4447, "lng": 78.4664},
    "SR Nagar": {"lat": 17.4431, "lng": 78.4410}, "Prakash Nagar": {"lat": 17.4442, "lng": 78.4740},
    "Punjagutta": {"lat": 17.4261, "lng": 78.4534}, "Balkampet": {"lat": 17.4478, "lng": 78.4452},
    "Madhura Nagar": {"lat": 17.4395, "lng": 78.4350}, "Rasoolpura": {"lat": 17.4491, "lng": 78.4836},
    "Sanathnagar": {"lat": 17.4566, "lng": 78.4312}, "Bharat Nagar": {"lat": 17.4645, "lng": 78.4208},
    "Erragadda": {"lat": 17.4580, "lng": 78.4230}, "Borabanda": {"lat": 17.4611, "lng": 78.3976},
    "Moti Nagar": {"lat": 17.4608, "lng": 78.4102}, "Nehru Nagar": {"lat": 17.4495, "lng": 78.4582},
    "Khairatabad": {"lat": 17.4124, "lng": 78.4617}, "Somajiguda": {"lat": 17.4251, "lng": 78.4595},
    "Raj Bhavan Road": {"lat": 17.4215, "lng": 78.4602}, "Lakdikapool": {"lat": 17.4045, "lng": 78.4651},
    "Saifabad": {"lat": 17.4089, "lng": 78.4682}, "A.C. Guards": {"lat": 17.4012, "lng": 78.4585},
    "Masab Tank": {"lat": 17.4018, "lng": 78.4522}, "Chintal Basti": {"lat": 17.4105, "lng": 78.4542},
    "Musheerabad": {"lat": 17.4184, "lng": 78.4912}, "Chikkadpally": {"lat": 17.4069, "lng": 78.4897},
    "Himayatnagar": {"lat": 17.3995, "lng": 78.4842}, "Ashok Nagar": {"lat": 17.4102, "lng": 78.4862},
    "Domalguda": {"lat": 17.4022, "lng": 78.4805}, "Hyderguda": {"lat": 17.3942, "lng": 78.4795},
    "Ramnagar": {"lat": 17.4208, "lng": 78.5028}, "Azamabad": {"lat": 17.4162, "lng": 78.4975},
    "Adikmet": {"lat": 17.4144, "lng": 78.5140}, "Nallakunta": {"lat": 17.3989, "lng": 78.5052},
    "Shanker Mutt": {"lat": 17.4008, "lng": 78.5012}, "RTC X Roads": {"lat": 17.4084, "lng": 78.4939},
    "Vidyanagar": {"lat": 17.3945, "lng": 78.5152}, "Narayanguda": {"lat": 17.3967, "lng": 78.4876},
    "Gachibowli": {"lat": 17.4401, "lng": 78.3489}, "HITEC City": {"lat": 17.4483, "lng": 78.3741},
    "Madhapur": {"lat": 17.4486, "lng": 78.3908}, "Kondapur": {"lat": 17.4622, "lng": 78.3568},
    "Jubilee Hills": {"lat": 17.4325, "lng": 78.4070}, "Banjara Hills": {"lat": 17.4176, "lng": 78.4347},
    "Colaba": {"lat": 18.9067, "lng": 72.8147}, "Lower Parel": {"lat": 18.9953, "lng": 72.8300},
    "Bandra West": {"lat": 19.0600, "lng": 72.8338}, "Juhu": {"lat": 19.0985, "lng": 72.8265},
    "Andheri West": {"lat": 19.1197, "lng": 72.8464}, "Powai": {"lat": 19.1176, "lng": 72.9060},
    "Connaught Place": {"lat": 28.6315, "lng": 77.2167}, "Khan Market": {"lat": 28.5993, "lng": 77.2271},
    "DLF Phase 3 / CyberHub": {"lat": 28.4952, "lng": 77.0888}, "Indiranagar": {"lat": 12.9784, "lng": 77.6408}
}

CITY_AREA_MAP = {
    "Hyderabad": ["Jubilee Hills", "Banjara Hills", "Gachibowli", "HITEC City", "Madhapur", "Kondapur", "Ameerpet", "Begumpet", "Punjagutta", "Somajiguda"],
    "Mumbai / Greater Mumbai": ["Colaba", "Lower Parel", "Bandra West", "Juhu", "Andheri West", "Powai"],
    "Delhi": ["Connaught Place", "Khan Market"],
    "Gurgaon": ["DLF Phase 3 / CyberHub"],
    "Bengaluru": ["Indiranagar"]
}

# Fill missing map configurations dynamically with safe center coordinates if not explicitly mapped
for city, areas in CITY_AREA_MAP.items():
    for area in areas:
        if area not in NEIGHBORHOOD_CONFIG:
            NEIGHBORHOOD_CONFIG[area] = {"lat": 17.4325, "lng": 78.4070}

MANAGER_PASSWORD = "APA@2024"

FNB_ALL_TYPES = [
    "restaurant", "cafe", "bar", "bakery", "coffee_shop", "fast_food_restaurant", "pub", "night_club", 
    "food_court", "meal_delivery", "meal_takeaway", "wine_bar", "cocktail_bar", "sports_bar", "lounge_bar"
]
TYPE_PRIORITY = ["restaurant", "cafe", "bar", "coffee_shop", "bakery"]
GRID_OFFSETS = [-0.022, 0.022]  # Streamlined grid to optimize token limitations 
CELL_RADIUS  = 2000.0
MAX_PAGES    = 2

# ── Data Core Engine ──────────────────────────────────────────────────────────

def load_data():
    """Pulls fresh master pipeline records from the live Google Sheet."""
    try:
        df_sheet = conn.read(worksheet="Leads", ttl=0)
        for col in ALL_COLUMNS:
            if col not in df_sheet.columns:
                df_sheet[col] = ""
        return df_sheet
    except Exception as e:
        st.error(f"⚠️ Google Sheets Connection Failure: {e}")
        return pd.DataFrame(columns=ALL_COLUMNS)

def parse_coordinate(value, field_name):
    if value == "" or value is None:
        return None, None
    try:
        return float(value), None
    except (ValueError, TypeError):
        return None, f"⚠️ Invalid {field_name} format."

def _paginate_cell(api_key, headers, node_lat, node_lng, node_label):
    url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:searchNearby"
    payload = {
        "includedTypes": FNB_ALL_TYPES,
        "maxResultCount": 20,
        "rankPreference": "DISTANCE",
        "locationRestriction": {"circle": {"center": {"latitude": node_lat, "longitude": node_lng}, "radius": CELL_RADIUS}},
        "languageCode": "en"
    }
    cell_places = []
    page = 0
    while page < MAX_PAGES:
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code != 200:
                break
            data = resp.json()
            places = data.get("places", [])
            next_token = data.get("nextPageToken")
            cell_places.extend(places)
            page += 1
            if not next_token or len(places) < 20:
                break
            payload = {"pageToken": next_token}
            time.sleep(0.5)
        except Exception:
            break
    return cell_places

def execute_4x4_paginated_grid_sweep(api_key, city, area):
    if area not in NEIGHBORHOOD_CONFIG:
        st.error(f"No config found for '{area}'.")
        return []

    cfg = NEIGHBORHOOD_CONFIG[area]
    nodes = [{"lat": cfg["lat"] + lat_off, "lng": cfg["lng"] + lng_off, "label": f"({lat_off:.3f},{lng_off:.3f})"} 
             for lat_off in GRID_OFFSETS for lng_off in GRID_OFFSETS]

    headers = {
        "content-type": "application/json",
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.priceLevel,places.types,places.websiteUri,places.nationalPhoneNumber",
        "x-rapidapi-host": "google-map-places-new-v2.p.rapidapi.com",
        "x-rapidapi-key":  api_key
    }

    seen_ids = set()
    all_places = []
    status_box = st.empty()
    
    for i, node in enumerate(nodes):
        status_box.markdown(f"🛰️ **Grid Crawler:** Active on node `{i+1}/{len(nodes)}`...")
        for place in _paginate_cell(api_key, headers, node["lat"], node["lng"], node["label"]):
            pid = place.get("id", "")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                all_places.append(place)
        time.sleep(0.2)

    status_box.empty()
    leads = []
    for place in all_places:
        name = place.get("displayName", {}).get("text", "F&B Venue")
        address = place.get("formattedAddress", f"{area}, {city}")
        loc = place.get("location", {})
        pid = place.get("id", "")

        leads.append({
            "Restaurant Name":  name,
            "Cuisine/Type":     next((t.replace("_", " ").title() for t in TYPE_PRIORITY if t in place.get("types", [])), "Food Space"),
            "Zone/Area":        area,
            "Address":          address,
            "Latitude":         float(loc.get("latitude", "")) if loc.get("latitude") else "",
            "Longitude":        float(loc.get("longitude", "")) if loc.get("longitude") else "",
            "Map Link":         f"https://www.google.com/maps/place/?q=place_id:{pid}" if pid else "",
            "Website":          place.get("websiteUri", ""),
            "Restaurant Phone": place.get("nationalPhoneNumber", ""),
            "Google Rating":    str(place.get("rating", "")),
            "Total Reviews":    str(place.get("userRatingCount", "")),
            "Price Segment":    PRICE_LEVEL_MAP.get(place.get("priceLevel", ""), ""),
            "Lead Source":      "Google Maps V2 — Cloud Sweep",
            "Lead Status":      "Cold Lead",
            "Last Contacted":   datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    return leads

# ── Main Application Render ──────────────────────────────────────────────────

df = load_data()

st.sidebar.markdown("### 🔐 Admin Controls")
user_password = st.sidebar.text_input("Enter Manager Password", type="password")
is_manager    = (user_password == MANAGER_PASSWORD)

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Pipeline Dashboard", "⚡ Quick Update / New Lead",
    "📥 Bulk Import CSV",    "🔍 Real-Time Lead Generator"
])

# ── Tab 1: Dashboard View ─────────────────────────────────────────────────────
with tab1:
    st.subheader("Current Pipeline")
    if df.empty:
        st.info("No active records found in the spreadsheet. Run the generator on Tab 4.")
    else:
        if is_manager:
            st.download_button(
                "📥 Export Full CRM Database to CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"apa_pipeline_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_query = st.text_input("🔍 Search by Establishment Name")
        with col_f2:
            zone_filter = st.multiselect("Filter by Zone/Area", options=list(df["Zone/Area"].dropna().unique()))

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["Restaurant Name"].str.contains(search_query, case=False, na=False)]
        if zone_filter:
            filtered_df = filtered_df[filtered_df["Zone/Area"].isin(zone_filter)]

        display_df = filtered_df.copy()
        if not is_manager:
            for col in ["Acquisition Cost (Excl GST)", "Agreed Margin %", "Monthly Volume (Bottles)"]:
                if col in display_df.columns:
                    display_df[col] = "🔒 Restricted"

        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_default_column(filter=True, sortable=True, resizable=True, floatingFilter=True, minWidth=100)
        gb.configure_column("Restaurant Name", pinned="left", minWidth=200, filter="agTextColumnFilter")
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)
        grid_opts = gb.build()

        AgGrid(display_df, gridOptions=grid_opts, update_mode=GridUpdateMode.NO_UPDATE, 
               columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, theme="streamlit", height=400, use_container_width=True)

        # PyDeck Geopoint Visualization Map
        map_df = filtered_df[["Restaurant Name", "Cuisine/Type", "Zone/Area", "Latitude", "Longitude"]].copy()
        map_df["latitude"]  = pd.to_numeric(map_df["Latitude"],  errors="coerce")
        map_df["longitude"] = pd.to_numeric(map_df["Longitude"], errors="coerce")
        map_df = map_df.dropna(subset=["latitude", "longitude"])

        if not map_df.empty:
            view = pdk.ViewState(latitude=map_df["latitude"].median(), longitude=map_df["longitude"].median(), zoom=11)
            layer = pdk.Layer("ScatterplotLayer", data=map_df, get_position="[longitude, latitude]", get_color="[0, 150, 255, 180]", get_radius=180, pickable=True)
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"text": "{Restaurant Name} - {Zone/Area}"}))

# ── Tab 2: Manual Update Entry ────────────────────────────────────────────────
with tab2:
    st.subheader("Sales Rep Log Entry & Deletion Portal")
    existing = ["-- Create New Blank Lead --"] + list(df["Restaurant Name"].dropna().unique())
    selected_rest = st.selectbox("Select Restaurant (or create new):", existing)

    defaults = {col: "" for col in ALL_COLUMNS}
    if selected_rest != "-- Create New Blank Lead --":
        row = df[df["Restaurant Name"] == selected_rest].iloc[0]
        for col in ALL_COLUMNS:
            defaults[col] = row[col] if pd.notna(row[col]) else ""

    if selected_rest != "-- Create New Blank Lead --" and is_manager:
        if st.button("❌ Delete This Entry From CRM"):
            df = df[df["Restaurant Name"] != selected_rest]
            conn.update(worksheet="Leads", data=df)
            st.warning(f"Deleted '{selected_rest}' from Google Sheets.")
            time.sleep(1)
            st.rerun()

    with st.form("crm_entry_form", clear_on_submit=True):
        r_name  = st.text_input("Restaurant Name *", value=defaults["Restaurant Name"])
        c_name  = st.text_input("Company / Parent Group", value=defaults["Company Name"])
        cuisine = st.text_input("Cuisine / Type", value=defaults["Cuisine/Type"])
        zone    = st.text_input("Zone / Area", value=defaults["Zone/Area"])
        address = st.text_area("Address", value=defaults["Address"])
        web     = st.text_input("Website", value=defaults["Website"])
        r_phone = st.text_input("Restaurant Phone", value=defaults["Restaurant Phone"])
        rating  = st.text_input("Google Rating", value=str(defaults["Google Rating"]))
        map_l   = st.text_input("Google Maps Link", value=defaults["Map Link"])
        lat_in  = st.text_input("Latitude", value=str(defaults["Latitude"]))
        lon_in  = st.text_input("Longitude", value=str(defaults["Longitude"]))
        
        # Internal Pipeline Metrics
        curr_b   = st.text_input("Current Water Brand", value=defaults["Current Brand"])
        b_type   = st.text_input("Bottle Type", value=defaults["Bottle Type"])
        acq_c    = st.text_input("Acquisition Cost", value=str(defaults["Acquisition Cost (Excl GST)"]))
        m_vol    = st.text_input("Monthly Volume", value=str(defaults["Monthly Volume (Bottles)"]))
        prop_sku = st.text_input("Proposed APA SKU", value=defaults["Proposed APA SKU"])
        status   = st.selectbox("Lead Status", ["Cold Lead", "Warm Lead", "Sample Dropped", "Negotiation", "Active Client"], index=0)
        notes    = st.text_area("Interaction Notes", value=defaults["Interaction Summary"])

        if st.form_submit_button("💾 Save & Update Lead") and r_name:
            lat_val, _ = parse_coordinate(lat_in.strip(), "Latitude")
            lon_val, _ = parse_coordinate(lon_in.strip(), "Longitude")

            form_entry = {
                "Restaurant Name": r_name, "Company Name": c_name, "Cuisine/Type": cuisine, "Zone/Area": zone, "Address": address,
                "Website": web, "Restaurant Phone": r_phone, "Google Rating": rating, "Map Link": map_l,
                "Latitude": lat_val if lat_val else "", "Longitude": lon_val if lon_val else "",
                "Current Brand": curr_b, "Bottle Type": b_type, "Acquisition Cost (Excl GST)": acq_c, "Monthly Volume (Bottles)": m_vol,
                "Proposed APA SKU": prop_sku, "Lead Source": "Manual Entry", "Lead Status": status,
                "Last Contacted": datetime.now().strftime("%Y-%m-%d %H:%M"), "Interaction Summary": notes
            }
            if selected_rest != "-- Create New Blank Lead --":
                df = df[df["Restaurant Name"] != selected_rest]
            df = pd.concat([df, pd.DataFrame([form_entry])], ignore_index=True)
            
            conn.update(worksheet="Leads", data=df)
            st.success(f"Saved '{r_name}' permanently to Google Sheets!")
            time.sleep(1)
            st.rerun()

# ── Tab 3: Bulk CSV Importer ──────────────────────────────────────────────────
with tab3:
    st.subheader("📥 Bulk Import External Scraped Leads")
    uploaded_file = st.file_uploader("Upload CSV Pipeline", type=["csv"])
    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)
            if "Restaurant Name" not in import_df.columns:
                st.error("Invalid schema format: Missing 'Restaurant Name' header.")
            else:
                if st.button("⚡ Execute Bulk Append"):
                    imported_records = []
                    for _, row in import_df.iterrows():
                        if str(row["Restaurant Name"]).strip() not in df["Restaurant Name"].dropna().values:
                            entry = {col: "" for col in ALL_COLUMNS}
                            for col in import_df.columns:
                                if col in ALL_COLUMNS:
                                    entry[col] = row[col]
                            imported_records.append(entry)
                    if imported_records:
                        df = pd.concat([df, pd.DataFrame(imported_records)], ignore_index=True)
                        conn.update(worksheet="Leads", data=df)
                        st.success(f"Appended {len(imported_records)} records straight to Google Sheets.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("All entries within this file match existing records in the CRM database.")
        except Exception as e:
            st.error(f"File validation failure: {e}")

# ── Tab 4: 16-Node Grid Harvester ─────────────────────────────────────────────
with tab4:
    st.subheader("🔍 Industrial Deep Grid Harvester")
    city_selected = st.selectbox("Target City", list(CITY_AREA_MAP.keys()))
    area_selected = st.selectbox("Neighbourhood Sector", CITY_AREA_MAP[city_selected])

    if st.button("🚀 Execute 16-Node Grid Crawl"):
        active_key = st.secrets.get("RAPIDAPI_KEY", "")
        if not active_key:
            st.error("Missing RAPIDAPI_KEY within application secrets configuration parameters.")
        else:
            scraped_results = execute_4x4_paginated_grid_sweep(active_key, city_selected, area_selected)
            if scraped_results:
                existing_names = df["Restaurant Name"].dropna().values
                new_rows = []
                for item in scraped_results:
                    if item["Restaurant Name"].strip() not in existing_names:
                        entry = {col: "" for col in ALL_COLUMNS}
                        entry.update(item)
                        new_rows.append(entry)
                if new_rows:
                    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                    conn.update(worksheet="Leads", data=df)
                    st.success(f"✅ Imported **{len(new_rows)}** fresh leads straight to your Google Sheet rows!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("All records recovered in this sweep sector already reside in your database tracker framework.")
            else:
                st.error("Crawler pipeline yielded zero properties. Verify API subscriptions or target nodes maps config parameters.")