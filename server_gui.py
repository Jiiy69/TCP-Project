import socket
import threading
import tkinter as tk
from tkinter import ttk

HOST = '0.0.0.0'
PORT = 5001
BUFFER_SIZE = 1024

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    log("Server started. Waiting for connection...")

    conn, addr = server.accept()
    log(f"Connected to {addr}")

    try:
        # Receive metadata (combined)
        metadata = b""
        while b"\n" not in metadata:
            metadata += conn.recv(1)

        metadata = metadata.decode().strip()
        file_name, file_size = metadata.split("|")
        file_size = int(file_size)

        log(f"Receiving file: {file_name} ({file_size} bytes)")

        save_path = "received_" + file_name

        progress_bar["maximum"] = file_size
        received = 0

        with open(save_path, "wb") as f:
            while received < file_size:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
                received += len(data)

                progress_bar["value"] = received
                percent = (received / file_size) * 100
                status_label.config(text=f"Receiving: {percent:.2f}%")
                window.update_idletasks()

        log("File received successfully!")
        status_label.config(text="Done")

    except Exception as e:
        log(f"Error: {e}")

    conn.close()
    server.close()

def start_thread():
    threading.Thread(target=start_server, daemon=True).start()

# GUI
window = tk.Tk()
window.title("File Receiver (Server)")
window.geometry("500x400")

tk.Label(window, text="TCP File Receiver", font=("Arial", 14)).pack(pady=10)

tk.Button(window, text="Start Server", command=start_thread).pack(pady=5)

status_label = tk.Label(window, text="Idle")
status_label.pack()

progress_bar = ttk.Progressbar(window, length=400)
progress_bar.pack(pady=10)

log_box = tk.Text(window, height=10)
log_box.pack(padx=10, pady=10, fill="both", expand=True)

window.mainloop()