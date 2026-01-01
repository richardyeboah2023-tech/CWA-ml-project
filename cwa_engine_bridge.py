import ctypes
from pathlib import Path

# Load DLL
C_LIB_PATH = Path("CWA-ENGINE/cwa_engine.dll").resolve()
c_lib = ctypes.CDLL(str(C_LIB_PATH))

# ---- CORRECT TYPES (float ≠ double) ----
c_lib.init_student.argtypes = [
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_float,   # current_cwa
    ctypes.c_float    # target_cwa
]
c_lib.init_student.restype = ctypes.c_void_p

c_lib.calculate_fair_distribution.argtypes = [ctypes.c_void_p]
c_lib.calculate_fair_distribution.restype = ctypes.c_float

c_lib.destroy_object.argtypes = [ctypes.c_void_p]
c_lib.destroy_object.restype = None


def calculate_cwa(name, completed, remaining, current, target):
    student = c_lib.init_student(
        name.encode("utf-8"),
        completed,
        remaining,
        ctypes.c_float(current),
        ctypes.c_float(target)
    )

    result = c_lib.calculate_fair_distribution(student)
    c_lib.destroy_object(student)
    return result
