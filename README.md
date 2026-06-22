# Hybrid CAD Parsing Pipeline

This directory contains the inference engine for the Hybrid CAD Parsing Pipeline. It processes unlabelled CAD assemblies (.STEP format), isolates the Stator and Shaft using geometric heuristics, and applies an XGBoost model to classify surrounding components (Covers, Rotors, Bearings, PCBs, EPS Packaging, Canopies, etc.).

Outputs:
1. **Rendered PNGs**: A 3D render of each identified component.
2. **Flattened Labeled CAD**: A `{Original_Name}_NAMED.step` file with a flattened assembly structure, where solids are renamed to their classified component names (e.g., `STATOR`, `TOP_COVER`, `Solid_1`).

---

## Setup Instructions (Windows)

Due to dependencies on C++ CAD libraries, this project requires Conda. Standard pip installations for `pythonocc-core` are generally not supported on Windows.

### 1. Install Conda
Install [Miniconda for Windows](https://docs.conda.io/en/latest/miniconda.html) if not already available on your system.

### 2. Create the Environment
Open the Anaconda Prompt, navigate to the project directory, and create the environment:

```cmd
cd path\to\hybrid_cad_pipeline
conda env create -f environment.yml
```
This process downloads OpenCASCADE, PyVista, XGBoost, and other required packages.

### 3. Activate the Environment
The environment must be activated before running any scripts:
```cmd
conda activate cv_datagen
```

---

## Usage

The `main.py` script serves as the primary entry point. It requires one input path (`--in`) and at least one output argument (`--imgs` or `--out`).

### 1. Process a Single File
Run the pipeline on a single STEP file, generate PNG renders, and export the labeled STEP file:
```cmd
python main.py --in "C:\path\to\Motor.STEP" --imgs .\output_renders --out .\output_cads
```

### 2. Process a Directory (Batch Mode)
Run the pipeline on all STEP files within a specified directory by adding the `--batch` flag.
Note: When using `--imgs` in batch mode, renders are grouped into sub-folders automatically named after each assembly.
```cmd
python main.py --batch --in "C:\path\to\CAD_Folder" --imgs .\output_renders --out .\output_cads
```

### 3. Target the PCB Box
If the CAD model contains a secondary enclosing top PCB box, use the `--box` modifier flag to trigger explicit heuristic searching for it:
```cmd
python main.py --in "C:\path\to\Motor.STEP" --imgs .\output_renders --box
```

### 4. Generate Images Only
Process a file and output only visual renders without exporting a new STEP file:
```cmd
python main.py --in "C:\path\to\Motor.STEP" --imgs .\output_renders
```

### 5. Explainability / Debugging
To debug misclassifications or analyze feature importance, generate SHAP plots for the trained models:
```cmd
python main.py --explain
```

---

## Directory Structure
*   `main.py` — Primary CLI script.
*   `environment.yml` — Conda environment and dependency configurations.
*   `core/` — OpenCASCADE topology extractors (`step_loader.py`).
*   `heuristics/` — Mathematical rule sets for filtering component candidates (Phases 1-6).
*   `engine/` — Inference logic (`inference_engine.py`) and CAD export/flattening tools (`step_exporter.py`).
*   `models/` — Trained XGBoost model weights (.json files).
