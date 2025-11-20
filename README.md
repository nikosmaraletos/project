# ChEMBL MCP Integration

## Overview
This project implements a lightweight MCP (Modular Content Protocol) service that retrieves structured drug information from the ChEMBL database and makes it available to any MCP-compatible client.  
The service exposes clean endpoints for retrieving drugs, indications, mechanisms, and related metadata.

The goal is to provide a reproducible, modular pipeline that pulls information from ChEMBL and returns it in a structured format suitable for further analysis or integration into larger systems.

---

## Folder Structure
project/
│── fastmcp_chembl_server.py # MCP server implementation
│── fastmcp_chembl_client.py # Simple client to test MCP calls
│── requirements.txt
│── README.md
│── .gitignore

yaml
Copy code

---

## Installation & Setup

### 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate # macOS / Linux

shell
Copy code

### 2. Install dependencies
pip install -r requirements.txt

yaml
Copy code

---

## How it Works

### ✦ Data Source: ChEMBL
The service connects to the ChEMBL public REST API to retrieve:
- Drug name
- ChEMBL ID
- Indications  
- Mechanisms of action  
- Molecule properties  
- Synonyms & classification  
- Related targets and pathways  

All responses are returned in structured JSON for easy consumption.

### ✦ MCP Server
- Runs on a lightweight FastAPI server  
- Exposes a single MCP tool:  
  `get_drug_info(drug_name)`  
- Handles the API request, normalizes fields, and returns clean output

### ✦ Client
A simple Python client is included to test the MCP server call using a local MCP-enabled environment.

---

## Running the Server

### Start the MCP server
python fastmcp_chembl_server.py

powershell
Copy code

The server will start at:

http://127.0.0.1:8001

yaml
Copy code

---

## Running the Client (Manual Test)

Open a second terminal:

python fastmcp_chembl_client.py

yaml
Copy code

You will be asked for a drug name (e.g., "apremilast"), and the client will request the MCP server and print the structured output.

---

## Example Output (Apremilast)

{
"drug_name": "Apremilast",
"chembl_id": "CHEMBL1908367",
"indications": ["Psoriatic arthritis", "Plaque psoriasis"],
"mechanism_of_action": "PDE4 inhibitor",
"targets": ["Enzyme PDE4"],
"properties": {
"molecular_weight": 460.5,
"alogp": 2.6
}
}

yaml
Copy code

---

## Requirements
All project dependencies are included in:
requirements.txt

csharp
Copy code

Install with:
pip install -r requirements.txt

yaml
Copy code

---

## Notes
- The server is modular and can be extended with additional MCP tools.
- The project is kept minimal for clarity and reproducibility.
# project
