import tkinter as tk
import ctypes
import os
from pathlib import Path

# ===============================
# LOCATE DLL
# ===============================

BASE_DIR = Path(__file__).resolve().parent
C_LIB_DIR = BASE_DIR / "CWA-ENGINE"
C_LIB_PATH = C_LIB_DIR / "cwa_engine.dll"

# Tell Windows where to find DLL dependencies
os.add_dll_directory(str(C_LIB_DIR))

# Load C library
c_lib = ctypes.WinDLL(str(C_LIB_PATH))

# ===============================
# DEFINE C TYPES
# ===============================

Student = ctypes.c_void_p

c_lib.init_student.argtypes = [
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_float,
    ctypes.c_float
]
c_lib.init_student.restype = Student

c_lib.calculate_fair_distribution.argtypes = [Student]
c_lib.calculate_fair_distribution.restype = ctypes.c_float

c_lib.destroy_object.argtypes = [Student]
c_lib.destroy_object.restype = None

# ===============================
# PYTHON → C ENGINE BRIDGE
# ===============================

def compute_required_average(
    completed_credits,
    remaining_credits,
    current_cwa,
    target_cwa
):
    student = c_lib.init_student(
        b"PythonUser",
        completed_credits,
        remaining_credits,
        current_cwa,
        target_cwa
    )

    if not student:
        return None

    result = c_lib.calculate_fair_distribution(student)
    c_lib.destroy_object(student)

    return result

# ===============================
# GUI CALLBACK
# ===============================

def send_to_engine():
    try:
        completed = int(completed_entry.get())
        remaining = int(remaining_entry.get())
        current = float(current_cwa_entry.get())
        target = float(target_cwa_entry.get())
    except ValueError:
        result_label.config(text="❌ Invalid input")
        return

    result = compute_required_average(
        completed, remaining, current, target
    )

    if result is None:
        result_label.config(text="❌ Engine error")
    elif result == 0:
        result_label.config(text="⚠ Target impossible (>100 needed)")
    elif result == -1:
        result_label.config(text="⚠ Target impossible (<0)")
    else:
        result_label.config(
            text=f"✅ Required Avg per Course: {result:.2f}"
        )

# ===============================
# GUI LAYOUT
# ===============================

root = tk.Tk()
root.title("CWA Predictor (Python + C Engine)")
root.geometry("420x350")

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

tk.Button(
    root,
    text="Compute Required Average",
    command=send_to_engine
).pack(pady=15)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack()

root.mainloop()
