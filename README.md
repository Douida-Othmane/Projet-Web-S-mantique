# 🌐 Projet Web Sémantique — Annotation de Tables avec Wikidata

## 👥 Auteurs
Othmane DOUDA

Achille BERGERET

Master ICE — Université Toulouse Jean Jaurès

## 🧩 Description

Ce projet consiste à enrichir automatiquement des tables anonymes au format CSV avec des annotations sémantiques provenant de **Wikidata**. L’objectif est d’associer :
- des cellules à des entités Wikidata (CEA),
- des colonnes à des classes Wikidata (CTA),
- et des relations entre colonnes à des propriétés Wikidata (CPA).

Le projet repose sur des requêtes SPARQL et l’utilisation de l’API de recherche de Wikidata.

---

## 📁 Structure du Projet

├── main.py # Script principal pour générer CEA, CTA et CPA

├── outputs/ # Contient les fichiers générés : CEA.csv, CTA.csv, CPA.csv

├── WikidataTables2024R1/

│ └── DataSets/

│ └── Valid/

│ ├── tables/ # Tables CSV anonymes

│ └── targets/ # Fichiers cibles à annoter : cea_targets.csv, cta_targets.csv, cpa_targets.csv

├── évaluation/

│ ├── CEA_WD_Evaluator.py

│ ├── CTA_WD_Evaluator.py

│ └── CPA_WD_Evaluator.py

└── README.md

---

## ⚙️ Installation et Prérequis

- Python ≥ 3.7
- Packages requis :
  ```bash
  pip install pandas tqdm requests
  ```

## 🚀 Exécution
Assurez-vous que la structure de fichiers est correcte, puis lancez :

  ```bash
python main.py
```
Les fichiers générés seront disponibles dans le dossier outputs/.

## 📊 Évaluation
Utilisez les scripts d’évaluation pour vérifier la qualité des annotations :
  ```bash
cd évaluation
python CEA_WD_Evaluator.py
python CTA_WD_Evaluator.py
python CPA_WD_Evaluator.py
```

## ✅ Résultats Obtenus

Tâche	  F1-Score	  Précision  	Rappel

CEA 	  0.060	      0.153	      0.037

CTA 	  0.027	      0.025	      0.029

CPA	 À compléter / à corriger selon les cas

## 📌 Remarques
Les chemins relatifs doivent être respectés pour le bon fonctionnement du script.

Certaines requêtes SPARQL peuvent échouer ou être lentes → gestion d'erreurs incluse.

Le fichier CPA dépend des résultats de CEA. Une faible couverture en CEA peut impacter CPA.

