import ctypes
from pathlib import Path

# Path to your compiled DLL
C_LIB_PATH = Path("CWA-ENGINE/cwa_engine.dll").resolve()

# Load the C library
c_lib = ctypes.CDLL(str(C_LIB_PATH))

# Define argument and return types
c_lib.init_student.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double]
c_lib.init_student.restype = ctypes.c_void_p

c_lib.calculate_fair_distribution.argtypes = [ctypes.c_void_p]
c_lib.calculate_fair_distribution.restype = ctypes.c_double

c_lib.recalculate_fair_distribution.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_int]
c_lib.recalculate_fair_distribution.restype = ctypes.c_double

c_lib.destroy_object.argtypes = [ctypes.c_void_p]
c_lib.destroy_object.restype = None

def calculate_cwa(name, completed_credits, remaining_credits, current_cwa, target_cwa):
    student = c_lib.init_student(
        name.encode('utf-8'), completed_credits, remaining_credits, current_cwa, target_cwa
    )
    fair_dist = c_lib.calculate_fair_distribution(student)
    c_lib.destroy_object(student)
    return fair_dist
