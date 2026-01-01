import tkinter as tk
from tkinter import messagebox
from cwa_engine_bridge import (
    calculate_fair_cwa,
    recalculate_with_priority,
    destroy_student,
)

student_ptr = None


def calculate():
    global student_ptr

    try:
        name = name_entry.get().strip()
        completed = int(completed_entry.get())
        remaining = int(remaining_entry.get())
        current_cwa = float(current_cwa_entry.get())
        target_cwa = float(target_cwa_entry.get())

        # ---- GUI VALIDATION ----
        if not name:
            raise ValueError("Name cannot be empty")

        if completed <= 0 or remaining <= 0:
            raise ValueError("Credits must be positive numbers")

        if not (0 < current_cwa <= 100):
            raise ValueError("Current CWA must be between 0 and 100")

        if not (0 < target_cwa <= 100):
            raise ValueError("Target CWA must be between 0 and 100")

        student_ptr, result = calculate_fair_cwa(
            name,
            completed,
            remaining,
            current_cwa,
            target_cwa,
        )

        if result < 0:
            messagebox.showerror(
                "Impossible",
                "Target CWA is not achievable with remaining credits",
            )
        else:
            result_label.config(
                text=f"Required average score: {result:.2f}"
            )

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as e:
        messagebox.showerror("System Error", str(e))


def recalculate():
    global student_ptr

    try:
        if not student_ptr:
            raise ValueError("Calculate fair distribution first")

        priority_score = float(priority_score_entry.get())
        priority_credit = int(priority_credit_entry.get())

        if priority_credit <= 0:
            raise ValueError("Priority credits must be positive")

        if not (0 < priority_score <= 100):
            raise ValueError("Priority score must be between 0 and 100")

        total_priority_wa = priority_score * priority_credit

        result = recalculate_with_priority(
            student_ptr,
            total_priority_wa,
            priority_credit,
        )

        if result < 0:
            messagebox.showerror(
                "Impossible",
                "Recalculated distribution is not realistic",
            )
        else:
            result_label.config(
                text=f"New required average: {result:.2f}"
            )

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as e:
        messagebox.showerror("System Error", str(e))


# -------------------------------
# GUI Layout
# -------------------------------
root = tk.Tk()
root.title("CWA Estimator")

tk.Label(root, text="Name").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Completed Credits").grid(row=1, column=0)
completed_entry = tk.Entry(root)
completed_entry.grid(row=1, column=1)

tk.Label(root, text="Remaining Credits").grid(row=2, column=0)
remaining_entry = tk.Entry(root)
remaining_entry.grid(row=2, column=1)

tk.Label(root, text="Current CWA").grid(row=3, column=0)
current_cwa_entry = tk.Entry(root)
current_cwa_entry.grid(row=3, column=1)

tk.Label(root, text="Target CWA").grid(row=4, column=0)
target_cwa_entry = tk.Entry(root)
target_cwa_entry.grid(row=4, column=1)

tk.Button(root, text="Calculate", command=calculate).grid(
    row=5, column=0, columnspan=2
)

tk.Label(root, text="Priority Score").grid(row=6, column=0)
priority_score_entry = tk.Entry(root)
priority_score_entry.grid(row=6, column=1)

tk.Label(root, text="Priority Credit").grid(row=7, column=0)
priority_credit_entry = tk.Entry(root)
priority_credit_entry.grid(row=7, column=1)

tk.Button(root, text="Recalculate", command=recalculate).grid(
    row=8, column=0, columnspan=2
)

result_label = tk.Label(root, text="")
result_label.grid(row=9, column=0, columnspan=2)

root.mainloop()

if student_ptr:
    destroy_student(student_ptr)
