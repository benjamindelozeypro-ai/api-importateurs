from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import pandas as pd

app = FastAPI()

COLONNE_CIBLE = "Site Officiel"


class LireProchaineLigneRequest(BaseModel):
    file_path: str


class MettreAJourExcelRequest(BaseModel):
    file_path: str
    index: int
    resultat_action: str


@app.post("/lire_prochaine_ligne")
def lire_prochaine_ligne(payload: LireProchaineLigneRequest):
    file_path = payload.file_path

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": f"Fichier introuvable : {file_path}"
        }

    df = pd.read_excel(file_path)

    if COLONNE_CIBLE not in df.columns:
        df[COLONNE_CIBLE] = ""
        df.to_excel(file_path, index=False)

    df = pd.read_excel(file_path)
    masque_vide = df[COLONNE_CIBLE].astype(str).str.strip() == ""
    if not masque_vide.any():
        return {
            "status": "complete",
            "message": "Toutes les lignes ont été traitées."
        }

    next_index = masque_vide[masque_vide].index.min()
    row = df.loc[next_index]

    entreprise = str(row.get("Entreprise", "N/A")).strip()
    pays = str(row.get("Pays", "N/A")).strip()
    ville = str(row.get("Ville", "")).strip()

    return {
        "status": "success",
        "index": int(next_index),
        "entreprise": entreprise,
        "pays": pays,
        "ville": ville
    }


@app.post("/mettre_a_jour_excel")
def mettre_a_jour_excel(payload: MettreAJourExcelRequest):
    file_path = payload.file_path
    index = payload.index
    resultat_action = payload.resultat_action

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": f"Fichier introuvable : {file_path}"
        }

    df = pd.read_excel(file_path)

    if COLONNE_CIBLE not in df.columns:
        df[COLONNE_CIBLE] = ""

    if index not in df.index:
        return {
            "status": "error",
            "message": f"Index {index} hors limites."
        }

    df.loc[index, COLONNE_CIBLE] = resultat_action
    df.to_excel(file_path, index=False)

    return {
        "status": "success",
        "message": f"Ligne {index} mise à jour avec succès."
    }
