import ctypes
from pathlib import Path

# Path to C DLL
C_LIB_PATH = Path(__file__).parent / "CWA-ENGINE" / "cwa_engine.dll"

# Load C library
c_lib = ctypes.CDLL(str(C_LIB_PATH))

# Define argument & return types
c_lib.init_student.argtypes = [
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_float,
    ctypes.c_float
]
c_lib.init_student.restype = ctypes.c_void_p

c_lib.calculate_fair_distribution.argtypes = [ctypes.c_void_p]
c_lib.calculate_fair_distribution.restype = ctypes.c_float

c_lib.destroy_object.argtypes = [ctypes.c_void_p]
c_lib.destroy_object.restype = None


def compute_required_average(name, completed, remaining, current_cwa, target_cwa):
    student = c_lib.init_student(
        name.encode("utf-8"),
        completed,
        remaining,
        current_cwa,
        target_cwa
    )

    if not student:
        raise RuntimeError("Failed to initialize student object")

    result = c_lib.calculate_fair_distribution(student)
    c_lib.destroy_object(student)

    if result == -1:
        return "Target CWA is too high (not realistic)"
    elif result == -2:
        return "Target CWA is too low (invalid)"
    else:
        return f"Required average for remaining courses: {result:.2f}"
