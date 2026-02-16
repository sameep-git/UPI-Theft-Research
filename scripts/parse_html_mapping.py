import pandas as pd
import re
from pathlib import Path

html_path = 'data/India Districts.html'

def parse_html_table(file_path):
    with open(file_path, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    
    # Simple regex to extract District and HASC code
    # Pattern looks for: <td>DistrictName</td><td><code>HASC</code></td>
    # or similar structure based on the snippet:
    # <tr class="o"><td>Adilabad</td><td><code>IN.TG.AD</code></td>...
    
    pattern = r'<td>(.*?)</td><td><code>(.*?)</code></td>'
    matches = re.findall(pattern, content)
    
    data = []
    for district, hasc in matches:
        data.append({'District': district.strip(), 'HASC': hasc.strip()})
        
    return pd.DataFrame(data)

df = parse_html_table(html_path)
print(f"Extracted {len(df)} records from HTML.")
print(df.head())

# Save to CSV for easy use in matching script
df.to_csv('data/html_hasc_mapping.csv', index=False)
