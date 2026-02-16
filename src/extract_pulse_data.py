import os
import json
import pandas as pd

def extract_pulse_data():
    # Base paths
    user_base_path = 'data/pulse/data/map/user/hover/country/india/state'
    txn_base_path = 'data/pulse/data/map/transaction/hover/country/india/state'
    
    if not os.path.exists(user_base_path) or not os.path.exists(txn_base_path):
        print(f"One of the paths does not exist: {user_base_path} or {txn_base_path}")
        return

    records = []

    # Iterate over states (assuming structure matches in both)
    # We drive with user_base_path
    for state_folder in os.listdir(user_base_path):
        state_path_user = os.path.join(user_base_path, state_folder)
        state_path_txn = os.path.join(txn_base_path, state_folder)
        
        if not os.path.isdir(state_path_user):
            continue
            
        state_name = state_folder.replace('-', ' ').title()
        
        # Iterate over years
        for year in os.listdir(state_path_user):
            if not year.isdigit():
                continue
            
            # Filter years slightly to optimization? 
            # We need 2017-2020 (to cover 2019 data and 2017 lags)
            # 2017: Need txn(2017), reg(2018Q1->2017)
            # ...
            # Actually we just extract everything available and filter later.
                
            year_path_user = os.path.join(state_path_user, year)
            year_path_txn = os.path.join(state_path_txn, year)
            
            if not os.path.isdir(year_path_user):
                continue

            # Iterate over quarters 1-4
            for q in range(1, 5):
                q_file = f"{q}.json"
                
                # --- Read User Data ---
                user_file = os.path.join(year_path_user, q_file)
                user_data_map = {} # District -> {Reg, AppOpens}
                
                if os.path.exists(user_file):
                    try:
                        with open(user_file, 'r') as f:
                            u_json = json.load(f)
                            hover_data = u_json.get('data', {}).get('hoverData', {})
                            for dist, metrics in hover_data.items():
                                dist_clean = dist.replace(" district", "").title().strip()
                                user_data_map[dist] = {
                                    'RegisteredUsers': metrics.get('registeredUsers', 0),
                                    'AppOpens': metrics.get('appOpens', 0)
                                }
                                # Add raw district name for debugging key matching if needed
                                # but usually they are consistent within same quarter
                                user_data_map[dist]['raw_name'] = dist
                    except Exception as e:
                        print(f"Error reading user file {user_file}: {e}")

                # --- Read Transaction Data ---
                txn_file = os.path.join(year_path_txn, q_file)
                txn_data_map = {} # District -> {Count, Amount}
                
                if os.path.exists(txn_file):
                    try:
                        with open(txn_file, 'r') as f:
                            t_json = json.load(f)
                            hover_list = t_json.get('data', {}).get('hoverDataList', [])
                            for item in hover_list:
                                dist = item.get('name')
                                metrics = item.get('metric', [])
                                count = 0
                                amount = 0
                                for m in metrics:
                                    if m.get('type') == 'TOTAL':
                                        count = m.get('count', 0)
                                        amount = m.get('amount', 0)
                                        break
                                
                                txn_data_map[dist] = {
                                    'TransactionCount': count,
                                    'TransactionAmount': amount
                                }
                    except Exception as e:
                        print(f"Error reading txn file {txn_file}: {e}")

                # --- Merge and Record ---
                # Get all unique districts from both maps
                all_districts_raw = set(user_data_map.keys()) | set(txn_data_map.keys())
                
                for dist_raw in all_districts_raw:
                    # Use the cleaning logic (remove ' district') for the record
                    dist_clean = dist_raw.replace(" district", "").title().strip()
                    
                    u_metrics = user_data_map.get(dist_raw, {})
                    t_metrics = txn_data_map.get(dist_raw, {})
                    
                    record = {
                        'State': state_name,
                        'Year': int(year),
                        'Quarter': q,
                        'District': dist_clean,
                        'RegisteredUsers': u_metrics.get('RegisteredUsers', 0),
                        'AppOpens': u_metrics.get('AppOpens', 0),
                        'TransactionCount': t_metrics.get('TransactionCount', 0),
                        'TransactionAmount': t_metrics.get('TransactionAmount', 0)
                    }
                    records.append(record)

    df = pd.DataFrame(records)
    output_path = 'data/pulse_unified_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Extracted {len(df)} records to {output_path}")
    print(df.head())

if __name__ == "__main__":
    extract_pulse_data()
