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

# Centre coordinates only. Grid cells are computed dynamically.
NEIGHBORHOOD_CONFIG = {
    # --- HYDERABAD ---
    "Ameerpet":                    {"lat": 17.4375, "lng": 78.4482},
    "Begumpet":                    {"lat": 17.4447, "lng": 78.4664},
    "SR Nagar":                    {"lat": 17.4431, "lng": 78.4410},
    "Prakash Nagar":               {"lat": 17.4442, "lng": 78.4740},
    "Punjagutta":                  {"lat": 17.4261, "lng": 78.4534},
    "Balkampet":                   {"lat": 17.4478, "lng": 78.4452},
    "Madhura Nagar":               {"lat": 17.4395, "lng": 78.4350},
    "Rasoolpura":                  {"lat": 17.4491, "lng": 78.4836},
    "Sanathnagar":                 {"lat": 17.4566, "lng": 78.4312},
    "Bharat Nagar":                {"lat": 17.4645, "lng": 78.4208},
    "Erragadda":                   {"lat": 17.4580, "lng": 78.4230},
    "Borabanda":                   {"lat": 17.4611, "lng": 78.3976},
    "Moti Nagar":                  {"lat": 17.4608, "lng": 78.4102},
    "Nehru Nagar":                 {"lat": 17.4495, "lng": 78.4582},
    "Khairatabad":                 {"lat": 17.4124, "lng": 78.4617},
    "Somajiguda":                  {"lat": 17.4251, "lng": 78.4595},
    "Raj Bhavan Road":             {"lat": 17.4215, "lng": 78.4602},
    "Lakdikapool":                 {"lat": 17.4045, "lng": 78.4651},
    "Saifabad":                    {"lat": 17.4089, "lng": 78.4682},
    "A.C. Guards":                 {"lat": 17.4012, "lng": 78.4585},
    "Masab Tank":                  {"lat": 17.4018, "lng": 78.4522},
    "Chintal Basti":               {"lat": 17.4105, "lng": 78.4542},
    "Musheerabad":                 {"lat": 17.4184, "lng": 78.4912},
    "Chikkadpally":                {"lat": 17.4069, "lng": 78.4897},
    "Himayatnagar":                {"lat": 17.3995, "lng": 78.4842},
    "Ashok Nagar":                 {"lat": 17.4102, "lng": 78.4862},
    "Domalguda":                   {"lat": 17.4022, "lng": 78.4805},
    "Hyderguda":                   {"lat": 17.3942, "lng": 78.4795},
    "Ramnagar":                    {"lat": 17.4208, "lng": 78.5028},
    "Azamabad":                    {"lat": 17.4162, "lng": 78.4975},
    "Adikmet":                     {"lat": 17.4144, "lng": 78.5140},
    "Nallakunta":                  {"lat": 17.3989, "lng": 78.5052},
    "Shanker Mutt":                {"lat": 17.4008, "lng": 78.5012},
    "RTC X Roads":                 {"lat": 17.4084, "lng": 78.4939},
    "Vidyanagar":                  {"lat": 17.3945, "lng": 78.5152},
    "Narayanguda":                 {"lat": 17.3967, "lng": 78.4876},
    "Durgabai Deshmukh Colony":    {"lat": 17.4215, "lng": 78.5202},
    "Central Excise Colony":       {"lat": 17.3931, "lng": 78.5010},
    "Amberpet":                    {"lat": 17.3854, "lng": 78.5244},
    "Tilaknagar":                  {"lat": 17.3895, "lng": 78.5112},
    "Golnaka":                     {"lat": 17.3789, "lng": 78.5195},
    "Barkatpura":                  {"lat": 17.3924, "lng": 78.4962},
    "Shivam Road":                 {"lat": 17.3905, "lng": 78.5202},
    "Jamia Osmania":               {"lat": 17.4168, "lng": 78.5192},
    "Kachiguda":                   {"lat": 17.3840, "lng": 78.4918},
    "Badichowdi":                  {"lat": 17.3878, "lng": 78.4862},
    "Nampally":                    {"lat": 17.3926, "lng": 78.4674},
    "Abids":                       {"lat": 17.3904, "lng": 78.4731},
    "Aghapura":                    {"lat": 17.3881, "lng": 78.4592},
    "Koti":                        {"lat": 17.3833, "lng": 78.4812},
    "Bank Street":                 {"lat": 17.3852, "lng": 78.4802},
    "Boggulkunta":                 {"lat": 17.3912, "lng": 78.4822},
    "Mehdipatnam":                 {"lat": 17.3916, "lng": 78.4326},
    "Karwan":                      {"lat": 17.3785, "lng": 78.4285},
    "Secunderabad":                {"lat": 17.4399, "lng": 78.4983},
    "Chilkalguda":                 {"lat": 17.4322, "lng": 78.5105},
    "Kavadiguda":                  {"lat": 17.4195, "lng": 78.4862},
    "MG Road (James Street)":      {"lat": 17.4344, "lng": 78.4901},
    "Minister Road":               {"lat": 17.4431, "lng": 78.4831},
    "Mylargadda":                  {"lat": 17.4352, "lng": 78.5142},
    "Namalagundu":                 {"lat": 17.4305, "lng": 78.5205},
    "Padmarao Nagar":              {"lat": 17.4278, "lng": 78.5095},
    "Pan Bazar":                   {"lat": 17.4355, "lng": 78.4930},
    "Paradise Circle":             {"lat": 17.4434, "lng": 78.4867},
    "Parsigutta":                  {"lat": 17.4231, "lng": 78.5135},
    "Patny":                       {"lat": 17.4415, "lng": 78.4935},
    "Rani Gunj":                   {"lat": 17.4331, "lng": 78.4852},
    "RP Road":                     {"lat": 17.4362, "lng": 78.4945},
    "Sindhi Colony":               {"lat": 17.4476, "lng": 78.4792},
    "Sitaphalmandi":               {"lat": 17.4262, "lng": 78.5235},
    "Tarnaka":                     {"lat": 17.4294, "lng": 78.5379},
    "Warsiguda":                   {"lat": 17.4215, "lng": 78.5285},
    "Addagutta":                   {"lat": 17.4542, "lng": 78.4652},
    "Tukaramgate":                 {"lat": 17.4368, "lng": 78.5052},
    "Kalasiguda":                  {"lat": 17.4285, "lng": 78.4982},
    "Secunderabad Cantonment":     {"lat": 17.4459, "lng": 78.5102},
    "Bowenpally":                  {"lat": 17.4721, "lng": 78.4722},
    "Karkhana":                    {"lat": 17.4565, "lng": 78.4922},
    "Marredpally":                 {"lat": 17.4484, "lng": 78.5085},
    "Sikh Village":                {"lat": 17.4642, "lng": 78.4885},
    "Trimulgherry":                {"lat": 17.4735, "lng": 78.5022},
    "Vikrampuri":                  {"lat": 17.4589, "lng": 78.4985},
    "Gachibowli":                  {"lat": 17.4401, "lng": 78.3489},
    "Gowlidoddi":                  {"lat": 17.4202, "lng": 78.3364},
    "Nanakramguda":                {"lat": 17.4172, "lng": 78.3556},
    "HITEC City":                  {"lat": 17.4483, "lng": 78.3741},
    "Madhapur":                    {"lat": 17.4486, "lng": 78.3908},
    "Kondapur":                    {"lat": 17.4622, "lng": 78.3568},
    "Kothaguda":                   {"lat": 17.4585, "lng": 78.3644},
    "Kokapet":                     {"lat": 17.4005, "lng": 78.3278},
    "Narsingi":                    {"lat": 17.3912, "lng": 78.3612},
    "Jubilee Hills":               {"lat": 17.4325, "lng": 78.4070},
    "Banjara Hills":               {"lat": 17.4176, "lng": 78.4347},
    "Film Nagar":                  {"lat": 17.4121, "lng": 78.4011},
    "Yousufguda":                  {"lat": 17.4366, "lng": 78.4282},
    "Srinagar Colony":             {"lat": 17.4374, "lng": 78.4433},
    "Serilingampally":             {"lat": 17.4831, "lng": 78.3252},
    "Chanda Nagar":                {"lat": 17.4931, "lng": 78.3262},
    "Allwyn Colony":               {"lat": 17.4982, "lng": 78.3452},
    "Hafeezpet":                   {"lat": 17.4822, "lng": 78.3652},
    "Madinaguda":                  {"lat": 17.5012, "lng": 78.3422},
    "Miyapur":                     {"lat": 17.4965, "lng": 78.3412},
    "Maktha Mahaboobpet":          {"lat": 17.5052, "lng": 78.3512},
    "Kukatpally":                  {"lat": 17.4852, "lng": 78.3986},
    "Bachupally":                  {"lat": 17.5282, "lng": 78.3852},
    "KPHB Colony":                 {"lat": 17.4844, "lng": 78.3889},
    "Nizampet":                    {"lat": 17.5142, "lng": 78.3842},
    "Pragathi Nagar":              {"lat": 17.5012, "lng": 78.4052},
    "Moosapet":                    {"lat": 17.4752, "lng": 78.4122},
    "Mallampet":                   {"lat": 17.5412, "lng": 78.3652},
    "Patancheru":                  {"lat": 17.5282, "lng": 78.2652},
    "BHEL Township":               {"lat": 17.5022, "lng": 78.2852},
    "RC Puram":                    {"lat": 17.5142, "lng": 78.2952},
    "Ameenpur":                    {"lat": 17.5312, "lng": 78.3152},
    "Beeramguda":                  {"lat": 17.5252, "lng": 78.3252},
    "Kistareddypet":               {"lat": 17.5152, "lng": 78.2752},
    "IDA Bollaram":                {"lat": 17.5312, "lng": 78.2552},
    "Medical Devices Park":        {"lat": 17.5222, "lng": 78.2652},
    "Afzal Gunj":                  {"lat": 17.3842, "lng": 78.4612},
    "Aliabad":                     {"lat": 17.3752, "lng": 78.4782},
    "Alijah Kotla":                {"lat": 17.3832, "lng": 78.4732},
    "Asif Nagar":                  {"lat": 17.3752, "lng": 78.4412},
    "Azampura":                    {"lat": 17.3652, "lng": 78.4952},
    "Barkas":                      {"lat": 17.3452, "lng": 78.5152},
    "Bazarghat":                   {"lat": 17.3732, "lng": 78.4712},
    "Begum Bazaar":                {"lat": 17.3892, "lng": 78.4642},
    "Chaderghat":                  {"lat": 17.3752, "lng": 78.4852},
    "Chanchalguda":                {"lat": 17.3682, "lng": 78.4852},
    "Chandrayan Gutta":            {"lat": 17.3482, "lng": 78.5052},
    "Chatta Bazaar":               {"lat": 17.3622, "lng": 78.4752},
    "Dabirpura":                   {"lat": 17.3782, "lng": 78.4882},
    "Dar-ul-Shifa":                {"lat": 17.3742, "lng": 78.4792},
    "Dhoolpet":                    {"lat": 17.3822, "lng": 78.4502},
    "Edi Bazar":                   {"lat": 17.3652, "lng": 78.4702},
    "Falaknuma":                   {"lat": 17.3252, "lng": 78.4852},
    "Malakpet":                    {"lat": 17.3682, "lng": 78.5012},
    "Moghalpura":                  {"lat": 17.3742, "lng": 78.4652},
    "Jahanuma":                    {"lat": 17.3412, "lng": 78.4752},
    "Laad Bazaar":                 {"lat": 17.3612, "lng": 78.4742},
    "Lal Darwaza":                 {"lat": 17.3622, "lng": 78.4762},
    "Langar Houz":                 {"lat": 17.3412, "lng": 78.4612},
    "Madina":                      {"lat": 17.3622, "lng": 78.4682},
    "Maharajgunj":                 {"lat": 17.3752, "lng": 78.4822},
    "Mehboob ki Mehendi":          {"lat": 17.3832, "lng": 78.4762},
    "Mir Alam Tank":               {"lat": 17.3532, "lng": 78.4752},
    "Mozamjahi Market":            {"lat": 17.3822, "lng": 78.4712},
    "Nawab Saheb Kunta":           {"lat": 17.3452, "lng": 78.4852},
    "Nayapul":                     {"lat": 17.3782, "lng": 78.4672},
    "Noorkhan Bazar":              {"lat": 17.3742, "lng": 78.4752},
    "Pisal Banda":                 {"lat": 17.3452, "lng": 78.4952},
    "Purana Pul":                  {"lat": 17.3762, "lng": 78.4712},
    "Putlibowli":                  {"lat": 17.3862, "lng": 78.4642},
    "Rein Bazar":                  {"lat": 17.3722, "lng": 78.4752},
    "Santoshnagar":                {"lat": 17.3452, "lng": 78.5052},
    "Shahran Market":              {"lat": 17.3642, "lng": 78.4712},
    "Shah Ali Banda":              {"lat": 17.3752, "lng": 78.4822},
    "Sultan Bazar":                {"lat": 17.3832, "lng": 78.4762},
    "Udden Gadda":                 {"lat": 17.3652, "lng": 78.4862},
    "Uppuguda":                    {"lat": 17.3732, "lng": 78.4882},
    "Yakutpura":                   {"lat": 17.3552, "lng": 78.4952},
    "Owaiy Colony":                {"lat": 17.3612, "lng": 78.4852},
    "Kareemuddin House":           {"lat": 17.3682, "lng": 78.4782},
    "Balanagar":                   {"lat": 17.4752, "lng": 78.4412},
    "Fateh Nagar":                 {"lat": 17.4652, "lng": 78.4302},
    "Ferozguda":                   {"lat": 17.4822, "lng": 78.4562},
    "Old Bowenpally":              {"lat": 17.4682, "lng": 78.4852},
    "Hasmathpet":                  {"lat": 17.4752, "lng": 78.4882},
    "Suchitra Center":             {"lat": 17.5082, "lng": 78.4652},
    "Quthbullapur":                {"lat": 17.5152, "lng": 78.4352},
    "Jeedimetla":                  {"lat": 17.4922, "lng": 78.4352},
    "Jagadgirigutta":              {"lat": 17.5072, "lng": 78.4452},
    "Suraram":                     {"lat": 17.5212, "lng": 78.4552},
    "Pet Basheerabad":             {"lat": 17.5312, "lng": 78.4952},
    "Kompally":                    {"lat": 17.5449, "lng": 78.4754},
    "Maisammaguda":                {"lat": 17.5152, "lng": 78.5052},
    "Medchal":                     {"lat": 17.6312, "lng": 78.5352},
    "Kandlakoya":                  {"lat": 17.5852, "lng": 78.5252},
    "Alwal":                       {"lat": 17.5022, "lng": 78.5012},
    "Lothkunta":                   {"lat": 17.5212, "lng": 78.4952},
    "Old Alwal":                   {"lat": 17.5052, "lng": 78.5082},
    "Macha Bollaram":              {"lat": 17.5352, "lng": 78.4452},
    "Venkatapuram":                {"lat": 17.5122, "lng": 78.5152},
    "Shamirpet":                   {"lat": 17.5852, "lng": 78.5552},
    "Malkajgiri":                  {"lat": 17.4522, "lng": 78.5312},
    "Anandbagh":                   {"lat": 17.4452, "lng": 78.5452},
    "Ammuguda":                    {"lat": 17.4622, "lng": 78.5352},
    "Gautham Nagar":               {"lat": 17.4552, "lng": 78.5252},
    "Kakatiya Nagar":              {"lat": 17.4652, "lng": 78.5452},
    "Vinayak Nagar":               {"lat": 17.4382, "lng": 78.5452},
    "Moula-Ali":                   {"lat": 17.4252, "lng": 78.5552},
    "Neredmet":                    {"lat": 17.4682, "lng": 78.5352},
    "Old Neredmet":                {"lat": 17.4622, "lng": 78.5452},
    "Safilguda":                   {"lat": 17.4552, "lng": 78.5182},
    "Sainikpuri":                  {"lat": 17.4862, "lng": 78.5412},
    "Yapral":                      {"lat": 17.5052, "lng": 78.5512},
    "Kapra":                       {"lat": 17.4752, "lng": 78.5682},
    "A.S. Rao Nagar":              {"lat": 17.4622, "lng": 78.5752},
    "ECIL X-Roads":                {"lat": 17.4552, "lng": 78.5652},
    "Kamala Nagar":                {"lat": 17.4452, "lng": 78.5552},
    "Kushaiguda":                  {"lat": 17.4152, "lng": 78.5452},
    "Cherlapally":                 {"lat": 17.4352, "lng": 78.5852},
    "Keesara":                     {"lat": 17.5052, "lng": 78.6252},
    "Nagaram":                     {"lat": 17.4452, "lng": 78.5952},
    "Dammaiguda":                  {"lat": 17.4952, "lng": 78.5652},
    "Jawaharnagar":                {"lat": 17.5252, "lng": 78.5952},
    "Rampally":                    {"lat": 17.4252, "lng": 78.6152},
    "Cheriyal":                    {"lat": 17.4052, "lng": 78.6152},
    "Uppal":                       {"lat": 17.4022, "lng": 78.5612},
    "Habsiguda":                   {"lat": 17.4092, "lng": 78.5452},
    "Ramanthapur":                 {"lat": 17.3952, "lng": 78.5752},
    "Boduppal":                    {"lat": 17.4252, "lng": 78.6052},
    "Nagole":                      {"lat": 17.3852, "lng": 78.5752},
    "Nacharam":                    {"lat": 17.4252, "lng": 78.5582},
    "Ghatkesar":                   {"lat": 17.4452, "lng": 78.6952},
    "Peerzadiguda":                {"lat": 17.4152, "lng": 78.6252},
    "Chengicherla":                {"lat": 17.4252, "lng": 78.6352},
    "Pocharam":                    {"lat": 17.4552, "lng": 78.6452},
    "Mallapur":                    {"lat": 17.4252, "lng": 78.5852},
    "Narapally":                   {"lat": 17.4352, "lng": 78.6452},
    "Medipally":                   {"lat": 17.4252, "lng": 78.6552},
    "Dilsukhnagar":                {"lat": 17.3682, "lng": 78.5252},
    "Kothapet":                    {"lat": 17.3552, "lng": 78.5252},
    "Gaddiannaram":                {"lat": 17.3552, "lng": 78.5152},
    "Moosarambagh":                {"lat": 17.3752, "lng": 78.5152},
    "Chaitanyapuri":               {"lat": 17.3652, "lng": 78.5252},
    "L.B. Nagar":                  {"lat": 17.3456, "lng": 78.5512},
    "Bairamalguda":                {"lat": 17.3352, "lng": 78.5452},
    "Chintalakunta":               {"lat": 17.3252, "lng": 78.5252},
    "Vanasthalipuram":             {"lat": 17.3352, "lng": 78.5352},
    "Hastinapuram":                {"lat": 17.3252, "lng": 78.5452},
    "Saroornagar":                 {"lat": 17.3452, "lng": 78.5252},
    "Badangpet":                   {"lat": 17.3152, "lng": 78.5052},
    "Balapur":                     {"lat": 17.3052, "lng": 78.5152},
    "Champapet":                   {"lat": 17.3452, "lng": 78.5052},
    "Jillelguda":                  {"lat": 17.3352, "lng": 78.5152},
    "Karmanghat":                  {"lat": 17.3252, "lng": 78.5152},
    "Lingojiguda":                 {"lat": 17.3652, "lng": 78.5052},
    "Meerpet":                     {"lat": 17.3352, "lng": 78.5252},
    "Sanghi Nagar":                {"lat": 17.3252, "lng": 78.5052},
    "Hayathnagar":                 {"lat": 17.3252, "lng": 78.6052},
    "Osman Nagar":                 {"lat": 17.3452, "lng": 78.6052},
    "Ibrahimpatnam":               {"lat": 17.2652, "lng": 78.6452},
    "Toli Chowki":                 {"lat": 17.4012, "lng": 78.4012},
    "Gudimalkapur":                {"lat": 17.3852, "lng": 78.4312},
    "Mallepally":                  {"lat": 17.3852, "lng": 78.4512},
    "Padmanabha Nagar Colony":     {"lat": 17.3852, "lng": 78.4212},
    "Red Hills":                   {"lat": 17.4012, "lng": 78.4212},
    "Shaikpet":                    {"lat": 17.4052, "lng": 78.4212},
    "Rajendranagar":               {"lat": 17.3552, "lng": 78.4152},
    "Attapur":                     {"lat": 17.3642, "lng": 78.4312},
    "Bandlaguda":                  {"lat": 17.3552, "lng": 78.4252},
    "Gandipet":                    {"lat": 17.3912, "lng": 78.3112},
    "Kismatpur":                   {"lat": 17.3452, "lng": 78.4052},
    "Ring Road":                   {"lat": 17.3652, "lng": 78.4012},
    "Puppalguda":                  {"lat": 17.3852, "lng": 78.3652},
    "Kotapet":                     {"lat": 17.3652, "lng": 78.3952},
    "Chevella":                    {"lat": 17.3052, "lng": 78.1452},
    "Moinabad":                    {"lat": 17.3452, "lng": 78.3252},
    "Shamshabad":                  {"lat": 17.2512, "lng": 78.4312},
    "Rajiv Gandhi International Airport": {"lat": 17.2403, "lng": 78.4294},
    "Umdanagar":                   {"lat": 17.2752, "lng": 78.4152},
    "Shadnagar":                   {"lat": 17.0652, "lng": 78.2152},
    # --- MUMBAI ---
    "Colaba":           {"lat": 18.9067, "lng": 72.8147},
    "Nariman Point":    {"lat": 18.9262, "lng": 72.8225},
    "Fort":             {"lat": 18.9322, "lng": 72.8354},
    "Churchgate":       {"lat": 18.9312, "lng": 72.8258},
    "Marine Drive":     {"lat": 18.9432, "lng": 72.8231},
    "Malabar Hill":     {"lat": 18.9543, "lng": 72.7984},
    "Breach Candy":     {"lat": 18.9742, "lng": 72.8052},
    "Grant Road":       {"lat": 18.9642, "lng": 72.8172},
    "Byculla":          {"lat": 18.9792, "lng": 72.8312},
    "Mazagaon":         {"lat": 18.9682, "lng": 72.8452},
    "Mahalaxmi":        {"lat": 18.9842, "lng": 72.8152},
    "Lower Parel":      {"lat": 18.9953, "lng": 72.8300},
    "Parel":            {"lat": 19.0022, "lng": 72.8412},
    "Dadar":            {"lat": 19.0212, "lng": 72.8422},
    "Matunga":          {"lat": 19.0322, "lng": 72.8462},
    "Sion":             {"lat": 19.0412, "lng": 72.8612},
    "Mahim":            {"lat": 19.0442, "lng": 72.8412},
    "Wadala":           {"lat": 19.0152, "lng": 72.8582},
    "Prabhadevi":       {"lat": 19.0112, "lng": 72.8252},
    "Dharavi":          {"lat": 19.0412, "lng": 72.8542},
    "Chunabhatti":      {"lat": 19.0512, "lng": 72.8692},
    "Bandra West":      {"lat": 19.0600, "lng": 72.8338},
    "Bandra East":      {"lat": 19.0625, "lng": 72.8485},
    "Khar":             {"lat": 19.0682, "lng": 72.8372},
    "Santacruz West":   {"lat": 19.0812, "lng": 72.8352},
    "Santacruz East":   {"lat": 19.0842, "lng": 72.8552},
    "Juhu":             {"lat": 19.0985, "lng": 72.8265},
    "Vile Parle West":  {"lat": 19.0972, "lng": 72.8352},
    "Vile Parle East":  {"lat": 19.1012, "lng": 72.8552},
    "Andheri West":     {"lat": 19.1197, "lng": 72.8464},
    "Andheri East":     {"lat": 19.1152, "lng": 72.8682},
    "Versova":          {"lat": 19.1302, "lng": 72.8152},
    "Jogeshwari West":  {"lat": 19.1452, "lng": 72.8352},
    "Jogeshwari East":  {"lat": 19.1422, "lng": 72.8552},
    "Goregaon West":    {"lat": 19.1622, "lng": 72.8374},
    "Goregaon East":    {"lat": 19.1692, "lng": 72.8556},
    "Malad West":       {"lat": 19.1862, "lng": 72.8285},
    "Malad East":       {"lat": 19.1892, "lng": 72.8552},
    "Kandivali West":   {"lat": 19.2062, "lng": 72.8362},
    "Kandivali East":   {"lat": 19.2092, "lng": 72.8612},
    "Borivali West":    {"lat": 19.2322, "lng": 72.8312},
    "Borivali East":    {"lat": 19.2352, "lng": 72.8612},
    "Dahisar":          {"lat": 19.2552, "lng": 72.8542},
    "Kurla":            {"lat": 19.0712, "lng": 72.8852},
    "Chembur":          {"lat": 19.0612, "lng": 72.9012},
    "Ghatkopar West":   {"lat": 19.0862, "lng": 72.9052},
    "Ghatkopar East":   {"lat": 19.0882, "lng": 72.9122},
    "Vikhroli":         {"lat": 19.1072, "lng": 72.9252},
    "Powai":            {"lat": 19.1176, "lng": 72.9060},
    "Bhandup":          {"lat": 19.1452, "lng": 72.9362},
    "Mulund West":      {"lat": 19.1762, "lng": 72.9412},
    "Mulund East":      {"lat": 19.1782, "lng": 72.9582},
    "Govandi":          {"lat": 19.0452, "lng": 72.9152},
    "Mankhurd":         {"lat": 19.0412, "lng": 72.9252},
    "Kanjurmarg":       {"lat": 19.1222, "lng": 72.9182},
    "Mira Road":        {"lat": 19.2852, "lng": 72.8712},
    "Bhayandar West":   {"lat": 19.3082, "lng": 72.8512},
    "Bhayandar East":   {"lat": 19.3052, "lng": 72.8712},
    "Kashimira":        {"lat": 19.3152, "lng": 72.8912},
    "Uttan":            {"lat": 19.3622, "lng": 72.7952},
    "Vasai West":       {"lat": 19.3712, "lng": 72.8012},
    "Vasai East":       {"lat": 19.3682, "lng": 72.8312},
    "Nalasopara West":  {"lat": 19.4152, "lng": 72.7912},
    "Nalasopara East":  {"lat": 19.4122, "lng": 72.8152},
    "Sopara":           {"lat": 19.4252, "lng": 72.8052},
    "Vasai Road":       {"lat": 19.3852, "lng": 72.8252},
    "Thane West":       {"lat": 19.2183, "lng": 72.9781},
    "Thane East":       {"lat": 19.2182, "lng": 73.0012},
    "Ghodbunder Road":  {"lat": 19.2452, "lng": 72.9712},
    "Majiwada":         {"lat": 19.2352, "lng": 72.9912},
    "Kopri":            {"lat": 19.2452, "lng": 73.0112},
    "Naupada":          {"lat": 19.2152, "lng": 72.9852},
    "Wagle Estate":     {"lat": 19.1952, "lng": 72.9752},
    "Teen Hath Naka":   {"lat": 19.2152, "lng": 73.0012},
    "Hiranandani Estate": {"lat": 19.2652, "lng": 72.9712},
    "Pokhran Road":     {"lat": 19.2352, "lng": 72.9812},
    "Manpada":          {"lat": 19.2252, "lng": 73.0212},
    "Upvan / Vasant Vihar": {"lat": 19.2352, "lng": 73.0112},
    "Vashi":            {"lat": 19.0745, "lng": 72.9978},
    "Nerul":            {"lat": 19.0332, "lng": 73.0162},
    "CBD Belapur":      {"lat": 19.0212, "lng": 73.0412},
    "Kharghar":         {"lat": 19.0252, "lng": 73.0672},
    "Airoli":           {"lat": 19.1552, "lng": 72.9982},
    "Ghansoli":         {"lat": 19.1252, "lng": 73.0012},
    "Kopar Khairane":   {"lat": 19.1052, "lng": 72.9882},
    "Sanpada":          {"lat": 19.0612, "lng": 72.9982},
    "Juinagar":         {"lat": 19.0452, "lng": 73.0152},
    "Seawoods":         {"lat": 19.0152, "lng": 73.0312},
    "Panvel":           {"lat": 18.9952, "lng": 73.1102},
    "Ulwe":             {"lat": 18.9852, "lng": 73.0612},
    "Dronagiri":        {"lat": 18.9552, "lng": 72.9752},
    "Taloja":           {"lat": 19.0252, "lng": 73.1452},
    "Kamothe":          {"lat": 19.0252, "lng": 73.0812},
    "Kalamboli":        {"lat": 19.0152, "lng": 73.0952},
    "Turbhe":           {"lat": 19.0812, "lng": 73.0212},
    "Roadpali":         {"lat": 19.0452, "lng": 73.0752},
    "Kalyan West":      {"lat": 19.2412, "lng": 73.1352},
    "Kalyan East":      {"lat": 19.2352, "lng": 73.1652},
    "Dombivli West":    {"lat": 19.2152, "lng": 73.0852},
    "Dombivli East":    {"lat": 19.2122, "lng": 73.1012},
    "Ulhasnagar":       {"lat": 19.2212, "lng": 73.1552},
    "Ambernath":        {"lat": 19.2012, "lng": 73.1852},
    "Badlapur":         {"lat": 19.1652, "lng": 73.2252},
    "Titwala":          {"lat": 19.2952, "lng": 73.2052},
    "Shahad":           {"lat": 19.2552, "lng": 73.1852},
    "Bhiwandi":         {"lat": 19.3052, "lng": 73.0652},
    "Murbad":           {"lat": 19.2552, "lng": 73.3952},
    "Shahapur":         {"lat": 19.4552, "lng": 73.3352},
    "Wada":             {"lat": 19.6652, "lng": 73.1952},
    "Palghar":          {"lat": 19.6952, "lng": 72.7652},
    "Boisar":           {"lat": 19.8052, "lng": 72.7652},
    "Karjat":           {"lat": 18.9152, "lng": 73.3152},
    "Khopoli":          {"lat": 18.7852, "lng": 73.3552},
    "Pen":              {"lat": 18.7352, "lng": 73.0952},
    # --- DELHI ---
    "Connaught Place":            {"lat": 28.6315, "lng": 77.2167},
    "Khan Market":                {"lat": 28.5993, "lng": 77.2271},
    "South Ext":                  {"lat": 28.5706, "lng": 77.2195},
    "Greater Kailash (GK 1 & 2)": {"lat": 28.5501, "lng": 77.2373},
    "Hauz Khas Village":          {"lat": 28.5494, "lng": 77.2001},
    "Aerocity":                   {"lat": 28.5562, "lng": 77.1173},
    # --- GURGAON ---
    "DLF Phase 3 / CyberHub": {"lat": 28.4952, "lng": 77.0888},
    "Golf Course Road":        {"lat": 28.4726, "lng": 77.1038},
    "Sector 29":               {"lat": 28.4719, "lng": 77.0697},
    "Sohna Road":              {"lat": 28.4231, "lng": 77.0359},
    # --- NOIDA ---
    "Sector 18":  {"lat": 28.5706, "lng": 77.3219},
    "Sector 62":  {"lat": 28.6271, "lng": 77.3664},
    "Sector 104": {"lat": 28.5282, "lng": 77.3641},
    # --- BENGALURU ---
    "Indiranagar":            {"lat": 12.9784, "lng": 77.6408},
    "Koramangala":            {"lat": 12.9352, "lng": 77.6245},
    "UB City / Lavelle Road": {"lat": 12.9719, "lng": 77.5963},
    "Whitefield":             {"lat": 12.9698, "lng": 77.7499},
    "HSR Layout":             {"lat": 12.9121, "lng": 77.6446},
    # --- CHENNAI ---
    "Nungambakkam":           {"lat": 13.0569, "lng": 80.2425},
    "Khader Nawaz Khan Road": {"lat": 13.0489, "lng": 80.2421},
    "Adyar":                  {"lat": 13.0012, "lng": 80.2565},
    "Alwarpet":               {"lat": 13.0359, "lng": 80.2556},
    # --- PUNE ---
    "Koregaon Park": {"lat": 18.5362, "lng": 73.8936},
    "Kalyani Nagar": {"lat": 18.5481, "lng": 73.9011},
    "Baner":         {"lat": 18.5590, "lng": 73.7868},
    "Viman Nagar":   {"lat": 18.5679, "lng": 73.9143},
    # --- CHANDIGARH ---
    "Sector 26":        {"lat": 30.7333, "lng": 76.8085},
    "Sector 35":        {"lat": 30.7273, "lng": 76.7738},
    "Elante Mall Area": {"lat": 30.7059, "lng": 76.8014},
}

CITY_AREA_MAP = {
    "Hyderabad": [
        "Ameerpet", "Begumpet", "SR Nagar", "Prakash Nagar", "Punjagutta", "Balkampet",
        "Madhura Nagar", "Rasoolpura", "Sanathnagar", "Bharat Nagar", "Erragadda",
        "Borabanda", "Moti Nagar", "Nehru Nagar", "Khairatabad", "Somajiguda",
        "Raj Bhavan Road", "Lakdikapool", "Saifabad", "A.C. Guards", "Masab Tank",
        "Chintal Basti", "Musheerabad", "Chikkadpally", "Himayatnagar", "Ashok Nagar",
        "Domalguda", "Hyderguda", "Ramnagar", "Azamabad", "Adikmet", "Nallakunta",
        "Shanker Mutt", "RTC X Roads", "Vidyanagar", "Narayanguda",
        "Durgabai Deshmukh Colony", "Central Excise Colony", "Amberpet", "Tilaknagar",
        "Golnaka", "Barkatpura", "Shivam Road", "Jamia Osmania", "Kachiguda",
        "Badichowdi", "Nampally", "Abids", "Aghapura", "Koti", "Bank Street",
        "Boggulkunta", "Mehdipatnam", "Karwan", "Secunderabad", "Chilkalguda",
        "Kavadiguda", "MG Road (James Street)", "Minister Road", "Mylargadda",
        "Namalagundu", "Padmarao Nagar", "Pan Bazar", "Paradise Circle", "Parsigutta",
        "Patny", "Rani Gunj", "RP Road", "Sindhi Colony", "Sitaphalmandi", "Tarnaka",
        "Warsiguda", "Addagutta", "Tukaramgate", "Kalasiguda", "Secunderabad Cantonment",
        "Bowenpally", "Karkhana", "Marredpally", "Sikh Village", "Trimulgherry",
        "Vikrampuri", "Gachibowli", "Gowlidoddi", "Nanakramguda", "HITEC City",
        "Madhapur", "Kondapur", "Kothaguda", "Kokapet", "Narsingi", "Jubilee Hills",
        "Banjara Hills", "Film Nagar", "Yousufguda", "Srinagar Colony", "Serilingampally",
        "Chanda Nagar", "Allwyn Colony", "Hafeezpet", "Madinaguda", "Miyapur",
        "Maktha Mahaboobpet", "Kukatpally", "Bachupally", "KPHB Colony", "Nizampet",
        "Pragathi Nagar", "Moosapet", "Mallampet", "Patancheru", "BHEL Township",
        "RC Puram", "Ameenpur", "Beeramguda", "Kistareddypet", "IDA Bollaram",
        "Medical Devices Park", "Afzal Gunj", "Aliabad", "Alijah Kotla", "Asif Nagar",
        "Azampura", "Barkas", "Bazarghat", "Begum Bazaar", "Chaderghat", "Chanchalguda",
        "Chandrayan Gutta", "Chatta Bazaar", "Dabirpura", "Dar-ul-Shifa", "Dhoolpet",
        "Edi Bazar", "Falaknuma", "Malakpet", "Moghalpura", "Jahanuma", "Laad Bazaar",
        "Lal Darwaza", "Langar Houz", "Madina", "Maharajgunj", "Mehboob ki Mehendi",
        "Mir Alam Tank", "Mozamjahi Market", "Nawab Saheb Kunta", "Nayapul",
        "Noorkhan Bazar", "Pisal Banda", "Purana Pul", "Putlibowli", "Rein Bazar",
        "Santoshnagar", "Shahran Market", "Shah Ali Banda", "Sultan Bazar", "Udden Gadda",
        "Uppuguda", "Yakutpura", "Owaiy Colony", "Kareemuddin House", "Balanagar",
        "Fateh Nagar", "Ferozguda", "Old Bowenpally", "Hasmathpet", "Suchitra Center",
        "Quthbullapur", "Jeedimetla", "Jagadgirigutta", "Suraram", "Pet Basheerabad",
        "Kompally", "Maisammaguda", "Medchal", "Kandlakoya", "Alwal", "Lothkunta",
        "Old Alwal", "Macha Bollaram", "Venkatapuram", "Shamirpet", "Malkajgiri",
        "Anandbagh", "Ammuguda", "Gautham Nagar", "Kakatiya Nagar", "Vinayak Nagar",
        "Moula-Ali", "Neredmet", "Old Neredmet", "Safilguda", "Sainikpuri", "Yapral",
        "Kapra", "A.S. Rao Nagar", "ECIL X-Roads", "Kamala Nagar", "Kushaiguda",
        "Cherlapally", "Keesara", "Nagaram", "Dammaiguda", "Jawaharnagar", "Rampally",
        "Cheriyal", "Uppal", "Habsiguda", "Ramanthapur", "Boduppal", "Nagole",
        "Nacharam", "Ghatkesar", "Peerzadiguda", "Chengicherla", "Pocharam", "Mallapur",
        "Narapally", "Medipally", "Dilsukhnagar", "Kothapet", "Gaddiannaram",
        "Moosarambagh", "Chaitanyapuri", "L.B. Nagar", "Bairamalguda", "Chintalakunta",
        "Vanasthalipuram", "Hastinapuram", "Saroornagar", "Badangpet", "Balapur",
        "Champapet", "Jillelguda", "Karmanghat", "Lingojiguda", "Meerpet", "Sanghi Nagar",
        "Hayathnagar", "Osman Nagar", "Ibrahimpatnam", "Toli Chowki", "Gudimalkapur",
        "Mallepally", "Padmanabha Nagar Colony", "Red Hills", "Shaikpet", "Rajendranagar",
        "Attapur", "Bandlaguda", "Gandipet", "Kismatpur", "Ring Road", "Puppalguda",
        "Kotapet", "Chevella", "Moinabad", "Shamshabad",
        "Rajiv Gandhi International Airport", "Umdanagar", "Shadnagar",
    ],
    "Mumbai / Greater Mumbai": [
        "Colaba", "Nariman Point", "Fort", "Churchgate", "Marine Drive", "Malabar Hill",
        "Breach Candy", "Grant Road", "Byculla", "Mazagaon", "Mahalaxmi", "Lower Parel",
        "Parel", "Dadar", "Matunga", "Sion", "Mahim", "Wadala", "Prabhadevi",
        "Dharavi", "Chunabhatti", "Bandra West", "Bandra East", "Khar",
        "Santacruz West", "Santacruz East", "Juhu", "Vile Parle West", "Vile Parle East",
        "Andheri West", "Andheri East", "Versova", "Jogeshwari West", "Jogeshwari East",
        "Goregaon West", "Goregaon East", "Malad West", "Malad East",
        "Kandivali West", "Kandivali East", "Borivali West", "Borivali East", "Dahisar",
        "Kurla", "Chembur", "Ghatkopar West", "Ghatkopar East", "Vikhroli", "Powai",
        "Bhandup", "Mulund West", "Mulund East", "Govandi", "Mankhurd", "Kanjurmarg",
        "Mira Road", "Bhayandar West", "Bhayandar East", "Kashimira", "Uttan",
        "Vasai West", "Vasai East", "Nalasopara West", "Nalasopara East", "Sopara",
        "Vasai Road", "Thane West", "Thane East", "Ghodbunder Road", "Majiwada",
        "Kopri", "Naupada", "Wagle Estate", "Teen Hath Naka", "Hiranandani Estate",
        "Pokhran Road", "Manpada", "Upvan / Vasant Vihar", "Vashi", "Nerul",
        "CBD Belapur", "Kharghar", "Airoli", "Ghansoli", "Kopar Khairane", "Sanpada",
        "Juinagar", "Seawoods", "Panvel", "Ulwe", "Dronagiri", "Taloja", "Kamothe",
        "Kalamboli", "Turbhe", "Roadpali", "Kalyan West", "Kalyan East",
        "Dombivli West", "Dombivli East", "Ulhasnagar", "Ambernath", "Badlapur",
        "Titwala", "Shahad", "Bhiwandi", "Murbad", "Shahapur", "Wada", "Palghar",
        "Boisar", "Karjat", "Khopoli", "Pen",
    ],
    "Delhi": [
        "Connaught Place", "Khan Market", "South Ext",
        "Greater Kailash (GK 1 & 2)", "Hauz Khas Village", "Aerocity",
    ],
    "Gurgaon":              ["DLF Phase 3 / CyberHub", "Golf Course Road", "Sector 29", "Sohna Road"],
    "Noida":                ["Sector 18", "Sector 62", "Sector 104"],
    "Bengaluru":            ["Indiranagar", "Koramangala", "UB City / Lavelle Road", "Whitefield", "HSR Layout"],
    "Chennai":              ["Nungambakkam", "Khader Nawaz Khan Road", "Adyar", "Alwarpet"],
    "Pune":                 ["Koregaon Park", "Kalyani Nagar", "Baner", "Viman Nagar"],
    "Chandigarh / Tricity": ["Sector 26", "Sector 35", "Elante Mall Area"],
}

MANAGER_PASSWORD = "APA@2024"

# Google Places (New) API Table A — confirmed from official docs, limit 50 types
# Verified February 2026 release — european_restaurant, halal_restaurant,
# north_indian_restaurant, south_indian_restaurant etc. now confirmed valid.
FNB_ALL_TYPES = [
    # Core (11)
    "restaurant", "cafe", "bar", "bakery", "coffee_shop", "fast_food_restaurant",
    "pub", "night_club", "food_court", "meal_delivery", "meal_takeaway",
    # Bar & grill variants (5)
    "wine_bar", "cocktail_bar", "sports_bar", "lounge_bar", "bar_and_grill",
    # Casual / other (6)
    "ice_cream_shop", "juice_shop", "tea_house", "diner",
    "fine_dining_restaurant", "buffet_restaurant",
    # India-specific & Middle Eastern (9)
    "indian_restaurant", "north_indian_restaurant", "south_indian_restaurant",
    "halal_restaurant", "kebab_shop", "shawarma_restaurant",
    "middle_eastern_restaurant", "lebanese_restaurant", "turkish_restaurant",
    # International cuisines popular in Indian metros (11)
    "european_restaurant", "mediterranean_restaurant", "italian_restaurant",
    "french_restaurant", "japanese_restaurant", "sushi_restaurant",
    "chinese_restaurant", "asian_restaurant", "thai_restaurant",
    "seafood_restaurant", "steak_house",
    # Contemporary / premium (8)
    "fusion_restaurant", "pizza_restaurant", "vietnamese_restaurant",
    "breakfast_restaurant", "brunch_restaurant", "sandwich_shop",
    "vegan_restaurant", "vegetarian_restaurant",
]  # Total: 50 exactly — confirmed valid, India-optimised

TYPE_PRIORITY = ["restaurant", "cafe", "bar", "coffee_shop", "bakery",
                 "fast_food_restaurant", "pub", "night_club"]

# 4x4 grid: ~2.5km steps → ~10km total span across the area
# 1500m cell radius → adjacent cells overlap ~560m, no gaps
GRID_OFFSETS = [-0.012, -0.004, 0.004, 0.012]
CELL_RADIUS  = 800.0
MAX_PAGES    = 3


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_data():
    try:
        df_sheet = conn.read(worksheet="Leads", ttl=0)
        for col in ALL_COLUMNS:
            if col not in df_sheet.columns:
                df_sheet[col] = ""
        return df_sheet
    except Exception as e:
        st.error(f"⚠️ Google Sheets connection failure: {e}")
        return pd.DataFrame(columns=ALL_COLUMNS)

def parse_coordinate(value, field_name):
    if value == "" or value is None:
        return None, None
    try:
        return float(value), None
    except (ValueError, TypeError):
        return None, f"⚠️ Invalid {field_name}: '{value}' is not a number. Pin skipped."

def _paginate_cell(api_key, headers, node_lat, node_lng, node_label, sweep_config=None):
    """Fetch up to MAX_PAGES pages from one grid cell via searchNearby."""
    cfg = sweep_config or {}
    url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:searchNearby"
    payload = {
        "includedTypes": FNB_ALL_TYPES,
        "maxResultCount": 20,
        "rankPreference": cfg.get("rankPreference", "POPULARITY"),
        "locationRestriction": {
            "circle": {
                "center": {"latitude": node_lat, "longitude": node_lng},
                "radius": CELL_RADIUS
            }
        },
        "languageCode": "en"
    }
    if cfg.get("priceLevels"):
        payload["priceLevels"] = cfg["priceLevels"]
    if cfg.get("minRating"):
        payload["minRating"] = cfg["minRating"]
    cell_places = []
    page = 0
    while page < MAX_PAGES:
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code != 200:
                st.warning(f"Node {node_label} p{page+1} → {resp.status_code}")
                st.json(resp.json())
                break
            data       = resp.json()
            places     = data.get("places", [])
            next_token = data.get("nextPageToken")
            cell_places.extend(places)
            page += 1
            if not next_token or len(places) < 20:
                break
            payload = {"pageToken": next_token}
            time.sleep(0.5)
        except Exception as e:
            st.warning(f"Node {node_label} p{page+1} failed: {str(e)}")
            break
    return cell_places

def execute_4x4_paginated_grid_sweep(api_key, city, area, sweep_config=None):
    """
    16-node 4x4 grid centred on the neighbourhood.
    Each node: up to 3 pages x 20 results = 60 venues.
    Total max: 16 x 60 = 960 unique venues per sweep.
    Deduplication by placeId across all nodes.
    """
    if area not in NEIGHBORHOOD_CONFIG:
        st.error(f"No config found for '{area}'.")
        return []

    cfg = NEIGHBORHOOD_CONFIG[area]
    nodes = [
        {"lat": cfg["lat"] + lat_off, "lng": cfg["lng"] + lng_off,
         "label": f"({lat_off:+.3f},{lng_off:+.3f})"}
        for lat_off in GRID_OFFSETS
        for lng_off in GRID_OFFSETS
    ]

    headers = {
        "content-type": "application/json",
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.location,places.rating,places.userRatingCount,"
            "places.priceLevel,places.types,places.websiteUri,"
            "places.nationalPhoneNumber,places.businessStatus"
        ),
        "x-rapidapi-host": "google-map-places-new-v2.p.rapidapi.com",
        "x-rapidapi-key":  api_key
    }

    seen_ids   = set()
    all_places = []
    total      = len(nodes)
    status_box = st.empty()
    progress   = st.progress(0, text="Initialising 16-node grid…")

    for i, node in enumerate(nodes):
        status_box.markdown(
            f"🛰️ **Grid Crawler:** Node `{i+1}/{total}` "
            f"at `{node['lat']:.4f}, {node['lng']:.4f}` — "
            f"**{len(all_places)}** unique venues so far"
        )
        progress.progress(int((i / total) * 90), text=f"Node {i+1}/{total}…")

        for place in _paginate_cell(api_key, headers, node["lat"], node["lng"], node["label"], sweep_config):
            pid    = place.get("id", "")
            status = place.get("businessStatus", "")
            if pid and pid not in seen_ids and status != "PERMANENTLY_CLOSED":
                seen_ids.add(pid)
                all_places.append(place)
        time.sleep(0.3)

    status_box.empty()
    progress.progress(95, text="Sorting by price tier then rating…")

    # Sort: price tier descending → rating descending → review count descending
    # This puts ₹₹₹₹ venues at top, roadside stalls at bottom — no venues excluded.
    PRICE_RANK = {
        "PRICE_LEVEL_VERY_EXPENSIVE": 4,
        "PRICE_LEVEL_EXPENSIVE":      3,
        "PRICE_LEVEL_MODERATE":       2,
        "PRICE_LEVEL_INEXPENSIVE":    1,
        "PRICE_LEVEL_FREE":           0,
        "":                          -1,   # untagged — sorted last
    }
    all_places.sort(key=lambda p: (
        p.get("userRatingCount", 0) or 0,               # popularity (review count) desc
        PRICE_RANK.get(p.get("priceLevel", ""), -1),   # price tier desc
        p.get("rating", 0) or 0,                        # rating value desc
    ), reverse=True)

    leads = []
    for place in all_places:
        name    = place.get("displayName", {}).get("text", "F&B Venue")
        address = place.get("formattedAddress", f"{area}, {city}")
        loc     = place.get("location", {})
        lat     = loc.get("latitude", "")
        lon     = loc.get("longitude", "")
        pid     = place.get("id", "")

        leads.append({
            "Restaurant Name":  name,
            "Cuisine/Type":     next((t.replace("_", " ").title() for t in TYPE_PRIORITY
                                     if t in place.get("types", [])), "Food Space"),
            "Zone/Area":        area,
            "Address":          address,
            "Latitude":         float(lat) if lat != "" else "",
            "Longitude":        float(lon) if lon != "" else "",
            "Map Link":         f"https://www.google.com/maps/place/?q=place_id:{pid}" if pid else "",
            "Website":          place.get("websiteUri", ""),
            "Restaurant Phone": place.get("nationalPhoneNumber", ""),
            "Google Rating":    str(place.get("rating", "")),
            "Total Reviews":    str(place.get("userRatingCount", "")),
            "Price Segment":    PRICE_LEVEL_MAP.get(place.get("priceLevel", ""), ""),
            "Lead Source":      "Google Maps V2 — 4×4 Grid Sweep",
            "Lead Status":      "Cold Lead",
            "Last Contacted":   datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    progress.progress(100, text=f"Done — {len(leads)} unique venues from 16 nodes.")
    return leads


# ── App ───────────────────────────────────────────────────────────────────────

df = load_data()

st.sidebar.markdown("### 🔐 Admin Controls")
user_password = st.sidebar.text_input("Enter Manager Password", type="password")
is_manager    = (user_password == MANAGER_PASSWORD)

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Pipeline Dashboard", "⚡ Quick Update / New Lead",
    "📥 Bulk Import CSV",    "🔍 Real-Time Lead Generator"
])

# ── Tab 1 ─────────────────────────────────────────────────────────────────────

with tab1:
    st.subheader("Current Pipeline")
    if df.empty:
        st.info("No data yet. Run the harvester on Tab 4.")
    else:
        if is_manager:
            st.download_button(
                "📥 Export Full CRM Database to CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"apa_pipeline_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="secure_mgr_export_btn"
            )
        else:
            st.warning("🔒 Export restricted. Enter Admin Password to unlock.")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_query = st.text_input("🔍 Search by Establishment Name")
        with col_f2:
            zone_filter = st.multiselect("Filter by Zone/Area",
                                         options=list(df["Zone/Area"].dropna().unique()))

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Restaurant Name"].str.contains(search_query, case=False, na=False)
            ]
        if zone_filter:
            filtered_df = filtered_df[filtered_df["Zone/Area"].isin(zone_filter)]

        display_df = filtered_df.copy()
        if not is_manager:
            for col in ["Acquisition Cost (Excl GST)", "Agreed Margin %", "Monthly Volume (Bottles)"]:
                if col in display_df.columns:
                    display_df[col] = "🔒 Restricted"

        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_default_column(
            filter=True,
            sortable=True,
            resizable=True,
            floatingFilter=True,   # filter row directly under headers, like Excel
            minWidth=100,
        )
        # Column-specific filter types
        gb.configure_column("Restaurant Name", pinned="left", minWidth=200,
                            filter="agTextColumnFilter")
        gb.configure_column("Cuisine/Type",    filter="agTextColumnFilter")
        gb.configure_column("Zone/Area",       filter="agSetColumnFilter")
        gb.configure_column("Lead Status",     filter="agSetColumnFilter")
        gb.configure_column("Price Segment",   filter="agSetColumnFilter")
        gb.configure_column("Google Rating",   filter="agNumberColumnFilter", type=["numericColumn"])
        gb.configure_column("Total Reviews",   filter="agNumberColumnFilter", type=["numericColumn"])
        gb.configure_column("Map Link",        cellRenderer="agHtmlCellRenderer",
                            cellRendererParams={"html": "<a href='{value}' target='_blank'>📍 Map</a>"})
        gb.configure_column("Website",         cellRenderer="agHtmlCellRenderer",
                            cellRendererParams={"html": "<a href='{value}' target='_blank'>🔗 Site</a>"})
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)
        gb.configure_side_bar(filters_panel=True, columns_panel=True)
        gb.configure_selection(selection_mode="single", use_checkbox=False)
        grid_opts = gb.build()

        AgGrid(
            display_df,
            gridOptions=grid_opts,
            update_mode=GridUpdateMode.NO_UPDATE,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            theme="streamlit",
            height=480,
            allow_unsafe_jscode=True,
            use_container_width=True,
        )

        map_df = filtered_df[["Restaurant Name", "Cuisine/Type", "Zone/Area",
                               "Google Rating", "Lead Status", "Latitude", "Longitude"]].copy()
        map_df["latitude"]  = pd.to_numeric(map_df["Latitude"],  errors="coerce")
        map_df["longitude"] = pd.to_numeric(map_df["Longitude"], errors="coerce")
        map_df = map_df.dropna(subset=["latitude", "longitude"])

        invalid_count = len(filtered_df) - len(map_df)
        if invalid_count > 0:
            st.warning(f"⚠️ {invalid_count} record(s) have missing/invalid coordinates and won't appear on map.")

        if not map_df.empty:
            view = pdk.ViewState(latitude=map_df["latitude"].median(),
                                 longitude=map_df["longitude"].median(), zoom=12, pitch=0)
            layer = pdk.Layer("ScatterplotLayer", data=map_df,
                              get_position="[longitude, latitude]",
                              get_color="[220, 50, 50, 180]", get_radius=100, pickable=True)
            tooltip = {
                "html": ("<b>{Restaurant Name}</b><br/>🍽️ {Cuisine/Type}<br/>"
                         "📍 {Zone/Area}<br/>⭐ {Google Rating}<br/>🔖 {Lead Status}"),
                "style": {"backgroundColor": "#0f1117", "color": "white",
                          "fontSize": "13px", "padding": "8px 12px", "borderRadius": "6px"}
            }
            st.pydeck_chart(
                pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip,
                         map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"),
                use_container_width=True
            )

# ── Tab 2 ─────────────────────────────────────────────────────────────────────

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
            st.warning(f"Deleted '{selected_rest}'.")
            time.sleep(1)
            st.rerun()

    with st.form("crm_entry_form", clear_on_submit=True):
        st.markdown("### 🏛️ 1. Profile Data")
        col1, col2 = st.columns(2)
        with col1:
            r_name  = st.text_input("Restaurant Name *",         value=defaults["Restaurant Name"])
            c_name  = st.text_input("Company / Parent Group",    value=defaults["Company Name"])
            cuisine = st.text_input("Cuisine / Type",            value=defaults["Cuisine/Type"])
            zone    = st.text_input("Zone / Area",               value=defaults["Zone/Area"])
            address = st.text_area("Address",                    value=defaults["Address"])
        with col2:
            web     = st.text_input("Website",                   value=defaults["Website"])
            r_phone = st.text_input("Restaurant Phone",          value=defaults["Restaurant Phone"])
            rating  = st.text_input("Google Rating",             value=str(defaults["Google Rating"]))
            map_l   = st.text_input("Google Maps Link",          value=defaults["Map Link"])
            lat_in  = st.text_input("Latitude (e.g. 17.4251)",  value=str(defaults["Latitude"]))
            lon_in  = st.text_input("Longitude (e.g. 78.4595)", value=str(defaults["Longitude"]))

        st.markdown("### 👥 2. Contact Directory")
        col3, col4 = st.columns(2)
        with col3:
            p_name     = st.text_input("Primary Contact Name",   value=defaults["Primary Contact Name"])
            p_role     = st.text_input("Primary Contact Role",   value=defaults["Primary Contact Role"])
            p_phone    = st.text_input("Primary Contact Phone",  value=defaults["Primary Contact Phone"])
            p_email    = st.text_input("Primary Contact Email",  value=defaults["Primary Contact Email"])
        with col4:
            dm_name    = st.text_input("Decision Maker Name",    value=defaults["Decision Maker Name"])
            dm_details = st.text_area("Decision Maker Details",  value=defaults["Decision Maker Details"])
            o_name     = st.text_input("Other Contact Name",     value=defaults["Other Contact Name"])
            o_details  = st.text_area("Other Contact Details",   value=defaults["Other Contact Details"])

        st.markdown("### 📊 3. Pipeline & Terms")
        col5, col6 = st.columns(2)
        with col5:
            curr_b      = st.text_input("Current Water Brand",          value=defaults["Current Brand"])
            b_type      = st.text_input("Bottle Type",                  value=defaults["Bottle Type"])
            acq_c       = st.text_input("Acquisition Cost (Excl. GST)", value=str(defaults["Acquisition Cost (Excl GST)"]))
            m_vol       = st.text_input("Monthly Volume (Bottles)",     value=str(defaults["Monthly Volume (Bottles)"]))
            expiry      = st.text_input("Competitor Contract Expiry",   value=defaults["Competitor Contract Expiry"])
        with col6:
            prop_sku    = st.text_input("Proposed APA SKU",             value=defaults["Proposed APA SKU"])
            sample_date = st.text_input("Sample Delivery Date",         value=defaults["Sample Delivery Date"])
            margin      = st.text_input("Agreed Margin %",              value=str(defaults["Agreed Margin %"]))
            credit      = st.text_input("Credit Terms",                 value=defaults["Credit Terms"])
            lead_src    = st.text_input("Lead Source",                  value=defaults["Lead Source"] or "Manual Entry")

        st.markdown("### ⚡ 4. Activity Logs")
        col7, col8 = st.columns(2)
        with col7:
            salesperson    = st.text_input("Salesperson Name", value=defaults["Salesperson Name"])
            status_options = ["Cold Lead", "Warm Lead", "Sample Dropped",
                              "Tasting Scheduled", "Negotiation", "Active Client", "Lost Account"]
            status = st.selectbox("Lead Status", status_options,
                                  index=status_options.index(defaults["Lead Status"])
                                  if defaults["Lead Status"] in status_options else 0)
        with col8:
            notes  = st.text_area("Interaction Notes",    value=defaults["Interaction Summary"])
            next_f = st.text_input("Next Follow-up Date", value=defaults["Next Follow-up"])

        if st.form_submit_button("💾 Save & Update Lead") and r_name:
            lat_val, lat_err = parse_coordinate(lat_in.strip(), "Latitude")
            lon_val, lon_err = parse_coordinate(lon_in.strip(), "Longitude")
            for err in [lat_err, lon_err]:
                if err: st.warning(err)

            form_entry = {
                "Restaurant Name": r_name, "Company Name": c_name, "Cuisine/Type": cuisine,
                "Zone/Area": zone, "Address": address, "Website": web,
                "Restaurant Phone": r_phone, "Google Rating": rating, "Map Link": map_l,
                "Latitude":  lat_val if lat_val is not None else "",
                "Longitude": lon_val if lon_val is not None else "",
                "Primary Contact Name": p_name, "Primary Contact Role": p_role,
                "Primary Contact Phone": p_phone, "Primary Contact Email": p_email,
                "Decision Maker Name": dm_name, "Decision Maker Details": dm_details,
                "Other Contact Name": o_name, "Other Contact Details": o_details,
                "Current Brand": curr_b, "Bottle Type": b_type,
                "Acquisition Cost (Excl GST)": acq_c, "Monthly Volume (Bottles)": m_vol,
                "Competitor Contract Expiry": expiry, "Proposed APA SKU": prop_sku,
                "Sample Delivery Date": sample_date, "Agreed Margin %": margin,
                "Credit Terms": credit, "Lead Source": lead_src,
                "Salesperson Name": salesperson, "Lead Status": status,
                "Last Contacted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Interaction Summary": notes, "Next Follow-up": next_f
            }
            if selected_rest != "-- Create New Blank Lead --":
                df = df[df["Restaurant Name"] != selected_rest]
            df = pd.concat([df, pd.DataFrame([form_entry])], ignore_index=True)
            conn.update(worksheet="Leads", data=df)
            st.success(f"Saved '{r_name}' to Google Sheets!")
            st.rerun()

# ── Tab 3 ─────────────────────────────────────────────────────────────────────

with tab3:
    st.subheader("📥 Bulk Import External Scraped Leads")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)
            if "Restaurant Name" not in import_df.columns:
                st.error("Invalid format: Missing 'Restaurant Name' column.")
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
                        st.success(f"Appended {len(imported_records)} new records to Google Sheets.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("All records already exist in the CRM.")
        except Exception as e:
            st.error(f"Parsing failure: {str(e)}")

# ── Tab 4 ─────────────────────────────────────────────────────────────────────

with tab4:
    st.subheader("🔍 Industrial 4×4 Deep Grid Harvester")
    st.markdown(
        "Deploys a **16-node coordinate grid** across a ~10km area. "
        "Each node paginates up to **3 pages × 20 results = 60 venues**. "
        "Theoretical max per sweep: **960 unique venues**."
    )

    city_selected = st.selectbox("Target City", list(CITY_AREA_MAP.keys()))
    area_selected = st.selectbox("Neighbourhood", CITY_AREA_MAP[city_selected])

    venue_focus = st.selectbox(
        "Venue Focus",
        options=["All venues", "Mid to premium (₹₹+)", "Premium only (₹₹₹+)"],
        index=0,
        help="Controls price filter and ranking. Premium modes suppress roadside stalls and rank by popularity."
    )

    # priceLevels not used — avoids excluding new venues with no price tag yet.
    # minRating filters by star VALUE not review count, so new places still appear.
    # Price tier ordering is applied post-fetch via sort, not as an API filter.
    SWEEP_CONFIGS = {
        "All venues (₹–₹₹₹₹)": {
            "rankPreference": "POPULARITY",
            "priceLevels":    None,
            "minRating":      3.5,
        },
        "Mid to premium (₹₹+)": {
            "rankPreference": "POPULARITY",
            "priceLevels":    ["PRICE_LEVEL_MODERATE", "PRICE_LEVEL_EXPENSIVE", "PRICE_LEVEL_VERY_EXPENSIVE"],
            "minRating":      3.5,
        },
        "Premium only (₹₹₹+)": {
            "rankPreference": "POPULARITY",
            "priceLevels":    ["PRICE_LEVEL_EXPENSIVE", "PRICE_LEVEL_VERY_EXPENSIVE"],
            "minRating":      3.5,
        },
    }
    sweep_config = SWEEP_CONFIGS[venue_focus]

    st.caption("ℹ️ 16 nodes × 3 pages × 20 results = up to **960 unique venues** | up to **48 API calls** per harvest")

    # ── API Connection Tester ──────────────────────────────────────────────────
    with st.expander("🔧 Test API Connection (run this first if getting zero results)"):
        if st.button("🧪 Run Single Node Test"):
            test_key = st.secrets.get("RAPIDAPI_KEY", "")
            if not test_key:
                st.error("No RAPIDAPI_KEY found in secrets.")
            else:
                cfg = NEIGHBORHOOD_CONFIG.get(area_selected, {})
                if cfg:
                    test_url = "https://google-map-places-new-v2.p.rapidapi.com/v1/places:searchNearby"
                    test_payload = {
                        "includedTypes": ["restaurant", "cafe", "bar"],
                        "maxResultCount": 3,
                        "rankPreference": "DISTANCE",
                        "locationRestriction": {
                            "circle": {
                                "center": {"latitude": cfg["lat"], "longitude": cfg["lng"]},
                                "radius": 1500.0
                            }
                        },
                        "languageCode": "en"
                    }
                    test_headers = {
                        "content-type": "application/json",
                        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress",
                        "x-rapidapi-host": "google-map-places-new-v2.p.rapidapi.com",
                        "x-rapidapi-key": test_key
                    }
                    try:
                        r = requests.post(test_url, json=test_payload, headers=test_headers, timeout=15)
                        st.markdown(f"**Status:** `{r.status_code}`")
                        st.json(r.json())
                        if r.status_code == 200:
                            places = r.json().get("places", [])
                            if places:
                                st.success(f"✅ searchNearby works — returned {len(places)} results. Safe to run full harvest.")
                            else:
                                st.warning("⚠️ 200 OK but empty places array — searchNearby may not be in your subscription plan.")
                        elif r.status_code == 403:
                            st.error("❌ 403 Forbidden — searchNearby endpoint not included in your RapidAPI subscription. Upgrade plan or switch endpoint.")
                        elif r.status_code == 400:
                            st.error("❌ 400 Bad Request — payload rejected. See response above for details.")
                        else:
                            st.error(f"❌ Unexpected status {r.status_code}.")
                    except Exception as e:
                        st.error(f"Request failed: {e}")

    if st.button("🚀 Execute 16-Node Grid Crawl"):
        active_key = st.secrets.get("RAPIDAPI_KEY", "")
        if not active_key:
            st.error("Missing RAPIDAPI_KEY in secrets.")
        else:
            scraped_results = execute_4x4_paginated_grid_sweep(active_key, city_selected, area_selected, sweep_config)
            if scraped_results:
                # Dedup by placeId (embedded in Map Link) — name-only dedup
                # caused real venues to be silently skipped when outer grid nodes
                # had already filled the name index with wrong-area venues.
                existing_map_links = set(df["Map Link"].dropna().values)
                existing_names     = set(df["Restaurant Name"].dropna().values)
                new_rows = []
                for item in scraped_results:
                    map_link = item.get("Map Link", "")
                    name     = item.get("Restaurant Name", "").strip()
                    # If we have a placeId link, use that; fall back to name only if no link
                    already_exists = (
                        (map_link and map_link in existing_map_links) or
                        (not map_link and name in existing_names)
                    )
                    if not already_exists:
                        entry = {col: "" for col in ALL_COLUMNS}
                        entry.update(item)
                        new_rows.append(entry)
                if new_rows:
                    try:
                        fresh_df = conn.read(worksheet="Leads", ttl=0)
                    except Exception:
                        fresh_df = df.copy()
                    df = pd.concat([fresh_df, pd.DataFrame(new_rows)], ignore_index=True)
                    conn.update(worksheet="Leads", data=df)
                    st.success(
                        f"✅ Imported **{len(new_rows)}** new venues "
                        f"({len(scraped_results) - len(new_rows)} already in CRM)."
                    )
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("All returned venues are already in the CRM for this area.")
            else:
                st.error("Zero results returned. Verify your RapidAPI key and subscription plan.")