import pandas as pd
import re
import os

def normalize_district(name):
    if not isinstance(name, str):
        return ""
    name = str(name).lower().strip()
    
    # --- 1. General Cleaning ---
    remove_phrases = [
        " police district", " police", " commissionarate", " commisionerate", " commissionerate", 
        " commr.", " commr", " comm.",
        " city", " rural", " urban", 
        " railway", " railways", " r.p.", " grp", " tr", " w.rly", " metro", " pc",
        " crime branch", " spl cell", " spuwac", " vigilance", " eow", " cice",
        " cyber crime", " cyber", " anti narcotic task force", " special crime wing",
        " ats & sog", " cid"
    ]
    
    for phrase in remove_phrases:
        if phrase in name:
            name = name.replace(phrase, "")

    # Remove content in parentheses e.g. "(East)", "(West)"
    name = re.sub(r'\s*\(.*?\)', '', name)
    
    # Formatting fixes
    name = name.replace(" & ", " and ")
    name = name.replace("-", " ")
    name = name.replace(".", "")
    name = name.strip()

    # --- 2. Specific Mappings ---
    mappings = {
        # Andhra Pradesh
        "cuddapah": "ysr",
        "kadapa": "ysr",
        "y s r": "ysr",
        "nellore": "spsr nellore",
        "sri potti sriramulu nellore": "spsr nellore",
        "prakasham": "prakasam",
        "rajahmundry": "east godavari", 
        "visakha": "visakhapatnam",
        "vijayawada": "ntr",
        "tirupathi": "tirupati",
        "ntr": "krishna", 
        "anakapalli": "visakhapatnam", 
        "alluri sitharama raju": "visakhapatnam", 
        "bapatla": "guntur", 
        "palnadu": "guntur", 
        "konaseema": "east godavari", 
        "dr br ambedkar konaseema": "east godavari",
        "eluru": "west godavari", 
        "kakinada": "east godavari",
        "nandyal": "kurnool",
        "sri sathya sai": "anantapur",
        "annamayya": "ysr", 
        "parvathipuram manyam": "vizianagaram",

        # Bihar
        "bhabhua": "kaimur bhabua",
        "kaimur": "kaimur bhabua",
        "bettiah": "pashchim champaran",
        "motihari": "purbi champaran",

        # Gujarat
        "ahmedabad": "ahmadabad",
        "baroda": "vadodara",
        "broach": "bharuch",
        "dohad": "dahod",
        "panchmahal": "panch mahals",
        "banaskantha": "banas kantha",
        "sabarkantha": "sabar kantha",
        "mehsana": "mahesana",
        "kutch": "kachchh",
        "araavallis": "arvalli",

        # Haryana
        "mewat": "nuh",
        "gurgaon": "gurugram",
        "hansi": "hisar",

        # Himachal
        "nurpur": "kangra", 
        "baddi": "solan", 

        # Karnataka
        "belgaum": "belagavi",
        "bellary": "ballari",
        "bijapur": "vijayapura",
        "chikmagalur": "chikkamagaluru",
        "gulbarga": "kalaburagi",
        "mysore": "mysuru",
        "shimoga": "shivamogga",
        "tumkur": "tumakuru",
        "kgf": "kolar",
        "vijayanagara": "ballari", 
        "hubballi dharwad": "dharwad",
        "bagalkot": "bagalkote",

        # Kerala
        "trivandrum": "thiruvananthapuram",
        "cochin": "ernakulam",
        "alleppey": "alappuzha",
        "cannanore": "kannur",
        "palghat": "palakkad",
        "quilon": "kollam",
        "trichur": "thrissur",
        "kasargod": "kasaragod",
        "wayanadu": "wayanad",

        # MP
        "hoshangabad": "narmadapuram",
        "khandwa": "east nimar",
        "khargone": "west nimar",
        "narsinghpur": "narsimhapur",
        "jabalpur": "jabalpur",
        "agar": "agar malwa",

        # Maharashtra
        "ahmednagar": "ahilyanagar",
        "aurangabad": "chhatrapati sambhajinagar", 
        "osmanabad": "dharashiv", 
        "mira bhayandar vasai virar": "thane", 
        "pimpri chinchwad": "pune",

        # Odisha
        "balasore": "baleshwar",
        "keonjhar": "kendujhar",
        "jajpur": "jajapur",
        "nabarangapur": "nabarangpur",
        "sonapur": "subarnapur", 
        "sonepur": "subarnapur",
        "angul": "anugul",
        "jamshedpur": "east singhbhum",
        "jagatsinghpur": "jagatsinghapur",

        # Punjab
        "malerkotla": "sangrur", 
        "batala": "gurdaspur", 
        "khanna": "ludhiana",
        "sbs nagar": "shahid bhagat singh nagar",
        "muktsar": "sri muktsar sahib",
        "ferozepur": "firozepur",

        # Rajasthan
        "kekri": "ajmer",
        "beawar": "ajmer",
        "shahpura": "bhilwara",
        "salumbar": "udaipur",
        "sanchore": "jalor",
        "phalodi": "jodhpur",
        "didwana kuchaman": "nagaur",
        "neem ka thana": "sikar",
        "kotputli behror": "jaipur",
        "khairtal tijara": "alwar",
        "deeg": "bharatpur",
        "gangapur": "sawai madhopur",
        "balotra": "barmer",
        "anupgarh": "sriganganagar",
        "dudu": "jaipur",
        "bhiwadi": "alwar",

        # Sikkim
        "gangtok": "east district",
        "pakyong": "east district",
        "gyalshing": "west district",
        "soreng": "west district",
        "mangan": "north district",
        "namchi": "south district",

        # Tamil Nadu
        "chengalpattu": "kancheepuram", 
        "kallakurichi": "viluppuram", 
        "ranipet": "vellore", 
        "tirupathur": "vellore", 
        "tiruppattur": "vellore",
        "tenkasi": "tirunelveli", 
        "mayiladuthurai": "nagapattinam", 
        "tambaram": "chengalpattu", 
        "avadi": "thiruvallur", 
        "kanchipuram": "kancheepuram",
        "villupuram": "viluppuram",
        "kanyakumari": "kanniyakumari",

        # UP
        "allahabad": "prayagraj", 
        "faizabad": "ayodhya", 
        "kaushambi": "kaushambi",
        "kushi nagar": "kushinagar",
        "lakhimpur": "kheri",
        "lakhimpur kheri": "kheri",
        "kanpur outer": "kanpur nagar",
        "varanasi dehat": "varanasi",
        "bhadohi": "sant ravidas nagar", 
        "barabanki": "bara banki",
        "bulandshahar": "bulandshahr",
        "gautambudh nagar": "gautam buddha nagar",
        "gautambudhnagar": "gautam buddha nagar",
        "amroha": "jyotiba phule nagar", # Or vice versa

        # West Bengal
        "burdwan": "bardhaman",
        "barddhaman": "bardhaman",
        "purba bardhaman": "east bardhaman",
        "paschim bardhaman": "west bardhaman", 
        "coochbehar": "koch bihar",
        "darjeeling": "darjiling",
        "hooghly": "hugli",
        "howrah": "haora",
        "midnapore": "medinipur",
        "barasat": "north 24 parganas",
        "basirhat": "north 24 parganas",
        "bangaon": "north 24 parganas",
        "barrackpore": "north 24 parganas",
        "bidhannagar": "north 24 parganas",
        "baruipur": "south 24 parganas",
        "diamond harbour": "south 24 parganas",
        "sundarban": "south 24 parganas",
        "krishnagar": "nadia",
        "ranaghat": "nadia",
        "jangipur": "murshidabad",
        "berhampore": "murshidabad",
        "raiganj": "north dinajpur",
        "islampur": "north dinajpur",
        "balurghat": "south dinajpur",
        "gangarampur": "south dinajpur",
        "bishnupur": "bankura",
        "khatra": "bankura",
        "asansol durgapur": "west bardhaman",
        "kalimpong": "darjiling",
        "jhargram": "west medinipur", 

        # Delhi 
        "delhi ut": "delhi",
        "igi airport": "new delhi",
        "active": "delhi",
        "outer north": "north west",
        "shahdara": "east", 
        "southeast": "south east",
        "southwest": "south west",
        "northeast": "north east",
        "northwest": "north west",
    }
    
    if name in mappings:
        name = mappings[name]
    
    return name.strip()

def main():
    theft_path = 'data/theft_data_extracted.csv'
    pulse_path = 'data/pulse_unified_data.csv'
    output_path = 'data/master_district_data.csv'
    
    if not os.path.exists(theft_path):
        print(f"Error: {theft_path} not found.")
        return
    if not os.path.exists(pulse_path):
        print(f"Error: {pulse_path} not found.")
        return

    print("Loading data...")
    theft_df = pd.read_csv(theft_path)
    pulse_df = pd.read_csv(pulse_path)

    print(f"Theft Data: {len(theft_df)} rows")
    theft_df['District_Norm'] = theft_df['District'].apply(normalize_district)
    theft_df['State_Norm'] = theft_df['State'].apply(normalize_district)

    # Aggregate Theft Data (Summing in case mappings merged districts)
    # Include both Theft_, Murder_, Cruelty_ columns
    crime_cols = [c for c in theft_df.columns if c.startswith('Theft_') or c.startswith('Murder_') or c.startswith('Cruelty_')]
    
    # Aggregation dictionary
    theft_agg_dict = {col: 'sum' for col in crime_cols}
    theft_agg_dict['State'] = 'first'
    
    theft_grouped = theft_df.groupby(['State_Norm', 'District_Norm'], as_index=False).agg(theft_agg_dict)
    print(f"Theft Data (Aggregated with Murder/Cruelty): {len(theft_grouped)} rows")

    print(f"Pulse Data (Unified): {len(pulse_df)} rows")
    
    # --- Prepare Pulse Data ---
    
    # Filter Q1 only
    pulse_reg = pulse_df[pulse_df['Quarter'] == 1].copy()
    pulse_reg['Target_Year'] = pulse_reg['Year'] - 1
    
    pulse_reg_pivot = pulse_reg.pivot_table(
        index=['State', 'District'],
        columns='Target_Year',
        values='RegisteredUsers'
    ).reset_index()
    
    # Rename pivot columns
    current_cols = list(pulse_reg_pivot.columns)
    new_cols = []
    for c in current_cols:
        if isinstance(c, int):
            new_cols.append(f"RegisteredUsers_{c}")
        else:
            new_cols.append(c)
    pulse_reg_pivot.columns = new_cols

    # Transaction Volume
    pulse_txn = pulse_df.groupby(['State', 'District', 'Year'], as_index=False)['TransactionCount'].sum()
    
    pulse_txn_pivot = pulse_txn.pivot_table(
        index=['State', 'District'],
        columns='Year',
        values='TransactionCount'
    ).reset_index()
    
    current_cols_txn = list(pulse_txn_pivot.columns)
    new_cols_txn = []
    for c in current_cols_txn:
        if isinstance(c, int):
            new_cols_txn.append(f"TransactionVolume_{c}")
        else:
            new_cols_txn.append(c)
    pulse_txn_pivot.columns = new_cols_txn
    
    # Merge Reg and Txn
    pulse_combined = pd.merge(pulse_reg_pivot, pulse_txn_pivot, on=['State', 'District'], how='outer')
    
    # Normalize Districts and Aggregate Pulse
    pulse_combined['District_Norm'] = pulse_combined['District'].apply(normalize_district)
    pulse_combined['State_Norm'] = pulse_combined['State'].apply(normalize_district)
    
    pulse_numeric_cols = [c for c in pulse_combined.columns if c.startswith('RegisteredUsers_') or c.startswith('TransactionVolume_')]
    
    pulse_agg_dict = {col: 'sum' for col in pulse_numeric_cols}
    pulse_agg_dict['State'] = 'first'
    
    pulse_grouped = pulse_combined.groupby(['State_Norm', 'District_Norm'], as_index=False).agg(pulse_agg_dict)
    print(f"Pulse Data (Aggregated & Combined): {len(pulse_grouped)} districts")

    # --- Final Merge ---
    merged_df = pd.merge(
        theft_grouped, 
        pulse_grouped, 
        on=['State_Norm', 'District_Norm'], 
        how='inner',
        suffixes=('_Crime', '_Pulse')
    )
    
    print(f"Merged Data: {len(merged_df)} rows")
    
    out_data = merged_df.copy()
    out_data['District'] = out_data['District_Norm'].str.title()
    if 'State_Crime' in out_data.columns:
        out_data['State'] = out_data['State_Crime']
    
    cols_to_keep = ['State', 'District']
    
    # Data columns
    target_years = [2017, 2018, 2019, 2022, 2023]
    
    for y in target_years:
        # Theft
        c_theft = f"Theft_{y}"
        if c_theft in out_data.columns:
             cols_to_keep.append(c_theft)
        elif f"{c_theft}_Crime" in out_data.columns:
            out_data[c_theft] = out_data[f"{c_theft}_Crime"]
            cols_to_keep.append(c_theft)
            
        # Murder
        c_murder = f"Murder_{y}"
        if c_murder in out_data.columns:
             cols_to_keep.append(c_murder)
        elif f"{c_murder}_Crime" in out_data.columns:
            out_data[c_murder] = out_data[f"{c_murder}_Crime"]
            cols_to_keep.append(c_murder)

        # Cruelty
        c_cruelty = f"Cruelty_{y}"
        if c_cruelty in out_data.columns:
             cols_to_keep.append(c_cruelty)
        elif f"{c_cruelty}_Crime" in out_data.columns:
            out_data[c_cruelty] = out_data[f"{c_cruelty}_Crime"]
            cols_to_keep.append(c_cruelty)
            
        # Pulse
        c_reg = f"RegisteredUsers_{y}"
        if c_reg in out_data.columns:
            cols_to_keep.append(c_reg)
        
        c_txn = f"TransactionVolume_{y}"
        if c_txn in out_data.columns:
            cols_to_keep.append(c_txn)
            
    final_cols = [c for c in cols_to_keep if c in out_data.columns]
    
    final_df = out_data[final_cols].copy()
    final_df.to_csv(output_path, index=False)
    print(f"Saved merged data to {output_path}")

if __name__ == "__main__":
    main()
