import ctypes
from pathlib import Path
from typing import Any, Dict, List


# -----------------------------------
# DLL LOADING
# -----------------------------------

C_LIB_PATH = Path("CWA-ENGINE/cwa_engine.dll").resolve()
c_lib = ctypes.CDLL(str(C_LIB_PATH))

# ---- Signatures from cwa_estimater.h ----
# Student init_student(int credits_com,int credits_remain);
c_lib.init_student.argtypes = [
    ctypes.c_int,  # credits_com
    ctypes.c_int,  # credits_remain
]
c_lib.init_student.restype = ctypes.c_void_p  # Student*

# float calculate_dist_CWA(const Student student,float target_cwa,float current_cwa);
c_lib.calculate_dist_CWA.argtypes = [
    ctypes.c_void_p,  # Student
    ctypes.c_float,   # target_cwa
    ctypes.c_float,   # current_cwa
]
c_lib.calculate_dist_CWA.restype = ctypes.c_float

# float recalculate_dist_CWA(const Student student,float total_achievable_WA,int total_achievable_Credits);
c_lib.recalculate_dist_CWA.argtypes = [
    ctypes.c_void_p,  # Student
    ctypes.c_float,   # total_achievable_WA
    ctypes.c_int,     # total_achievable_Credits
]
c_lib.recalculate_dist_CWA.restype = ctypes.c_float

# void destroy_object(const Student student);
c_lib.destroy_object.argtypes = [ctypes.c_void_p]
c_lib.destroy_object.restype = None


# -----------------------------------
# LOW-LEVEL STUDENT WRAPPER
# -----------------------------------

class _StudentHandle:
    """
    RAII wrapper around the C engine student object.

    - Calls init_student on creation
    - Guarantees destroy_object is called exactly once
    """

    def __init__(self, credits_completed: int, credits_remaining: int) -> None:
        ptr = c_lib.init_student(int(credits_completed), int(credits_remaining))
        if not ptr:
            raise RuntimeError("init_student returned NULL pointer")
        self._ptr = ptr

    def calculate_dist_cwa(self, target_cwa: float, current_cwa: float) -> float:
        return float(
            c_lib.calculate_dist_CWA(
                self._ptr,
                ctypes.c_float(float(target_cwa)),
                ctypes.c_float(float(current_cwa)),
            )
        )

    def recalculate_dist_cwa(self, total_achievable_wa: float, total_achievable_credits: int) -> float:
        return float(
            c_lib.recalculate_dist_CWA(
                self._ptr,
                ctypes.c_float(float(total_achievable_wa)),
                int(total_achievable_credits),
            )
        )

    def close(self) -> None:
        if getattr(self, "_ptr", None):
            c_lib.destroy_object(self._ptr)
            self._ptr = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


# -----------------------------------
# PUBLIC ENGINE FUNCTION (simple wrapper)
# -----------------------------------

def calculate_cwa(name, completed, remaining, current, target):
    """
    Backwards-compatible wrapper for your earlier usage.

    Now implemented using:
        init_student
        calculate_dist_CWA
        destroy_object
    but keeps the same signature.
    """
    student = _StudentHandle(int(completed), int(remaining))
    try:
        required = student.calculate_dist_cwa(float(target), float(current))
    finally:
        student.close()
    return required


# -----------------------------------
# HIGH-LEVEL SUMMARY FOR GUI
# -----------------------------------

def _safe_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


def _safe_int(x: Any) -> int:
    try:
        return int(float(x))
    except Exception:
        return 0


def compute_summary(payload: dict) -> dict:
    """
    High-level helper called by the PySide6 GUI.

    Expected payload (built in cwa_pyside6_app.py):

        {
          "courses": [
             {"course": str, "credits": int, "current": float, "allocated": float},
             ...
          ],
          "target_cwa": float,          # from Target CWA input
        }

    Semantics (aligned with your documentation):

      1. Compute:
         - completed_credits: we still approximate from 'current' values
         - remaining_credits: credits that have no 'current' yet (future/remaining)
         - current_cwa: weighted average of 'current' over all credits > 0

      2. Call calculate_dist_CWA to get the base required average
         for all remaining credits.

      3. Identify LOCKED courses among remaining:
         - credits > 0
         - allocated > 0
         - current >= allocated
         This matches the Target tick rule in your PySide6 GUI.

         For these locked courses we compute:
           total_achievable_WA = sum(allocated * credits)
           total_achievable_Credits = sum(credits)

      4. If we have any locked courses, call recalculate_dist_CWA
         to get the redistributed required average on the *unlocked*
         portion of the remaining credits.

      5. Return a summary dict that the GUI uses to update:
         - current_cwa
         - required_avg
         - total_credits
         - selected_credits   (here we treat as sum of LOCKED credits)
         - remaining_credits  (remaining_credits_total - locked_credits)
    """
    courses: List[Dict[str, Any]] = payload.get("courses", []) or []

    # --- credits + current weighted sum ---
    completed_credits = 0
    remaining_credits_total = 0
    weighted_sum = 0.0

    for c in courses:
        cr = _safe_int(c.get("credits", 0))
        if cr <= 0:
            continue

        cur = _safe_float(c.get("current", 0.0))

        if cur > 0.0:
            completed_credits += cr
        else:
            remaining_credits_total += cr

        weighted_sum += cr * cur

    total_credits = completed_credits + remaining_credits_total

    # Current CWA (approximate, as before)
    current_cwa = (weighted_sum / total_credits) if total_credits > 0 else 0.0

    if "target_cwa" not in payload:
        raise ValueError("target_cwa is required in payload for compute_summary()")

    target_cwa = _safe_float(payload.get("target_cwa"))

    # No remaining credits => nothing to compute
    if remaining_credits_total <= 0 or total_credits <= 0:
        return {
            "current_cwa": current_cwa,
            "required_avg": 0.0,
            "total_credits": total_credits,
            "selected_credits": 0,
            "remaining_credits": 0,
        }

    # ---- 1) Base distribution for all remaining credits ----
    student = _StudentHandle(completed_credits, remaining_credits_total)
    try:
        base_required = student.calculate_dist_cwa(target_cwa, current_cwa)

        # ---- 2) Locked courses among remaining (for recalc) ----
        locked_wa = 0.0
        locked_cr = 0

        for c in courses:
            cr = _safe_int(c.get("credits", 0))
            if cr <= 0:
                continue

            cur = _safe_float(c.get("current", 0.0))
            alloc = _safe_float(c.get("allocated", 0.0))

            # A course is "locked" if:
            # - it is part of the remaining group (no current yet)
            # - user has set an allocated score
            # - AND current >= allocated (same as Target tick rule)
            if cur <= 0.0 and alloc > 0.0 and cur >= alloc:
                locked_wa += alloc * cr
                locked_cr += cr

        required_avg = base_required

        # Only recalc if there are truly locked courses
        if locked_cr > 0 and locked_wa > 0.0 and locked_cr < remaining_credits_total:
            new_required = student.recalculate_dist_cwa(locked_wa, locked_cr)
            # If recalc returns an error code (<0), keep base_required
            if new_required > 0:
                required_avg = new_required

    finally:
        student.close()

    # For the GUI summary:
    # - total_credits    -> total_credits from courses
    # - selected_credits -> locked credits
    # - remaining_credits-> remaining_credits_total - locked_cr
    return {
        "current_cwa": current_cwa,
        "required_avg": required_avg,
        "total_credits": total_credits,
        "selected_credits": locked_cr,
        "remaining_credits": max(0, remaining_credits_total - locked_cr),
    }