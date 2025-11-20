import requests
from fastmcp import FastMCP
from typing import Dict, Any, List

mcp = FastMCP(
    name="ChEMBL_MCP",
    instructions=(
        "Search molecules on ChEMBL and fetch details (mechanism, indications) "
        "via the ChEMBL REST API under the MCP framework."
    ),
    log_level="DEBUG",
    host="127.0.0.1",
    port=8001,
)

BASE = "https://www.ebi.ac.uk/chembl/api/data"
HEADERS = {"Accept": "application/json"}


def _safe_get(d: Dict[str, Any], *path, default=None):
    cur = d
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur


@mcp.tool()
def search_molecules(q: str, limit: int = 10) -> Dict[str, Any]:
    """
    🔎 Search ChEMBL molecules by free-text query.
    """
    try:
        params = {
            "q": q,
            "limit": limit,
            "page_size": limit,
        }
        resp = requests.get(f"{BASE}/molecule/search", params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        items: List[Dict[str, Any]] = (
            data.get("molecules")
            or data.get("molecule")
            or data.get("results")
            or []
        )

        out = []
        for m in items[:limit]:
            chembl_id = m.get("molecule_chembl_id") or m.get("chembl_id") or m.get("molecule")
            pref_name = m.get("pref_name") or m.get("molecule_pref_name")
            molecule_type = m.get("molecule_type")
            max_phase = m.get("max_phase")
            canonical_smiles = _safe_get(m, "molecule_structures", "canonical_smiles")
            inchi_key = _safe_get(m, "molecule_structures", "standard_inchi_key")

            out.append({
                "chembl_id": chembl_id,
                "pref_name": pref_name,
                "molecule_type": molecule_type,
                "max_phase": max_phase,
                "canonical_smiles": canonical_smiles,
                "inchi_key": inchi_key,
            })

        return {"result": out}
    except Exception as e:
        return {"result": [], "error": str(e)}


@mcp.tool()
def get_molecule_details(chembl_id: str) -> Dict[str, Any]:
    """
    🧪 Fetch detailed information for a molecule by ChEMBL ID.
    """
    try:
        r_mol = requests.get(f"{BASE}/molecule/{chembl_id}", headers=HEADERS, timeout=30)
        r_mol.raise_for_status()
        mol = r_mol.json()

        result: Dict[str, Any] = {
            "chembl_id": mol.get("molecule_chembl_id") or chembl_id,
            "pref_name": mol.get("pref_name"),
            "molecule_type": mol.get("molecule_type"),
            "max_phase": mol.get("max_phase"),
            "canonical_smiles": _safe_get(mol, "molecule_structures", "canonical_smiles"),
            "inchi_key": _safe_get(mol, "molecule_structures", "standard_inchi_key"),
        }

        try:
            r_mech = requests.get(
                f"{BASE}/mechanism",
                params={"molecule_chembl_id": chembl_id, "limit": 50, "page_size": 50},
                headers=HEADERS,
                timeout=30,
            )
            r_mech.raise_for_status()
            mech_json = r_mech.json()
            mech_items = (
                mech_json.get("mechanisms")
                or mech_json.get("mechanism")
                or mech_json.get("results")
                or []
            )
            result["mechanisms"] = [
                {
                    "mechanism_of_action": mi.get("mechanism_of_action"),
                    "target_name": mi.get("target_name"),
                    "target_chembl_id": mi.get("target_chembl_id"),
                }
                for mi in mech_items
            ]
        except Exception:
            result["mechanisms"] = []

        try:
            r_ind = requests.get(
                f"{BASE}/drug_indication",
                params={"molecule_chembl_id": chembl_id, "limit": 50, "page_size": 50},
                headers=HEADERS,
                timeout=30,
            )
            r_ind.raise_for_status()
            ind_json = r_ind.json()
            ind_items = (
                ind_json.get("drug_indications")
                or ind_json.get("indications")
                or ind_json.get("results")
                or []
            )
            result["indications"] = [
                {
                    "efo_id": ii.get("efo_id"),
                    "efo_term": ii.get("efo_term"),
                    "mesh_id": ii.get("mesh_id"),
                    "mesh_heading": ii.get("mesh_heading"),
                }
                for ii in ind_items
            ]
        except Exception:
            result["indications"] = []

        return {"result": result}

    except Exception as e:
        return {"result": {}, "error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="http")

