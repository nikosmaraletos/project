import asyncio
from fastmcp import Client

MCP_URL = "http://127.0.0.1:8001/mcp"


async def main():
    user_prompt = input("Δώσε ChEMBL query: π.χ. 'imatinib', 'EGFR inhibitor'\n> ").strip()

    async with Client(MCP_URL) as client:
        tools = await client.list_tools()
        print(f"\n🔧 Διαθέσιμα εργαλεία MCP: {[t.name for t in tools]}\n")

        print("🔍 Εκτελώ αναζήτηση...")
        sr = await client.call_tool("search_molecules", {"q": user_prompt, "limit": 10})

        if hasattr(sr, "structured_content") and "result" in sr.structured_content:
            hits = sr.structured_content["result"]
        elif hasattr(sr, "data"):
            hits = sr.data
        else:
            hits = []

        if not hits:
            print("⚠️ Δεν βρέθηκαν μόρια.")
            return

        print("\n📄 Αποτελέσματα ChEMBL (σύνοψη):")
        for i, h in enumerate(hits, 1):
            print(f"{i}. {h.get('pref_name') or '—'} | id={h.get('chembl_id')} | type={h.get('molecule_type') or '—'} | phase={h.get('max_phase')}")

        # ✅ Ζήτα επιλογή hit για λεπτομέρειες
        choice = input("\nΠοιο # θες να δούμε σε λεπτομέρεια; (Enter για 1)\n> ").strip()
        idx = 1
        if choice.isdigit():
            idx = max(1, min(int(choice), len(hits)))

        first = hits[idx - 1]
        cid = first.get("chembl_id")

        if not cid:
            print("ℹ️ Δεν υπάρχει έγκυρο chembl_id για αυτό το αποτέλεσμα.")
            return

        print(f"\n— Φέρνω λεπτομέρειες για: {cid} …\n")
        det = await client.call_tool("get_molecule_details", {"chembl_id": cid})

        if hasattr(det, "structured_content") and "result" in det.structured_content:
            details = det.structured_content["result"]
        elif hasattr(det, "data"):
            details = det.data
        else:
            details = {}

        if not details:
            print("ℹ️ Δεν επιστράφηκαν λεπτομέρειες.")
            return

        print("🧪 Λεπτομέρειες:")
        print(f"ChEMBL ID:   {details.get('chembl_id')}")
        print(f"Name:        {details.get('pref_name')}")
        print(f"Type:        {details.get('molecule_type')}")
        print(f"Max Phase:   {details.get('max_phase')}\n")

        mechs = details.get("mechanisms") or []
        if mechs:
            print("Mechanisms (έως 5):")
            for m in mechs[:5]:
                moa = m.get("mechanism_of_action") or "—"
                tgt = m.get("target_name") or m.get("target_chembl_id") or "—"
                print(f" • {moa} (target: {tgt})")

        inds = details.get("indications") or []
        if inds:
            print("\nIndications (έως 5):")
            for ind in inds[:5]:
                term = ind.get("efo_term") or ind.get("mesh_heading") or "—"
                print(f" • {term}")


if __name__ == "__main__":
    asyncio.run(main())

