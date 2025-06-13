import random
import time
import tkinter as tk
from threading import Thread

# Define IoT Device Classes
class SmartDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.status = False

    def toggle_status(self):
        self.status = not self.status

class SmartLight(SmartDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.brightness = 0

    def set_brightness(self, brightness):
        self.brightness = brightness

class Thermostat(SmartDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.temperature = 20

    def set_temperature(self, temperature):
        self.temperature = temperature

class SecurityCamera(SmartDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.motion_detected = False

    def detect_motion(self):
        self.motion_detected = random.choice([True, False])

# Automation System and Rule Classes
class AutomationSystem:
    def __init__(self):
        self.devices = []
        self.rules = []

    def add_device(self, device):
        self.devices.append(device)

    def add_rule(self, rule):
        self.rules.append(rule)

    def execute_rules(self):
        for rule in self.rules:
            rule.apply(self.devices)

class AutomationRule:
    def __init__(self, condition, action):
        self.condition = condition
        self.action = action

    def apply(self, devices):
        if self.condition(devices):
            self.action(devices)

# GUI Dashboard Class
class Dashboard:
    def __init__(self, root, system):
        self.root = root
        self.system = system
        self.root.title("Smart Home IoT Simulator")
        self.labels = []
        self.automation_on = True
        self.automation_text = tk.StringVar()
        self.automation_text.set("Random automation: ON")

        # Motion timer
        self.motion_timer = None  # Initialize motion timer here

        # Automation toggle button
        self.automation_btn = tk.Button(self.root, textvariable=self.automation_text, command=self.toggle_random)
        self.automation_btn.pack()

        self.device_listbox = tk.Listbox(root, width=50)
        self.device_listbox.pack()

        # Additional label for indication of light status
        self.light_status_label = tk.Label(root, text="")
        self.light_status_label.pack()

        self.create_device_controls()
        self.create_rule_controls()

        self.update_device_list()
        self.update_thread = Thread(target=self.simulation_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def toggle_random(self):
        self.automation_on = not self.automation_on
        self.automation_text.set("Random automation: {}".format("ON" if self.automation_on else "OFF"))

    def create_device_controls(self):
        for device in self.system.devices:
            if isinstance(device, SmartLight):
                self.create_light_controls(device)
                label_text = tk.StringVar()
                label_text.set(f"{device.device_id} - Brightness: {device.brightness}%")
                label = tk.Label(self.root, textvariable=label_text)
                self.labels.append({'id': device.device_id, 'label': label_text, 'device': device})
                tk.Button(self.root, text="Toggle ON/OFF", command=lambda d=device: self.toggle_helper(d)).pack()
                label.pack()
            elif isinstance(device, Thermostat):
                self.create_thermostat_controls(device)
                label_text = tk.StringVar()
                label_text.set(f"{device.device_id} - Temperature: {device.temperature}C")
                label = tk.Label(self.root, textvariable=label_text)
                self.labels.append({'id': device.device_id, 'label': label_text, 'device': device})
                tk.Button(self.root, text="Toggle ON/OFF", command=lambda d=device: self.toggle_helper(d)).pack()
                label.pack()
            elif isinstance(device, SecurityCamera):
                self.create_camera_controls(device)
                label_text = tk.StringVar()
                label_text.set(f"{device.device_id} - Motion: {'YES' if device.motion_detected else 'NO'}")
                label = tk.Label(self.root, textvariable=label_text)
                self.labels.append({'id': device.device_id, 'label': label_text, 'device': device})
                tk.Button(self.root, text="Toggle ON/OFF", command=lambda d=device: self.toggle_helper(d)).pack()
                label.pack()

    def toggle_helper(self, device):
        device.toggle_status()

    def update_values(self):
        for entry in self.labels:
            device = entry['device']
            if isinstance(device, SmartLight):
                entry['label'].set(f"{device.device_id} - Brightness: {device.brightness}%" if device.status else f"{device.device_id} - OFF")
            elif isinstance(device, Thermostat):
                entry['label'].set(f"{device.device_id} - Temperature: {device.temperature}C" if device.status else f"{device.device_id} - OFF")
            elif isinstance(device, SecurityCamera):
                entry['label'].set(f"{device.device_id} - Motion: {'YES' if device.motion_detected else 'NO'}" if device.status else f"{device.device_id} - OFF")

    def create_light_controls(self, light):
        tk.Label(self.root, text=f"{light.device_id} Brightness").pack()
        tk.Scale(self.root, from_=0, to=100, orient="horizontal", command=lambda v, l=light: self.set_brightness(l, v)).pack()

    def create_thermostat_controls(self, thermostat):
        tk.Label(self.root, text=f"{thermostat.device_id} Temperature").pack()
        tk.Scale(self.root, from_=10, to=30, orient="horizontal", command=lambda v, t=thermostat: self.set_temperature(t, v)).pack()

    def create_camera_controls(self, camera):
        tk.Label(self.root, text=f"{camera.device_id} Motion Detection").pack()
        tk.Button(self.root, text="Detect Motion", command=lambda c=camera: self.detect_motion(c)).pack()

    def create_rule_controls(self):
        tk.Label(self.root, text="Automation Rule: Turn on lights when motion is detected").pack()

    def update_device_list(self):
        self.device_listbox.delete(0, tk.END)
        for device in self.system.devices:
            self.device_listbox.insert(tk.END, f"{device.device_id}: {type(device).__name__} Status: {'On' if device.status else 'Off'}")

    def simulation_loop(self):
        while True:
            if self.automation_on:
                self.system.execute_rules()
                self.check_light_status()
                randomize_device_states(self.system.devices)
            self.update_values()
            self.update_device_list()
            time.sleep(2)

    def check_light_status(self):
        # Check if motion is detected and manage light status accordingly
        motion_detected = any(isinstance(device, SecurityCamera) and device.motion_detected for device in self.system.devices)
        
        if motion_detected:
            for device in self.system.devices:
                if isinstance(device, SmartLight):
                    device.status = True
                    self.light_status_label.config(text=f"{device.device_id} is ON (Motion Detected)")
            self.reset_motion_timer()
        else:
            if self.motion_timer is None:
                self.motion_timer = time.time()
            elif time.time() - self.motion_timer >= 5:  # 5 seconds without motion
                for device in self.system.devices:
                    if isinstance(device, SmartLight):
                        device.status = False
                        self.light_status_label.config(text=f"{device.device_id} is OFF (No Motion for 5 seconds)")
                self.motion_timer = None  # Reset the timer

    def reset_motion_timer(self):
        self.motion_timer = None  # Reset the motion timer if motion is detected

    def set_brightness(self, light, brightness):
        light.set_brightness(int(brightness))

    def set_temperature(self, thermostat, temperature):
        thermostat.set_temperature(int(temperature))

    def detect_motion(self, camera):
        camera.detect_motion()

# Randomization mechanism
def randomize_device_states(devices):
    for device in devices:
        if device.status:
            if isinstance(device, SmartLight):
                device.set_brightness(random.randint(0, 100))
            elif isinstance(device, Thermostat):
                device.set_temperature(random.randint(18, 25))
            elif isinstance(device, SecurityCamera):
                device.detect_motion()

# Main function to initialize and run the simulation
if __name__ == "__main__":
    light1 = SmartLight("Living Room Light")
    thermostat1 = Thermostat("Living Room Thermostat")
    camera1 = SecurityCamera("Front Door Camera")

    automation_system = AutomationSystem()
    automation_system.add_device(light1)
    automation_system.add_device(thermostat1)
    automation_system.add_device(camera1)

    # Create GUI Dashboard
    root = tk.Tk()
    dashboard = Dashboard(root, automation_system)
    root.mainloop()

