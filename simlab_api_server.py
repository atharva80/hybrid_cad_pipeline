import sys, os, time, threading, socket, json, queue
import tkinter as tk
import simlab

# Dynamically resolve the project root, but force the ATHARVA workspace if it exists
_ROOT = r"F:\02.CAE\ATHARVA\hybrid_cad_pipeline"
if not os.path.exists(_ROOT):
    _ROOT = os.path.dirname(os.path.abspath(__file__))

_CACHE_DIR = os.path.join(_ROOT, "_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

job_queue = queue.Queue()

def api_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 5050))
    server.listen(5)
    while True:
        try:
            conn, addr = server.accept()
            with conn:
                data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    data += chunk
                if data:
                    try:
                        payload = json.loads(data.decode('utf-8'))
                        job_queue.put(payload)
                    except Exception as parse_e:
                        print("Failed to parse JSON payload:", parse_e)
        except Exception as e:
            print("Socket accept error:", e)

class LiveMeshBadge(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ATLAS API")
        
        # Position it nicely in the top left with a sleek size
        self.geometry("260x60+60+60") 
        self.attributes('-topmost', True)
        # Use a crisp gray border matching SimLab's native windows
        self.configure(bg='#CCCCCC') 
        self.overrideredirect(True)
        
        # Inner frame (SimLab crisp white theme)
        inner = tk.Frame(self, bg="#FFFFFF")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Top branding accent (Altair Blue)
        banner = tk.Frame(inner, bg="#005A9C", height=3)
        banner.pack(fill="x", side="top")
        
        # Custom drawn status dot
        self.canvas = tk.Canvas(inner, width=14, height=14, bg="#FFFFFF", highlightthickness=0)
        self.canvas.place(x=15, y=23)
        self.dot = self.canvas.create_oval(2, 2, 12, 12, fill="#2ECC71", outline="#1F8B4C")
        
        # Native Light-Mode Typography
        lbl_title = tk.Label(inner, text="ATLAS IPC Bridge Active", font=("Segoe UI", 9, "bold"), fg="#333333", bg="#FFFFFF")
        lbl_title.place(x=36, y=11)
        
        self.lbl_status = tk.Label(inner, text="Listening on localhost:5050", font=("Segoe UI", 8), fg="#666666", bg="#FFFFFF")
        self.lbl_status.place(x=36, y=31)
        
        # Interactive Close Button (removed cursor property for SimLab compatibility)
        close_btn = tk.Label(inner, text="✕", font=("Segoe UI", 10), fg="#999999", bg="#FFFFFF")
        close_btn.place(x=235, y=10)
        close_btn.bind("<Button-1>", lambda e: self.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg="#D32F2F"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg="#999999"))

        # Make the borderless window draggable
        inner.bind("<ButtonPress-1>", self.start_move)
        inner.bind("<B1-Motion>", self.do_move)
        lbl_title.bind("<ButtonPress-1>", self.start_move)
        lbl_title.bind("<B1-Motion>", self.do_move)
        
        # Start TCP Server on background thread
        threading.Thread(target=api_server, daemon=True).start()
        
        # Start safely polling the memory queue
        self.after(500, self.poll)
        
        # Start pulsing animation
        self.pulse_state = False
        self.after(800, self.pulse_dot)
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def pulse_dot(self):
        # Pulse between bright green and dim green
        color = "#28A745" if self.pulse_state else "#175E27"
        self.canvas.itemconfig(self.dot, fill=color)
        self.pulse_state = not self.pulse_state
        self.after(800, self.pulse_dot)
        
    def log(self, msg):
        log_path = os.path.join(_CACHE_DIR, "api_server.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [SimLab API] {msg}\n")
        except: pass

    def poll(self):
        try:
            job = job_queue.get_nowait()
            if job:
                task_type = job.get("task_type", "mesh")
                self.log(f"Received job type: {task_type}")
                if "code" in job:
                    code = job["code"]
                elif task_type == "create_contact":
                    contact_name = job.get("contact_name")
                    config = job.get("config", {})
                    scripts_dir = job.get("scripts_dir", os.path.join(_ROOT, "contact_templates").replace('\\', '/'))
                    module_name = "create_contact"
                    self.log(f"Processing contact: {contact_name}")
                    
                    code = f"""import sys, os
scripts_dir = r"{scripts_dir}"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import {module_name}
import importlib
importlib.reload({module_name})

CONFIG = {repr(config)}
{module_name}.run("{contact_name}", CONFIG)
"""
                else:
                    script_name = job.get("script_name")
                    body_name = job.get("body_name")
                    config = job.get("config", {})
                    scripts_dir = job.get("scripts_dir", os.path.join(_ROOT, "mesh_templates").replace('\\', '/'))
                    
                    module_name = script_name.replace(".py", "")
                    self.log(f"Processing mesh: {body_name} with {script_name}")
                    
                    code = f"""import sys, os
sys.dont_write_bytecode = True
scripts_dir = r"{scripts_dir}"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import {module_name}
import importlib
importlib.reload({module_name})

CONFIG = {repr(config)}
{module_name}.run("{body_name}", CONFIG)
"""
                
                tmp_job = os.path.join(_CACHE_DIR, "_active_job.py").replace('\\', '/')
                self.log(f"Writing runner script to {tmp_job}")
                with open(tmp_job, "w", encoding="utf-8") as f:
                    f.write(code)
                try: 
                    self.log(f"-> EXECUTING MACRO IN SIMLAB KERNEL: {module_name}")
                    simlab.executeFile(tmp_job)
                    self.log("<- EXECUTION COMPLETED SUCCESSFULLY")
                except Exception as e: 
                    self.log(f"<- EXECUTION FAILED: {e}")
                finally:
                    try: os.remove(tmp_job)
                    except: pass
        except queue.Empty:
            pass
            
        self.after(500, self.poll)

if __name__ == "__main__":
    badge = LiveMeshBadge()
    badge.mainloop()
