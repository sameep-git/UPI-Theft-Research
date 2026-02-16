import pandas as pd
import sys

def analyze_state(df, state_name):
    print(f"\n--- Analyzing {state_name} ---")
    state_df = df[df['State'].astype(str).str.contains(state_name, case=False, na=False)].copy()
    
    # Pre-2022 Columns
    pre_cols = ['Theft_2017', 'Theft_2018', 'Theft_2019']
    # Post-2022 Columns
    post_cols = ['Theft_2022', 'Theft_2023']
    
    state_df['Has_Pre'] = state_df[pre_cols].notna().any(axis=1)
    state_df['Has_Post'] = state_df[post_cols].notna().any(axis=1)
    
    # Rows with ONLY Pre data (Potential Old Names)
    only_pre = state_df[state_df['Has_Pre'] & ~state_df['Has_Post']]['District'].unique()
    
    # Rows with ONLY Post data (Potential New Names)
    only_post = state_df[~state_df['Has_Pre'] & state_df['Has_Post']]['District'].unique()
    
    print(f"Districts with data ONLY for 2017-2019 (Likely Old Names):")
    for d in sorted(only_pre):
        print(f"  - {d}")
        
    print(f"Districts with data ONLY for 2022-2023 (Likely New Names):")
    for d in sorted(only_post):
        print(f"  - {d}")

def main():
    try:
        df = pd.read_csv('data/theft_data_extracted.csv')
    except FileNotFoundError:
        print("data/theft_data_extracted.csv not found.")
        return

    states_to_check = sorted(df['State'].dropna().unique())
    
    for state in states_to_check:
        analyze_state(df, state)

if __name__ == "__main__":
    main()
