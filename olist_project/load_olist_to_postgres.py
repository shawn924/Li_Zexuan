import os
import zipfile
import argparse
import pandas as pd
from sqlalchemy import create_engine,text

def unzip_file(zip_path, extract_dir):
    print(f"[Extracting] {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"[Done] Extracted to {extract_dir}")

def load_csv_to_postgres(csv_path, table_name, engine):
    print(f"Loading {csv_path} into table '{table_name}'...")
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        print(f"[Done] Loaded '{table_name}'")
    except Exception as e:
        print(f"[Error] Failed to load {csv_path}: {e}")

def load_all_csvs_to_postgres(extract_dir, engine):
    print(f"[Loading] CSVs from {extract_dir} into PostgreSQL...")
    for filename in os.listdir(extract_dir):
        if filename.endswith(".csv"):
            table_name = filename.replace(".csv", "").lower()
            file_path = os.path.join(extract_dir, filename)
            load_csv_to_postgres(file_path, table_name, engine)
    print("[All done] Data loaded.")

def main():
    parser = argparse.ArgumentParser(description="Load CSVs from ZIP into PostgreSQL")
    parser.add_argument("--postgres-uri", required=True, help="SQLAlchemy Postgres URI")
    parser.add_argument("--zip-file", required=True, help="Path to the ZIP file")
    parser.add_argument("--extract-dir", required=True, help="Directory to extract ZIP contents into")
    args = parser.parse_args()

    # Create engine
    print("[Connecting] to PostgreSQL...")
    engine = create_engine(args.postgres_uri)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[Connected] successfully.")
    except Exception as e:
        print(f"[Error] Database connection failed: {e}")
        return

    # Unzip and load data
    unzip_file(args.zip_file, args.extract_dir)
    load_all_csvs_to_postgres(args.extract_dir, engine)

if __name__ == "__main__":
    main()
