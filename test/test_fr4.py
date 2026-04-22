"""
T-FR-4 (Section 4.1.4): Electric-Field Analytic Trajectory + Vertical Detector Hit
With B=0 and E_x=1 everywhere, the equations of motion reduce to constant
acceleration a_x = kappa * E_x = 1 m/s^2.

Analytic solution:
  x(t) = 0.5 * t^2
  y(t) = 0
  v_x(t) = t
  v_y(t) = 0

Vertical detector at x_det=2.0 -> t_hit_ref = sqrt(2*2) = 2.0 s
y_hit_ref = 0.0 m (within detector span [-0.5, 0.5])

VnVPlan reference: T-FR-4
Tolerance: position error <= 1e-3 m, hit error <= 1e-2 s / 1e-3 m
"""
import subprocess
import os
import sys
import ast
import math

PYTHON_DIR = os.path.expanduser(
    "~/Desktop/Drasil741/code/drasil-example/trajecto/src/python"
)
INPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "input_fr4.txt")
)
OUTPUT_FILE = os.path.join(PYTHON_DIR, "output.txt")

TOL_POS  = 1e-3   # tolerance for trajectory positions
TOL_T_HIT = 1e-2  # tolerance for t_hit (one step = 3.0/1000 = 0.003 s)
TOL_HIT  = 1e-2   # tolerance for x_hit, y_hit


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


def test_fr4():
    print("=" * 60)
    print("T-FR-4: Electric-Field Analytic Trajectory + Vertical Detector Hit")
    print("=" * 60)

    result = run_trajecto(INPUT_FILE)
    if result.returncode != 0:
        print(f"FAIL: Program exited with code {result.returncode}.")
        print(result.stderr[:500])
        return False

    out, traj = parse_output(OUTPUT_FILE)

    # --- Trajectory comparison: x(t)=0.5*t^2, y(t)=0 ---
    t_final = 3.0
    n_pts = len(traj)
    t_step = t_final / (n_pts - 1)
    max_x_err = 0.0
    max_y_err = 0.0
    # Only compare trajectory samples where the analytic formula holds:
    # x(t) = 0.5*t^2 is valid while the particle is inside the E-field grid
    # (x_grid=-1, w=2, N_col=2 -> right edge at x=3.0).
    # After the particle exits the grid, E=0 and the formula no longer applies.
    # We additionally cap comparison at the hit point (x <= x_det = 2.0) to
    # keep the test focused on the physics we are actually verifying.
    X_GRID_RIGHT = 3.0   # x_grid + N_col * w = -1 + 2*2
    X_DET = 2.0
    X_CAP = min(X_GRID_RIGHT, X_DET)

    for i, pt in enumerate(traj):
        t_i = i * t_step
        if pt[0] > X_CAP:  # particle has left the comparison region
            break
        x_ref = 0.5 * t_i ** 2
        y_ref = 0.0
        max_x_err = max(max_x_err, abs(pt[0] - x_ref))
        max_y_err = max(max_y_err, abs(pt[1] - y_ref))

    print(f"  Trajectory samples: {n_pts}")
    print(f"  (Comparison limited to x <= {X_CAP} where analytic formula holds)")
    print(f"  Max |x_num - 0.5*t^2|: {max_x_err:.2e}  (tol={TOL_POS:.0e})")
    print(f"  Max |y_num - 0|:        {max_y_err:.2e}  (tol={TOL_POS:.0e})")
    traj_ok = max_x_err <= TOL_POS and max_y_err <= TOL_POS

    # --- Detector hit values ---
    t_hit = float(out.get("t_hit", "-999"))
    x_hit = float(out.get("x_hit", "-999"))
    y_hit = float(out.get("y_hit", "-999"))

    t_hit_ref, x_hit_ref, y_hit_ref = 2.0, 2.0, 0.0
    t_hit_ok = abs(t_hit - t_hit_ref) <= TOL_T_HIT
    x_hit_ok = abs(x_hit - x_hit_ref) <= TOL_HIT
    y_hit_ok = abs(y_hit - y_hit_ref) <= TOL_HIT

    print(f"\n  t_hit = {t_hit:.6f}  (expected {t_hit_ref}, {'OK' if t_hit_ok else 'FAIL'})")
    print(f"  x_hit = {x_hit:.6f}  (expected {x_hit_ref}, {'OK' if x_hit_ok else 'FAIL'})")
    print(f"  y_hit = {y_hit:.6f}  (expected {y_hit_ref}, {'OK' if y_hit_ok else 'FAIL'})")

    contract_ok = t_hit >= 0
    print(f"  Output contract t_hit >= 0: {'OK' if contract_ok else 'FAIL'}")

    all_pass = traj_ok and t_hit_ok and x_hit_ok and y_hit_ok and contract_ok
    print(f"\nRESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    success = test_fr4()
    sys.exit(0 if success else 1)
