import tkinter as tk
from tkinter import messagebox
from cwa_engine_bridge import calculate_cwa

def send_to_c():
    try:
        # Read and convert inputs
        name = name_entry.get()
        current_cwa = float(current_cwa_entry.get())
        completed_credits = int(completed_credits_entry.get())
        remaining_credits = int(remaining_credits_entry.get())
        target_cwa = float(target_cwa_entry.get())

        # Validate inputs
        if current_cwa < 0 or target_cwa < 0 or completed_credits < 0 or remaining_credits < 0:
            messagebox.showerror("Input Error", "Values cannot be negative")
            return

        # Call C function via bridge
        fair_dist = calculate_cwa(name, completed_credits, remaining_credits, current_cwa, target_cwa)

        # Display results or handle C error codes
        if fair_dist == -1:
            result_label.config(text="Impossible: required score > 100")
        elif fair_dist == -2:
            result_label.config(text="Impossible: required score < 0")
        else:
            result_label.config(text=f"Predicted fair distribution: {fair_dist:.2f}")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers")

def reset_fields():
    name_entry.delete(0, tk.END)
    current_cwa_entry.delete(0, tk.END)
    completed_credits_entry.delete(0, tk.END)
    remaining_credits_entry.delete(0, tk.END)
    target_cwa_entry.delete(0, tk.END)
    result_label.config(text="")

# Setup main window
root = tk.Tk()
root.title("CWA Predictor")
root.geometry("500x400")   # Bigger window for recording

# Zoomable window
root.option_add("*Font", "Arial 12")

# Labels and entries
tk.Label(root, text="Student Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()
name_entry.insert(0, "Enter full name")  # Placeholder

tk.Label(root, text="Current CWA").pack()
current_cwa_entry = tk.Entry(root)
current_cwa_entry.pack()
current_cwa_entry.insert(0, "e.g., 60.0")  # Placeholder

tk.Label(root, text="Completed Credits").pack()
completed_credits_entry = tk.Entry(root)
completed_credits_entry.pack()
completed_credits_entry.insert(0, "e.g., 30")  # Placeholder

tk.Label(root, text="Remaining Credits").pack()
remaining_credits_entry = tk.Entry(root)
remaining_credits_entry.pack()
remaining_credits_entry.insert(0, "e.g., 30")  # Placeholder

tk.Label(root, text="Target CWA").pack()
target_cwa_entry = tk.Entry(root)
target_cwa_entry.pack()
target_cwa_entry.insert(0, "e.g., 75.0")  # Placeholder

# Buttons
tk.Button(root, text="Predict", command=send_to_c).pack(pady=10)
tk.Button(root, text="Reset", command=reset_fields).pack(pady=5)

# Result label
result_label = tk.Label(root, text="", fg="blue")
result_label.pack(pady=10)

root.mainloop()
