import pandas as pd
try:
    df = pd.read_excel('data/IPC_Crimes_2022.xlsx', nrows=5)
    print("Columns 2022:", df.columns.tolist())
    print(df.head(2))
    
    df23 = pd.read_excel('data/IPC_Crimes_2023.xlsx', nrows=5)
    print("Columns 2023:", df23.columns.tolist())
except Exception as e:
    print(e)
