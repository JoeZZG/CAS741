"""
T-FR-6 (Section 4.1.6): Horizontal Detector Hit Case
With E=0, B=0 the motion is uniform: x(t)=t, y(t)=t.
A horizontal detector at y=1.0 is hit when t=1.0 s, at x=1.0 m.

VnVPlan reference: T-FR-6
Input: m=1, q=1, x0=0, y0=0, vx0=1, vy0=1
       Two field-free regions; horizontal detector at y=1.0, x in [-1, 3]
Expected: t_hit=1.0 s, x_hit=1.0 m, y_hit=1.0 m
Tolerance: 1e-2
"""
import subprocess
import os
import sys
import ast

PYTHON_DIR = os.path.expanduser(
    "~/Desktop/Drasil741/code/drasil-example/trajecto/src/python"
)
INPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "input_fr6.txt")
)
OUTPUT_FILE = os.path.join(PYTHON_DIR, "output.txt")

TOL_HIT = 1e-2


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


def test_fr6():
    print("=" * 60)
    print("T-FR-6: Horizontal Detector Hit Case")
    print("=" * 60)

    result = run_trajecto(INPUT_FILE)
    if result.returncode != 0:
        print(f"FAIL: Program exited with code {result.returncode}.")
        print(result.stderr[:500])
        return False

    out, traj = parse_output(OUTPUT_FILE)

    t_hit = float(out.get("t_hit", "-999"))
    x_hit = float(out.get("x_hit", "-999"))
    y_hit = float(out.get("y_hit", "-999"))

    t_hit_ref, x_hit_ref, y_hit_ref = 1.0, 1.0, 1.0
    t_hit_ok = abs(t_hit - t_hit_ref) <= TOL_HIT
    x_hit_ok = abs(x_hit - x_hit_ref) <= TOL_HIT
    y_hit_ok = abs(y_hit - y_hit_ref) <= TOL_HIT
    contract_ok = t_hit >= 0

    print(f"  t_hit = {t_hit:.6f}  (expected {t_hit_ref}, {'OK' if t_hit_ok else 'FAIL'})")
    print(f"  x_hit = {x_hit:.6f}  (expected {x_hit_ref}, {'OK' if x_hit_ok else 'FAIL'})")
    print(f"  y_hit = {y_hit:.6f}  (expected {y_hit_ref}, {'OK' if y_hit_ok else 'FAIL'})")
    print(f"  Output contract t_hit >= 0: {'OK' if contract_ok else 'FAIL'}")

    all_pass = t_hit_ok and x_hit_ok and y_hit_ok and contract_ok
    print(f"\nRESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    success = test_fr6()
    sys.exit(0 if success else 1)
