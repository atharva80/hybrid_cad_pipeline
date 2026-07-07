# ATLAS ↔ SimLab: End-to-End API Workflow Deep Dive

This document explains the precise step-by-step lifecycle of the system, bridging a modern PySide6 desktop application (ATLAS) with a closed-source C++ monolithic application (SimLab) using a custom TCP Socket architecture.

---

## 1. The CAD Handoff ("Open in SimLab")

When you click **Open in SimLab** in the ATLAS UI, a few critical things happen to safely hand the CAD file over:

1. **Macro Generation:** The ATLAS app (`gui/app.py`) looks at the exact file path of your exported STEP file. It writes a temporary python script into the `_cache/` folder called `simlab_import_macro.py`. This script contains the native `simlab` API commands to set the unit system and import that specific STEP file.
2. **Process Detachment:** ATLAS uses Python's `subprocess.Popen` to launch `SimLab.bat` from your E: drive. It passes the `-auto` flag alongside the macro it just generated.
   - *Crucially*, it uses the `DETACHED_PROCESS` flag. This severs the connection between ATLAS and SimLab at the OS level, meaning if ATLAS crashes, SimLab stays alive.
3. **Execution:** SimLab boots, immediately executes the macro to draw the CAD geometry on screen, and then returns control to the user. 

---

## 2. Booting the Listener ("ATLAS API" Button)

SimLab is now open and the CAD is loaded, but it is completely deaf to the outside world. When you click your custom **ATLAS API** Ribbon button, it executes the `simlab_api_server.py` script.

1. **The Daemon Server:** The script immediately spins up a background thread (a "Daemon") that opens a raw TCP Socket on `localhost:5050`. This thread sits silently and listens for incoming network connections.
2. **The Memory Queue:** It initializes a `queue.Queue()`. This is a special, thread-safe data structure. Because SimLab's C++ core will crash if a background thread tries to mesh something, the background server needs a safe way to hand jobs to the main thread.
3. **The UI & Polling Loop:** The script renders the sleek light-mode Tkinter badge on the main thread. At the same time, it starts a recursive `poll()` function using `tkinter.after(500)`. Every 500 milliseconds, the main thread checks the Memory Queue to see if the background thread put any jobs in it.

---

## 3. Preparing the Mesh Job ("Mesh" Button)

Back in the ATLAS app, you select "Tet10", "4.0mm", and click **Mesh** on a specific component (e.g., `OUTER_RACE_1`).

1. **Template Selection:** ATLAS looks at the component name and determines which base template to use (e.g., `EXISTING_SCRIPTS/MESHING/mesh_races.py`). It reads this entire `.py` file into memory as a giant string.
2. **Dynamic Regex Injection:** The template has hardcoded values, so ATLAS uses Regular Expressions (Regex) to surgically modify the code string in memory:
   - It finds `BODY_NAME = "..."` and replaces it with `BODY_NAME = "OUTER_RACE_1"`.
   - It finds variables like `mesh_size = ...` and replaces them with `4.0`.
   - It finds broken `C:/` paths for the CSV files and replaces them with the correct dynamic `_ROOT` paths on your F: drive.
3. **The Payload:** ATLAS now has a fully complete, customized Python script sitting in memory. It wraps this string into a JSON dictionary:
   ```json
   {
       "code": "import simlab\nBODY_NAME = 'OUTER_RACE_1'\nmesh_size = 4.0\n..."
   }
   ```

---

## 4. The IPC Bridge (Sending & Executing)

1. **The Network Request:** ATLAS opens a TCP socket connection to `127.0.0.1:5050` (the exact port SimLab is listening on), serializes the JSON payload into bytes, fires it across the network, and immediately closes the connection.
2. **Receiving the Job:** Inside SimLab, the background daemon thread wakes up, receives the bytes, decodes the JSON, extracts the `"code"` string, and drops it into the thread-safe Memory Queue.
3. **Execution (The Main Thread):** 
   - A few milliseconds later, the Tkinter `poll()` loop checks the queue and finds the job.
   - Because `simlab.executeFile()` requires a physical file (it cannot execute strings from memory reliably), the script quickly saves the string to `_cache/_active_job.py`.
   - It tells SimLab to execute that file. **Because this is happening on the main UI thread, SimLab's C++ core accepts the command perfectly and meshes the part.**
   - Once the mesh is done, it deletes `_active_job.py` and goes back to polling!

### Why this architecture is brilliant:
By moving the actual file creation *inside* the listener (rather than ATLAS dropping files into a folder), you completely eliminate Windows file-lock collisions. ATLAS and SimLab never fight over read/write access to the same file. ATLAS just sends data, and SimLab handles the file logic internally!
