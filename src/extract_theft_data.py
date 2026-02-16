import pandas as pd
import os
import sys
import re
from openpyxl.utils.cell import column_index_from_string

def get_state_from_row(row):
    # Check S_No and District columns for "State"
    s_no = str(row['S_No']).strip()
    dist = str(row['District']).strip()
    
    # Check for "State/UT" or "State :" patterns
    # Regex to capture "State", "UT", "Union Territory" followed by optional punctuation
    state_pattern = r'(?i)^(state|ut|union territory)[\s/]*[:.-]?\s*'
    
    if re.search(state_pattern, s_no):
         return re.sub(state_pattern, '', s_no).strip()
    
    if re.search(state_pattern, dist):
         return re.sub(state_pattern, '', dist).strip()
         
    return None

def is_district_row(row):
    # S_No should be integer-like
    s_no = row['S_No']
    dist = row['District']
    
    # Check if s_no is a number
    try:
        float(s_no)
    except:
        return False
        
    # Check if District is NOT a number (header rows often have numbers in all columns)
    try:
        float(dist)
        return False # It's a header row number
    except:
        pass
        
    return True

def process_year(year, theft_col_letter, cruelty_col_letter):
    file_path = f'data/IPC_Crimes_{year}.xlsx'
    if not os.path.exists(file_path):
        print(f"File missing: {file_path}")
        return pd.DataFrame()

    theft_col_idx = column_index_from_string(theft_col_letter) - 1
    murder_col_idx = column_index_from_string('C') - 1 # Always Column 3 (Index 2)
    cruelty_col_idx = column_index_from_string(cruelty_col_letter) - 1

    print(f"Processing {year} from {file_path} (Theft:{theft_col_letter}, Cruelty:{cruelty_col_letter})...")
    
    # Indices needed
    cols_to_use = [0, 1, murder_col_idx, theft_col_idx, cruelty_col_idx]
    # Ensure unique and sorted for read_excel stability
    cols_to_use = sorted(list(set(cols_to_use)))
    
    # Read all rows
    df = pd.read_excel(file_path, header=None, usecols=cols_to_use)
    
    # The columns will be returned in ascending index order.
    # 0 -> S_No
    # 1 -> District
    # murder (Index 2) -> Murder
    # Cruelty (Usually > 100)
    # Theft (Usually ~90)
    
    # We need to map the output dataframe columns back to our concepts
    # Since we sorted the indices, we can recreate the map.
    col_map = {
        0: 'S_No',
        1: 'District',
        murder_col_idx: 'Murder',
        theft_col_idx: 'Theft',
        cruelty_col_idx: 'Cruelty'
    }
    
    # Create the actual column names list based on the sorted indices
    actual_col_names = [col_map[idx] for idx in cols_to_use]
    df.columns = actual_col_names
    
    extracted_data = []
    current_state = "Unknown"
    
    for _, row in df.iterrows():
        state = get_state_from_row(row)
        if state:
            current_state = state
            continue
            
        if is_district_row(row):
            district = str(row['District']).strip()
            # Skip "Total" or similar aggregations if they have a numeric S_No
            if district.upper() == 'TOTAL' or district.upper().startswith('TOTAL '):
                continue
            
            # Clean values
            theft_val = row['Theft']
            murder_val = row['Murder']
            cruelty_val = row['Cruelty']
            
            extracted_data.append({
                'State': current_state,
                'District': district,
                f'Theft_{year}': theft_val,
                f'Murder_{year}': murder_val,
                f'Cruelty_{year}': cruelty_val
            })
            
    return pd.DataFrame(extracted_data)

def main():
    # Year, Theft_Col, Cruelty_Col
    years_config = [
        (2017, 'CN', 'EI'),
        (2018, 'CN', 'EI'),
        (2019, 'CM', 'EH'),
        (2022, 'CM', 'EH'), 
        (2023, 'CM', 'EH')
    ]

    final_df = None

    for year, theft_col, cruelty_col in years_config:
        year_df = process_year(year, theft_col, cruelty_col)
        print(f"Extracted {len(year_df)} rows for {year}")
        
        if year_df.empty:
            continue
            
        if final_df is None:
            final_df = year_df
        else:
            final_df = pd.merge(final_df, year_df, on=['State', 'District'], how='outer')

    output_path = 'data/theft_data_extracted.csv'
    if final_df is not None:
        final_df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
        print(final_df.head())
    else:
        print("No data extracted.")

if __name__ == "__main__":
    main()
