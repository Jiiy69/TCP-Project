import socket
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

HOST = '127.0.0.1'  # change for LAN
PORT = 5001
BUFFER_SIZE = 1024

file_path = ""

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

def choose_file():
    global file_path
    file_path = filedialog.askopenfilename()
    file_label.config(text=file_path)

def send_file():
    if not file_path:
        status_label.config(text="No file selected!")
        return

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Send metadata as ONE message
        metadata = f"{file_name}|{file_size}\n"
        client.sendall(metadata.encode())

        log(f"Sending: {file_name} ({file_size} bytes)")

        progress_bar["maximum"] = file_size
        sent = 0

        with open(file_path, "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                client.sendall(data)
                sent += len(data)

                progress_bar["value"] = sent
                percent = (sent / file_size) * 100
                status_label.config(text=f"Sending: {percent:.2f}%")
                window.update_idletasks()

        log("File sent successfully!")
        status_label.config(text="Done")

        client.close()

    except Exception as e:
        log(f"Error: {e}")

# GUI
window = tk.Tk()
window.title("File Sender (Client)")
window.geometry("500x450")

tk.Label(window, text="TCP File Sender", font=("Arial", 14)).pack(pady=10)

tk.Button(window, text="Choose File", command=choose_file).pack(pady=5)

file_label = tk.Label(window, text="No file selected")
file_label.pack()

tk.Button(window, text="Send File", command=send_file).pack(pady=10)

status_label = tk.Label(window, text="Idle")
status_label.pack()

progress_bar = ttk.Progressbar(window, length=400)
progress_bar.pack(pady=10)

log_box = tk.Text(window, height=10)
log_box.pack(padx=10, pady=10, fill="both", expand=True)

window.mainloop()