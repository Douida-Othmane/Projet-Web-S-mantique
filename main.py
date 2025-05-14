import os
import pandas as pd
from tqdm import tqdm
import requests
from collections import Counter

# Constants
TABLES_FOLDER = "WikidataTables2024R1/DataSets/Valid/tables"
CEA_RESULTS_FILE = "outputs/CEA.csv"
CTA_RESULTS_FILE = "outputs/CTA.csv"
CPA_RESULTS_FILE = "outputs/CPA.csv"
CEA_TARGETS_FILE = "WikidataTables2024R1/DataSets/Valid/targets/cea_targets.csv"
CTA_TARGETS_FILE = "WikidataTables2024R1/DataSets/Valid/targets/cta_targets.csv"
CPA_TARGETS_FILE = "WikidataTables2024R1/DataSets/Valid/targets/cpa_targets.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

# Load CSV safely
def read_csv(filepath):
    return pd.read_csv(filepath, header=None, names=["TableID", "ColumnID", "RowID"] if 'cea' in filepath else ["TableID", "ColumnID"] if 'cta' in filepath else ["TableID", "Col0", "Col1"])

# Load tables
def load_table(table_id):
    filepath = os.path.join(TABLES_FOLDER, f"{table_id}.csv")
    with open(filepath, encoding="utf-8") as f:
        lines = [line.strip().split(",") for line in f.readlines()]
    return lines

# Query Wikidata SPARQL

def get_wikidata_types(qid):
    query = f"""
    SELECT ?type WHERE {{
      wd:{qid} wdt:P31 ?type .
    }}
    """
    try:
        response = requests.get(WIKIDATA_SPARQL_URL, headers=HEADERS, params={"query": query, "format": "json"}, timeout=20)
        results = response.json()["results"]["bindings"]
        return [r["type"]["value"].split("/")[-1] for r in results]
    except:
        return []

def get_common_type(qids):
    types = []
    for qid in qids:
        types.extend(get_wikidata_types(qid))
    if not types:
        return None
    return Counter(types).most_common(1)[0][0]


def get_wikidata_property(qid1, qid2):
    query = f"""
    SELECT ?p WHERE {{
      wd:{qid1} ?p wd:{qid2} .
    }}
    """
    try:
        response = requests.get(WIKIDATA_SPARQL_URL, headers=HEADERS, params={"query": query, "format": "json"}, timeout=20)
        results = response.json()["results"]["bindings"]
        props = [r["p"]["value"].split("/")[-1] for r in results if "/prop/direct/" in r["p"]["value"]]
        return props[0] if props else None
    except:
        return None

# Main process

def process_cea():
    cea_targets = read_csv(CEA_TARGETS_FILE)
    results = []
    grouped = cea_targets.groupby("TableID")
    for table_id, group in tqdm(grouped, desc="Generating CEA"):
        table = load_table(table_id)
        for _, row in group.iterrows():
            col, row_idx = int(row["ColumnID"]), int(row["RowID"])
            try:
                val = table[row_idx][col]
                qid = search_entity(val)
                if qid:
                    results.append([table_id, col, row_idx, f"http://www.wikidata.org/entity/{qid}"])
            except:
                continue
    pd.DataFrame(results).to_csv(CEA_RESULTS_FILE, header=False, index=False)
    return results

def search_entity(label):
    try:
        url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&search={label}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        res = r.json()
        return res["search"][0]["id"] if res["search"] else None
    except:
        return None

def process_cta(cea_results):
    df = pd.DataFrame(cea_results, columns=["TableID", "ColumnID", "RowID", "Entity"])
    results = []
    for (table_id, col), group in tqdm(df.groupby(["TableID", "ColumnID"]), desc="Generating CTA"):
        qids = [ent.split("/")[-1] for ent in group["Entity"]]
        common_type = get_common_type(qids)
        if common_type:
            results.append([table_id, col, f"http://www.wikidata.org/entity/{common_type}"])
    pd.DataFrame(results).to_csv(CTA_RESULTS_FILE, header=False, index=False)
    return results

def process_cpa(cea_results):
    df = pd.DataFrame(cea_results, columns=["TableID", "ColumnID", "RowID", "Entity"])
    results = []
    for table_id, group in tqdm(df.groupby("TableID"), desc="Generating CPA"):
        entity_map = {}
        for _, row in group.iterrows():
            entity_map[(int(row["RowID"]), int(row["ColumnID"]))] = row["Entity"].split("/")[-1]
        columns = set(col for (_, col) in entity_map.keys())
        if len(columns) < 2:
            continue
        for c1 in columns:
            for c2 in columns:
                if c1 >= c2:
                    continue
                pairs = [(entity_map.get((r, c1)), entity_map.get((r, c2))) for r in range(max(row["RowID"] for row in group.itertuples())) if entity_map.get((r, c1)) and entity_map.get((r, c2))]
                props = [get_wikidata_property(q1, q2) for q1, q2 in pairs if get_wikidata_property(q1, q2)]
                if props:
                    prop = Counter(props).most_common(1)[0][0]
                    results.append([table_id, c1, c2, f"http://www.wikidata.org/entity/{prop}"])
    pd.DataFrame(results).to_csv(CPA_RESULTS_FILE, header=False, index=False)
    return results

# Main Execution
if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    cea_res = process_cea()
    cta_res = process_cta(cea_res)
    cpa_res = process_cpa(cea_res)
    print("✅ Fichiers générés dans 'outputs/' :")
    print(" - CEA.csv")
    print(" - CTA.csv")
    print(" - CPA.csv")
