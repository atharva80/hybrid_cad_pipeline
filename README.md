# ATLAS: Hybrid CAD Parsing & Meshing Pipeline

ATLAS is a comprehensive Machine Learning and CAD processing application designed to automate the classification, parsing, and live meshing of motor assemblies in Altair SimLab.

It processes unlabelled CAD assemblies (.STEP format), isolates key components using geometric heuristics, classifies them using an XGBoost model, and communicates directly with Altair SimLab via a TCP socket to automate surface/volume meshing and contact generation.

---

## Windows Installation & Setup Guide

Since this pipeline requires OpenCASCADE (C++) for CAD parsing and communicates with Altair SimLab for meshing, please follow these steps carefully on a Windows machine.

### Prerequisites
1. **Altair SimLab 2025.1** (or compatible newer version) installed.
2. **Miniconda** (or Anaconda) installed.

### Step 1: Install the Conda Environment
Open your **Anaconda Prompt** as Administrator, navigate to the project directory, and create the environment:

```cmd
cd path\to\hybrid_cad_pipeline
conda env create -f config/environment.yml
```
*(Note: Standard `pip` installations for `pythonocc-core` are not supported on Windows. You must use Conda.)*

### Step 2: Launch the SimLab API Server
ATLAS communicates with SimLab using an internal IPC (Inter-Process Communication) socket.
1. Open **Altair SimLab 2025.1**.
2. Go to the **Advanced** tab in the top ribbon.
3. Click **Play** (or `Play Script`).
4. Browse to your `hybrid_cad_pipeline` folder and select **`simlab_api_server.py`**.
5. The SimLab console will print: `ATLAS IPC Bridge Active. Listening on localhost:5050`. Leave SimLab open.

### Step 3: Launch the ATLAS Interface
Go back to your Anaconda Prompt. Activate the environment and run the GUI entry point:

```cmd
conda activate cv_datagen
python gui/main.py
```

---

## Usage Workflow

1. **Import & Process:** In the ATLAS "Component Identification" tab, browse for a raw `.STEP` file. Click "Process / Import".
2. **Review & Edit:** Review the identified components. Manually tweak tags or remove unwanted bodies if needed.
3. **Automated Meshing:** Switch to the "Meshing" tab. Mesh individual components or hit "Mesh All". ATLAS will dispatch meshing macros to SimLab instantly.
4. **Define Contacts:** Switch to the "Contacts" tab. Verify suggested contacts and tolerances, then hit "Create All Contacts" to apply them in SimLab.

---

## Architecture

- `gui/main.py` — The core ATLAS PySide6 desktop application.
- `simlab_api_server.py` — The TCP socket listener running inside SimLab's Python environment.
- `mesh_templates/` — Granular meshing scripts injected dynamically into SimLab.
- `contact_templates/` — Automated contact creation logic.
- `config/contact_config/default_contacts.json` — Logic file defining which components should mate.
- `heuristics/` & `engine/` — Mathematical rule sets and XGBoost inference logic.
