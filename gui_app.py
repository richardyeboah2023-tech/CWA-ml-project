import tkinter as tk
from tkinter import messagebox
from cwa_engine_bridge import calculate_cwa


def send_to_c():
    try:
        name = name_entry.get().strip()

        current_cwa = float(current_cwa_entry.get())
        completed_credits = int(completed_credits_entry.get())
        remaining_credits = int(remaining_credits_entry.get())
        target_cwa = float(target_cwa_entry.get())

        # Validation
        if not name:
            messagebox.showerror("Input Error", "Name is required")
            return

        if current_cwa < 0 or target_cwa < 0:
            messagebox.showerror("Input Error", "CWA cannot be negative")
            return

        if completed_credits <= 0 or remaining_credits <= 0:
            messagebox.showerror("Input Error", "Credits must be greater than zero")
            return

        fair_dist = calculate_cwa(
            name,
            current_cwa,
            completed_credits,
            remaining_credits,
            target_cwa
        )

        if fair_dist < 0 or fair_dist > 100:
            result_label.config(
                text="❌ Impossible target (required score out of range)",
                fg="red"
            )
        else:
            result_label.config(
                text=f"✅ Required average for remaining courses: {fair_dist:.2f}",
                fg="green"
            )

    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numeric values")


def reset_fields():
    name_entry.delete(0, tk.END)
    current_cwa_entry.delete(0, tk.END)
    completed_credits_entry.delete(0, tk.END)
    remaining_credits_entry.delete(0, tk.END)
    target_cwa_entry.delete(0, tk.END)
    result_label.config(text="")


# GUI setup
root = tk.Tk()
root.title("CWA Predictor")
root.geometry("520x420")
root.option_add("*Font", "Arial 12")

tk.Label(root, text="Student Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Current CWA").pack()
current_cwa_entry = tk.Entry(root)
current_cwa_entry.pack()

tk.Label(root, text="Completed Credits").pack()
completed_credits_entry = tk.Entry(root)
completed_credits_entry.pack()

tk.Label(root, text="Remaining Credits").pack()
remaining_credits_entry = tk.Entry(root)
remaining_credits_entry.pack()

tk.Label(root, text="Target CWA").pack()
target_cwa_entry = tk.Entry(root)
target_cwa_entry.pack()

tk.Button(root, text="Predict", command=send_to_c).pack(pady=10)
tk.Button(root, text="Reset", command=reset_fields).pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 13, "bold"))
result_label.pack(pady=15)

root.mainloop()
