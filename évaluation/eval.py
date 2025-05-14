from CEA_WD_Evaluator import CEA_Evaluator
from CTA_WD_Evaluator import CTA_Evaluator
from CPA_WD_Evaluator import CPA_Evaluator

# === Chemins ===
gt_path = "./gt"
submission_path = "./outputs"

cea_eval = CEA_Evaluator(f"{gt_path}/cea_gt.csv")
cta_eval = CTA_Evaluator(f"{gt_path}/cta_gt.csv")
cpa_eval = CPA_Evaluator(f"{gt_path}/cpa_gt.csv")

# Créer un payload
cea_payload = {"submission_file_path": f"{submission_path}/CEA.csv"}
cta_payload = {"submission_file_path": f"{submission_path}/CTA.csv"}
cpa_payload = {"submission_file_path": f"{submission_path}/CPA.csv"}

# Évaluation
print("\n🧪 Évaluation CEA")
cea_eval._evaluate(cea_payload)

print("\n🧪 Évaluation CTA")
cta_eval._evaluate(cta_payload)

print("\n🧪 Évaluation CPA")
cpa_eval._evaluate(cpa_payload)
