import os
import json
import pandas as pd

def extract_pulse_users():
    base_path = 'data/pulse/data/map/user/hover/country/india/state'
    
    if not os.path.exists(base_path):
        print(f"Path does not exist: {base_path}")
        return

    records = []

    # Iterate over states
    for state_folder in os.listdir(base_path):
        state_path = os.path.join(base_path, state_folder)
        if not os.path.isdir(state_path):
            continue
            
        state_name = state_folder.replace('-', ' ').title()
        
        # Iterate over years
        for year in os.listdir(state_path):
            if not year.isdigit():
                continue
                
            year_path = os.path.join(state_path, year)
            if not os.path.isdir(year_path):
                continue
                
            # We only want Q1 data -> 1.json
            q1_file = os.path.join(year_path, '1.json')
            if not os.path.exists(q1_file):
                # Try checking if there are other files, maybe 2024 doesn't have Q1 yet?
                # But we only want Q1, so if it's missing, we skip.
                continue
                
            try:
                with open(q1_file, 'r') as f:
                    data = json.load(f)
                    
                hover_data = data.get('data', {}).get('hoverData', {})
                
                for district_key, metrics in hover_data.items():
                    # clean district name: "anantapur district" -> "Anantapur"
                    # But maybe keeping "District" is safer? 
                    # The user's earlier data had "Anantapur", "Chittoor".
                    # The JSON has "anantapur district".
                    # Let's clean it up to be title case at least.
                    
                    district_name = district_key.title()
                    # Optional: Remove " District" suffix if present to match other datasets better?
                    # The user didn't explicitly ask for matching, but it's good practice.
                    # However, some might be "xyz city". 
                    # for now, I will keep it title cased.
                    
                    registered_users = metrics.get('registeredUsers', 0)
                    app_opens = metrics.get('appOpens', 0)
                    
                    records.append({
                        'State': state_name,
                        'Year': int(year),
                        'Quarter': 1,
                        'District': district_name,
                        'RegisteredUsers': registered_users,
                        'AppOpens': app_opens
                    })
                    
            except Exception as e:
                print(f"Error processing {q1_file}: {e}")

    if not records:
        print("No data extracted.")
        return

    df = pd.DataFrame(records)
    output_file = 'data/pulse_users_q1_data.csv'
    df.to_csv(output_file, index=False)
    print(f"Extracted {len(df)} records to {output_file}")
    print(df.head())

if __name__ == '__main__':
    extract_pulse_users()
