import ctypes
from pathlib import Path

# -------------------------------
# Load C library
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
C_LIB_PATH = BASE_DIR / "CWA-ENGINE" / "cwa_engine.dll"

if not C_LIB_PATH.exists():
    raise FileNotFoundError(f"C library not found at {C_LIB_PATH}")

c_lib = ctypes.CDLL(str(C_LIB_PATH))

# -------------------------------
# C function signatures
# -------------------------------
c_lib.init_student.argtypes = [
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_float,
    ctypes.c_float,
]
c_lib.init_student.restype = ctypes.c_void_p

c_lib.calculate_fair_distribution.argtypes = [ctypes.c_void_p]
c_lib.calculate_fair_distribution.restype = ctypes.c_float

c_lib.recalculate_fair_distribution.argtypes = [
    ctypes.c_void_p,
    ctypes.c_float,
    ctypes.c_int,
]
c_lib.recalculate_fair_distribution.restype = ctypes.c_float

c_lib.destroy_object.argtypes = [ctypes.c_void_p]
c_lib.destroy_object.restype = None


# -------------------------------
# Python-friendly wrappers
# -------------------------------
def calculate_fair_cwa(name, completed, remaining, current_cwa, target_cwa):
    # ---- SAFETY CHECKS (bridge-level) ----
    if completed <= 0 or remaining <= 0:
        raise ValueError("Credits must be positive")

    if not (0 < current_cwa <= 100) or not (0 < target_cwa <= 100):
        raise ValueError("CWA must be between 0 and 100")

    student = c_lib.init_student(
        name.encode("utf-8"),
        completed,
        remaining,
        current_cwa,
        target_cwa,
    )

    if not student:
        raise RuntimeError("Failed to initialize student")

    result = c_lib.calculate_fair_distribution(student)

    return student, result


def recalculate_with_priority(student, total_priority_wa, total_priority_credit):
    if total_priority_credit <= 0:
        raise ValueError("Priority credits must be positive")

    result = c_lib.recalculate_fair_distribution(
        student,
        total_priority_wa,
        total_priority_credit,
    )

    return result


def destroy_student(student):
    if student:
        c_lib.destroy_object(student)
