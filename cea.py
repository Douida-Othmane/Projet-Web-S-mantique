import os
import pandas as pd
import requests
from tqdm import tqdm
from collections import Counter

# === CONFIGURATION ===
DATASET_PATH = "WikidataTables2024R1/DataSets/Valid"
TABLES_PATH = os.path.join(DATASET_PATH, "tables")
TARGETS_PATH = os.path.join(DATASET_PATH, "targets")

CEA_TARGETS_FILE = os.path.join(TARGETS_PATH, "cea_targets.csv")
CTA_TARGETS_FILE = os.path.join(TARGETS_PATH, "cta_targets.csv")
CPA_TARGETS_FILE = os.path.join(TARGETS_PATH, "cpa_targets.csv")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CEA_OUTPUT = os.path.join(OUTPUT_DIR, "CEA.csv")
CTA_OUTPUT = os.path.join(OUTPUT_DIR, "CTA.csv")
CPA_OUTPUT = os.path.join(OUTPUT_DIR, "CPA.csv")

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "SemanticWebProjectBot/1.0"}

# === WIKIDATA HELPERS ===
def search_entity(label):
    query = f"""
    SELECT ?item WHERE {{
      ?item rdfs:label "{label}"@en .
      FILTER(STRSTARTS(STR(?item), "http://www.wikidata.org/entity/"))
    }} LIMIT 1
    """
    try:
        response = requests.get(WIKIDATA_SPARQL_URL, params={"query": query, "format": "json"}, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            results = response.json()["results"]["bindings"]
            if results:
                return results[0]["item"]["value"]
    except Exception as e:
        print(f"❌ SPARQL error for '{label}': {e}")
    return None

# === PROCESSORS ===
def process_cea():
    print("📥 Start annotation tasks...")
    cea_targets = pd.read_csv(CEA_TARGETS_FILE, names=["TableID", "ColumnID", "RowID"], dtype=str)
    rows = []
    for _, target in tqdm(cea_targets.iterrows(), total=len(cea_targets), desc="CEA"):
        table_id, col_id, row_id = target["TableID"], int(target["ColumnID"]), int(target["RowID"])
        table_path = os.path.join(TABLES_PATH, f"{table_id}.csv")
        if not os.path.exists(table_path): continue
        try:
            df = pd.read_csv(table_path, header=None, dtype=str).fillna("")
            if row_id < len(df) and col_id < len(df.columns):
                value = df.iat[row_id, col_id].strip()
                if value:
                    entity = search_entity(value)
                    if entity:
                        rows.append([table_id, col_id, row_id, entity])
        except Exception as e:
            print(f"❌ Error CEA in {table_id}: {e}")
    pd.DataFrame(rows, columns=["TableID", "ColumnID", "RowID", "EntityID"]).to_csv(CEA_OUTPUT, index=False)



if __name__ == "__main__":
    process_cea()
    print("\n✅ Outputs saved to outputs/:\n - CEA.csv\n")
