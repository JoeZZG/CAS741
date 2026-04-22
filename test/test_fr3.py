"""
T-FR-3 (Section 4.1.3): B-Only Speed Invariant + No Detector Hit
With E=0 and B=1 (both regions), the Lorentz force is always perpendicular to
velocity, so speed is conserved.  The horizontal detector at y=1.5 is above the
maximum y=0 reached by the circular orbit, so no hit occurs (t_hit=-1).

VnVPlan reference: T-FR-3
Initial state: m=1, q=1, vx0=1, vy0=0; kappa=1, omega=1 rad/s.
Expected:
  - t_hit = -1 (no hit)
  - Speed squared v^2 = vx^2 + vy^2 = 1 throughout simulation
  - Relative drift D = max|v^2 - v0^2| / v0^2 <= 1% (1e-2)
"""
import subprocess
import os
import sys
import ast

PYTHON_DIR = os.path.expanduser(
    "~/Desktop/Drasil741/code/drasil-example/trajecto/src/python"
)
INPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "input_fr3.txt")
)
OUTPUT_FILE = os.path.join(PYTHON_DIR, "output.txt")

DRIFT_TOL = 0.01  # 1% relative drift in speed^2


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


def test_fr3():
    print("=" * 60)
    print("T-FR-3: B-Only Speed Invariant + No Detector Hit")
    print("=" * 60)

    result = run_trajecto(INPUT_FILE)
    if result.returncode != 0:
        print(f"FAIL: Program exited with code {result.returncode}.")
        print(result.stderr[:500])
        return False

    out, traj = parse_output(OUTPUT_FILE)

    # --- No-hit output contract ---
    t_hit = float(out.get("t_hit", "0"))
    no_hit_ok = (t_hit == -1)
    print(f"  t_hit = {t_hit}  (expected -1, {'OK' if no_hit_ok else 'FAIL'})")
    print(f"  Output contract no-hit sentinel (t_hit=-1): {'OK' if no_hit_ok else 'FAIL'}")

    # --- Speed invariant check ---
    v0_sq = 1.0  # vx0=1, vy0=0
    max_drift = 0.0
    for pt in traj:
        v_sq = pt[2] ** 2 + pt[3] ** 2
        drift = abs(v_sq - v0_sq) / v0_sq
        max_drift = max(max_drift, drift)

    drift_ok = max_drift <= DRIFT_TOL
    print(f"\n  Speed^2 initial: {v0_sq}")
    print(f"  Max relative drift in speed^2: {max_drift:.4e}  "
          f"(tol={DRIFT_TOL:.0e}, {'OK' if drift_ok else 'FAIL'})")

    all_pass = no_hit_ok and drift_ok
    print(f"\nRESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    success = test_fr3()
    sys.exit(0 if success else 1)
