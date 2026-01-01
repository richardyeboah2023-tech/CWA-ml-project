import tkinter as tk
from tkinter import messagebox
from cwa_engine_bridge import compute_required_average


def predict():
    try:
        name = name_entry.get().strip()
        completed = int(completed_entry.get())
        remaining = int(remaining_entry.get())
        current_cwa = float(current_cwa_entry.get())
        target_cwa = float(target_cwa_entry.get())

        # -------- VALIDATION --------
        if not name:
            raise ValueError("Name cannot be empty")

        if completed < 0 or remaining < 0:
            raise ValueError("Credits cannot be negative")

        if current_cwa < 0 or target_cwa < 0:
            raise ValueError("CWA cannot be negative")

        if remaining == 0:
            raise ValueError("Remaining credits cannot be zero")

        if current_cwa > 100 or target_cwa > 100:
            raise ValueError("CWA cannot exceed 100")

        # -------- CALL ENGINE --------
        result = compute_required_average(
            name,
            completed,
            remaining,
            current_cwa,
            target_cwa
        )

        result_label.config(text=result)

    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))

    except Exception as e:
        messagebox.showerror("System Error", str(e))


# -------- GUI --------
root = tk.Tk()
root.title("CWA Predictor")
root.geometry("420x360")

tk.Label(root, text="Student Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Completed Credits").pack()
completed_entry = tk.Entry(root)
completed_entry.pack()

tk.Label(root, text="Remaining Credits").pack()
remaining_entry = tk.Entry(root)
remaining_entry.pack()

tk.Label(root, text="Current CWA").pack()
current_cwa_entry = tk.Entry(root)
current_cwa_entry.pack()

tk.Label(root, text="Target CWA").pack()
target_cwa_entry = tk.Entry(root)
target_cwa_entry.pack()

tk.Button(root, text="Calculate", command=predict).pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 11, "bold"))
result_label.pack()

root.mainloop()
