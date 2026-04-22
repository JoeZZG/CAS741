"""
T-FR-2 (Section 4.1.2): Field-Free Analytic Trajectory + Vertical Detector Hit
With E=0, B=0 the motion is uniform: x(t)=2t, y(t)=t.
Analytic detector hit: t_hit=0.5 s, x_hit=1.0 m, y_hit=0.5 m.

VnVPlan reference: T-FR-2
Tolerance: 1e-2 (one ODE sample step = t_final/1000 = 0.001 s of error in time,
propagated to position; acceptable relative error for this coarse grid).
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
    os.path.join(os.path.dirname(__file__), "input_fr2.txt")
)
OUTPUT_FILE = os.path.join(PYTHON_DIR, "output.txt")

TOL_HIT = 1e-2   # tolerance for t_hit, x_hit, y_hit
TOL_TRAJ = 1e-4  # tolerance for individual trajectory position samples


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


def test_fr2():
    print("=" * 60)
    print("T-FR-2: Field-Free Analytic Trajectory + Vertical Detector Hit")
    print("=" * 60)

    result = run_trajecto(INPUT_FILE)
    if result.returncode != 0:
        print(f"FAIL: Program exited with code {result.returncode}.")
        print(result.stderr[:500])
        return False

    out, traj = parse_output(OUTPUT_FILE)

    # --- Trajectory comparison against analytic solution x(t)=2t, y(t)=t ---
    t_final = 1.0
    n_pts = len(traj)
    t_step = t_final / (n_pts - 1)
    max_x_err = 0.0
    max_y_err = 0.0
    for i, pt in enumerate(traj):
        t_i = i * t_step
        x_ref = 2.0 * t_i
        y_ref = 1.0 * t_i
        max_x_err = max(max_x_err, abs(pt[0] - x_ref))
        max_y_err = max(max_y_err, abs(pt[1] - y_ref))

    print(f"  Trajectory samples: {n_pts}")
    print(f"  Max |x_num - x_ref|: {max_x_err:.2e}  (tol={TOL_TRAJ:.0e})")
    print(f"  Max |y_num - y_ref|: {max_y_err:.2e}  (tol={TOL_TRAJ:.0e})")
    traj_ok = max_x_err <= TOL_TRAJ and max_y_err <= TOL_TRAJ

    # --- Detector hit values ---
    t_hit = float(out.get("t_hit", "-999"))
    x_hit = float(out.get("x_hit", "-999"))
    y_hit = float(out.get("y_hit", "-999"))

    t_hit_ref, x_hit_ref, y_hit_ref = 0.5, 1.0, 0.5
    t_hit_ok = abs(t_hit - t_hit_ref) <= TOL_HIT
    x_hit_ok = abs(x_hit - x_hit_ref) <= TOL_HIT
    y_hit_ok = abs(y_hit - y_hit_ref) <= TOL_HIT

    print(f"\n  t_hit = {t_hit}  (expected {t_hit_ref}, {'OK' if t_hit_ok else 'FAIL'})")
    print(f"  x_hit = {x_hit}  (expected {x_hit_ref}, {'OK' if x_hit_ok else 'FAIL'})")
    print(f"  y_hit = {y_hit}  (expected {y_hit_ref}, {'OK' if y_hit_ok else 'FAIL'})")

    # Output contract: t_hit >= 0
    contract_ok = t_hit >= 0
    print(f"  Output contract t_hit >= 0: {'OK' if contract_ok else 'FAIL'}")

    all_pass = traj_ok and t_hit_ok and x_hit_ok and y_hit_ok and contract_ok
    print(f"\nRESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    success = test_fr2()
    sys.exit(0 if success else 1)
