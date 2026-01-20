import psutil, time, struct, threading, json, os
import serial, serial.tools.list_ports
import pynvml
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

# --- SETTINGS ---
BAUD = 115200
CONFIG_FILE = "config.json"

running = False
ser = None
selected_port = None
icon = None 

# ---------- GPU (NVIDIA ONLY) ----------
USE_NVIDIA = False
gpu_info_text = "GPU: Not Detected"
try:
    pynvml.nvmlInit()
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    gpu_name = pynvml.nvmlDeviceGetName(gpu_handle)
    gpu_info_text = f"GPU: {gpu_name}"
    USE_NVIDIA = True
except:
    gpu_info_text = "GPU: NVIDIA not found"

def load_config():
    global selected_port
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                selected_port = data.get("port")
        except: pass

def save_config():
    if selected_port:
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"port": selected_port}, f)
        except: pass

def get_stats():
    cpu = int(psutil.cpu_percent())
    ram = int(psutil.virtual_memory().percent)
    gpu_load, gpu_temp = 0, 0
    
    if USE_NVIDIA:
        try:
            u = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle)
            gpu_load = int(u.gpu)
            gpu_temp = int(pynvml.nvmlDeviceGetTemperature(gpu_handle, pynvml.NVML_TEMPERATURE_GPU))
        except: pass
    
    return min(cpu, 255), min(ram, 255), min(gpu_load, 255), min(gpu_temp, 255)

def send_loop():
    global running, ser
    while running:
        try:
            if ser and ser.is_open:
                packet = struct.pack("BBBB", *get_stats())
                ser.write(packet)
                time.sleep(1)
            else:
                running = False
                update_icon_color("red")
        except:
            running = False
            update_icon_color("red")
            if ser: ser.close()

def set_port(icon, item):
    global selected_port
    selected_port = str(item)
    save_config()
    if running:
        stop_monitor()
        start_monitor()

def start_monitor(icon=None, item=None):
    global ser, running
    if not selected_port: return
    try:
        ser = serial.Serial(selected_port, BAUD, timeout=1)
        ser.setDTR(True) 
        ser.setRTS(True)
        running = True
        update_icon_color("green")
        threading.Thread(target=send_loop, daemon=True).start()
    except:
        stop_monitor()

def stop_monitor(icon=None, item=None):
    global running, ser
    running = False
    if ser:
        try: ser.close()
        except: pass
    update_icon_color("red")

def quit_app(icon, item):
    stop_monitor()
    icon.stop()

def create_image(color):
    image = Image.new('RGB', (64, 64), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, 63, 63), outline="white", width=2)
    dc.text((15, 10), "PC", fill="white")
    dc.ellipse((22, 35, 42, 55), fill=color)
    return image

def update_icon_color(status):
    if icon: icon.icon = create_image(status)

def get_ports_menu():
    menu_items = []
    for p in serial.tools.list_ports.comports():
        is_checked = lambda item, p_name=p.device: selected_port == p_name
        menu_items.append(item(p.device, set_port, checked=is_checked))
    if not menu_items:
        menu_items.append(item("No Ports Found", lambda: None, enabled=False))
    return pystray.Menu(*menu_items)

def build_main_menu():
    return pystray.Menu(
        item(gpu_info_text, lambda: None, enabled=False), 
        pystray.Menu.SEPARATOR,
        item('Select Port', get_ports_menu()),
        item('Start Monitoring', start_monitor, checked=lambda item: running),
        item('Stop', stop_monitor, checked=lambda item: not running),
        pystray.Menu.SEPARATOR,
        item('Exit', quit_app)
    )

if __name__ == "__main__":
    load_config()
    if selected_port:
        threading.Thread(target=start_monitor, daemon=True).start()
    
    initial_color = "green" if selected_port else "red"
    icon = pystray.Icon("PC Monitor", create_image(initial_color), "PC Stats Monitor", menu=build_main_menu())
    icon.run()