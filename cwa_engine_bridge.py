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

def compute_summary(payload: dict) -> dict:
    courses = payload.get("courses", [])

    # Credits logic
    completed = sum(
        c["credits"] for c in courses
        if c["credits"] > 0 and c["current"] > 0
    )

    remaining = sum(
        c["credits"] for c in courses
        if c["credits"] > 0 and c["allocated"] == 0
    )

    total_credits = completed + remaining

    # Current CWA (weighted)
    weighted_sum = sum(
        c["credits"] * c["current"]
        for c in courses
        if c["credits"] > 0
    )

    current_cwa = weighted_sum / total_credits if total_credits else 0.0
    target_cwa = float(payload.get("target_cwa", 72.5))

    # 🔥 CALL C DLL
    required_avg = calculate_cwa(
        name="Student",
        completed=completed,
        remaining=remaining,
        current=current_cwa,
        target=target_cwa
    )

    return {
        "current_cwa": current_cwa,
        "required_avg": required_avg,
        "total_credits": total_credits,
        "selected_credits": completed,
        "remaining_credits": remaining,
    }

