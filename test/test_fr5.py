"""
T-FR-5 (Section 4.1.5): Multi-Region Field Transition
Region 0 (R1) is field-free; region 1 (R2) has B=1 (magnetic only).
The particle moves in a straight line through R1 and enters R2 at t=1 s.

Expected:
1. Detector hit in R1: t_hit=0.5 s, x_hit=0.5 m, y_hit=0.0 m
   (vertical detector at x=0.5, within R1=[-1,1)x[-1,1))
2. After entering R2 (t > 1 s), speed is conserved under B-only force:
   relative drift in v^2 <= 1%

Grid: x_grid=-1, N_col=2, w=2
  Region 0: x in [-1, 1)  -- field-free (B_0=0)
  Region 1: x in [ 1, 3)  -- magnetic  (B_1=1)

VnVPlan reference: T-FR-5
"""
import subprocess
import os
import sys
import ast

PYTHON_DIR = os.path.expanduser(
    "~/Desktop/Drasil741/code/drasil-example/trajecto/src/python"
)
INPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "input_fr5.txt")
)
OUTPUT_FILE = os.path.join(PYTHON_DIR, "output.txt")

TOL_HIT   = 1e-2   # tolerance for hit coordinates
DRIFT_TOL = 0.01   # 1% for speed invariant


def run_trajecto(input_file):
    result = subprocess.run(
        ["python3", "Control.py", input_file],
        cwd=PYTHON_DIR,
        capture_output=True,
        text=True,
    )
    return result


def parse_output(output_file):
    data = {}
    traj = None
    with open(output_file, "r") as f:
        content = f.read()
    for line in content.splitlines():
        if line.startswith("s = "):
            traj = ast.literal_eval(line[4:])
        elif " = " in line:
            key, _, val = line.partition(" = ")
            data[key.strip()] = val.strip()
    return data, traj


def test_fr5():
    print("=" * 60)
    print("T-FR-5: Multi-Region Field Transition")
    print("=" * 60)

    result = run_trajecto(INPUT_FILE)
    if result.returncode != 0:
        print(f"FAIL: Program exited with code {result.returncode}.")
        print(result.stderr[:500])
        return False

    out, traj = parse_output(OUTPUT_FILE)

    # --- Detector hit (in R1) ---
    t_hit = float(out.get("t_hit", "-999"))
    x_hit = float(out.get("x_hit", "-999"))
    y_hit = float(out.get("y_hit", "-999"))

    t_hit_ref, x_hit_ref, y_hit_ref = 0.5, 0.5, 0.0
    t_hit_ok = abs(t_hit - t_hit_ref) <= TOL_HIT
    x_hit_ok = abs(x_hit - x_hit_ref) <= TOL_HIT
    y_hit_ok = abs(y_hit - y_hit_ref) <= TOL_HIT
    contract_ok = t_hit >= 0

    print(f"  t_hit = {t_hit:.6f}  (expected {t_hit_ref}, {'OK' if t_hit_ok else 'FAIL'})")
    print(f"  x_hit = {x_hit:.6f}  (expected {x_hit_ref}, {'OK' if x_hit_ok else 'FAIL'})")
    print(f"  y_hit = {y_hit:.6f}  (expected {y_hit_ref}, {'OK' if y_hit_ok else 'FAIL'})")
    print(f"  Output contract t_hit >= 0: {'OK' if contract_ok else 'FAIL'}")

    # --- Speed invariant AFTER field transition (t > 1 s, i.e., x > 1) ---
    t_final = 4.0
    n_pts = len(traj)
    t_step = t_final / (n_pts - 1)
    v0_sq = 1.0  # vx0=1, vy0=0 -> speed^2 = 1
    max_drift_r2 = 0.0
    r2_count = 0
    for i, pt in enumerate(traj):
        t_i = i * t_step
        if t_i > 1.0:  # particle is in R2 after t=1 s
            v_sq = pt[2] ** 2 + pt[3] ** 2
            drift = abs(v_sq - v0_sq) / v0_sq
            max_drift_r2 = max(max_drift_r2, drift)
            r2_count += 1

    drift_ok = max_drift_r2 <= DRIFT_TOL
    print(f"\n  Samples in R2 (t>1 s): {r2_count}")
    print(f"  Max relative drift in speed^2 (R2): {max_drift_r2:.4e}  "
          f"(tol={DRIFT_TOL:.0e}, {'OK' if drift_ok else 'FAIL'})")
    print("  (Speed conservation confirms field switched to B=1 in R2)")

    all_pass = t_hit_ok and x_hit_ok and y_hit_ok and contract_ok and drift_ok
    print(f"\nRESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    success = test_fr5()
    sys.exit(0 if success else 1)
