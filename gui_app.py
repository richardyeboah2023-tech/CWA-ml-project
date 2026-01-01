import tkinter as tk
from tkinter import messagebox
from cwa_engine_bridge import compute_cwa

def send_to_ml():
    try:
        name = name_entry.get()
        completed_credits = int(completed_credits_entry.get())
        remaining_credits = int(remaining_credits_entry.get())
        current_cwa = float(current_cwa_entry.get())
        target_cwa = float(target_cwa_entry.get())

        result = compute_cwa(name, completed_credits, remaining_credits, current_cwa, target_cwa)

        result_label.config(text=f"Predicted CWA: {result}")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter numeric values for credits and CWA")

def reset_fields():
    name_entry.delete(0, tk.END)
    completed_credits_entry.delete(0, tk.END)
    remaining_credits_entry.delete(0, tk.END)
    current_cwa_entry.delete(0, tk.END)
    target_cwa_entry.delete(0, tk.END)
    result_label.config(text="")

root = tk.Tk()
root.title("CWA Predictor")
root.geometry("500x400")
root.resizable(True, True)  # Allows zooming

# Labels and entry fields with placeholder hints
tk.Label(root, text="Student Name").pack()
name_entry = tk.Entry(root)
name_entry.insert(0, "e.g., John Doe")
name_entry.pack()

tk.Label(root, text="Completed Credits").pack()
completed_credits_entry = tk.Entry(root)
completed_credits_entry.insert(0, "e.g., 30")
completed_credits_entry.pack()

tk.Label(root, text="Remaining Credits").pack()
remaining_credits_entry = tk.Entry(root)
remaining_credits_entry.insert(0, "e.g., 60")
remaining_credits_entry.pack()

tk.Label(root, text="Current CWA").pack()
current_cwa_entry = tk.Entry(root)
current_cwa_entry.insert(0, "e.g., 70.5")
current_cwa_entry.pack()

tk.Label(root, text="Target CWA").pack()
target_cwa_entry = tk.Entry(root)
target_cwa_entry.insert(0, "e.g., 75.0")
target_cwa_entry.pack()

# Buttons
tk.Button(root, text="Predict", command=send_to_ml).pack(pady=10)
tk.Button(root, text="Reset", command=reset_fields).pack(pady=5)

# Result display
result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.pack(pady=20)

root.mainloop()
