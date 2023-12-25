from bersta.extract_pfand import extract_pfand_from_bersta_rechnung_as_string

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_label.config(text=file_path)
        extract_button.config(state="normal")
        result_text.delete(1.0, tk.END)

def extract_pfand():
    file_path = file_path_label.cget("text")
    try:
        result = extract_pfand_from_bersta_rechnung_as_string(file_path)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, result)
    except Exception as e:
        import traceback
        traceback.print_tb(e)
        messagebox.showerror("Error", str(e))


# Set up the root GUI window
root = tk.Tk()
root.title("BerSta Pfand Extractor")

# Create a frame for the file path and browse button
file_frame = tk.Frame(root)
file_frame.pack(padx=10, pady=10)

file_path_label = tk.Label(file_frame, text="No file selected", anchor="w")
file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

browse_button = tk.Button(file_frame, text="Browse", command=browse_file)
browse_button.pack(side=tk.RIGHT)

# Create a frame for the Extract button
extract_button = tk.Button(root, text="Extract Pfand", state="disabled", command=extract_pfand)
extract_button.pack(pady=5)

# Create a text widget to display the result
result_text = tk.Text(root, height=30, width=40)
result_text.pack(padx=10, pady=10)


def run_ui():
    root.mainloop()