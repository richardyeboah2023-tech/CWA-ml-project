import ctypes
import os

# Full path to your compiled C library
C_LIB_PATH = os.path.join(os.getcwd(), "CWA-ENGINE", "cwa_engine.dll")
c_lib = ctypes.CDLL(C_LIB_PATH)

# Expose functions from the DLL
c_lib.init_student.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double]
c_lib.init_student.restype = ctypes.c_void_p

c_lib.calculate_fair_distribution.argtypes = [ctypes.c_void_p]
c_lib.calculate_fair_distribution.restype = ctypes.c_double

c_lib.recalculate_fair_distribution.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_int]
c_lib.recalculate_fair_distribution.restype = ctypes.c_double

c_lib.destroy_object.argtypes = [ctypes.c_void_p]
c_lib.destroy_object.restype = None

# Python wrapper
def compute_cwa(name, completed_credits, remaining_credits, current_cwa, target_cwa):
    if completed_credits < 0 or remaining_credits < 0 or current_cwa < 0 or target_cwa < 0:
        return "Error: Negative values are not allowed"
    
    student = c_lib.init_student(name.encode('utf-8'), completed_credits, remaining_credits, current_cwa, target_cwa)
    
    result = c_lib.calculate_fair_distribution(student)
    if result < 0:
        c_lib.destroy_object(student)
        return "Error: Impossible target or invalid calculation"
    
    c_lib.destroy_object(student)
    return result
