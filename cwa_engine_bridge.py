import ctypes
from pathlib import Path

# Absolute path to DLL
C_LIB_PATH = Path(__file__).parent / "CWA-ENGINE" / "cwa_engine.dll"

# Load DLL
c_lib = ctypes.CDLL(str(C_LIB_PATH))

# C function signatures (MATCH THE C HEADER ORDER)
c_lib.init_student.argtypes = [
    ctypes.c_char_p,   # name
    ctypes.c_double,   # current_cwa
    ctypes.c_int,      # completed_credits
    ctypes.c_int,      # remaining_credits
    ctypes.c_double    # target_cwa
]
c_lib.init_student.restype = ctypes.c_void_p

c_lib.calculate_fair_distribution.argtypes = [ctypes.c_void_p]
c_lib.calculate_fair_distribution.restype = ctypes.c_double

c_lib.destroy_object.argtypes = [ctypes.c_void_p]
c_lib.destroy_object.restype = None


def calculate_cwa(name, current_cwa, completed_credits, remaining_credits, target_cwa):
    student = c_lib.init_student(
        name.encode("utf-8"),
        current_cwa,
        completed_credits,
        remaining_credits,
        target_cwa
    )

    result = c_lib.calculate_fair_distribution(student)
    c_lib.destroy_object(student)

    return result
