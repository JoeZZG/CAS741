"""
T-FR-1 (Section 4.1.1): Input Specification + Echoing Inputs
Tests that Trajecto accepts a valid two-region, zero-field input without errors
and echoes every input parameter correctly in output.txt.

VnVPlan reference: T-FR-1
Input: m=1, q=1, x0=0, y0=0, vx0=2, vy0=1
       Two field-free regions [0,1]x[-1,1] and [1,2]x[-1,1]
       Vertical detector at x=1, y in [-1, 1], t_final=1.0
Expected: No InputError raised; output.txt contains echoed inputs.
"""
import subprocess
import os
import sys

PYTHON_DIR = os.path.expanduser(
    "~/Desktop/Drasil741/code/drasil-example/trajecto/src/python"
)
INPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "input_fr1.txt")
)
OUTPUT_FILE = os.path.join(PYTHON_DIR, "output.txt")


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
    with open(output_file, "r") as f:
        for line in f:
            line = line.strip()
            if " = " in line and not line.startswith("s ="):
                key, _, val = line.partition(" = ")
                data[key.strip()] = val.strip()
    return data


def test_fr1():
    print("=" * 60)
    print("T-FR-1: Input Specification + Echoing Inputs")
    print("=" * 60)

    result = run_trajecto(INPUT_FILE)

    # Check: no InputError exception raised
    if "InputError" in result.stdout or "InputError" in result.stderr:
        print("FAIL: InputError was raised for a valid input.")
        return False

    # Physical-range warnings are expected (m=1, q=1 exceed physical
    # constants), but no hard error
    if result.returncode != 0:
        print(f"FAIL: Program exited with non-zero code {result.returncode}.")
        print("stderr:", result.stderr[:500])
        return False

    # Parse output.txt for echoed parameters
    out = parse_output(OUTPUT_FILE)

    expected = {
        "m": "1.0",
        "q": "1.0",
        "x_0": "0.0",
        "y_0": "0.0",
        "v_x0": "2.0",
        "v_y0": "1.0",
        "N": "2",
        "N_col": "2",
        "w": "1.0",
        "h": "2.0",
        "x_grid": "0.0",
        "y_grid": "-1.0",
        "d_orient": "0",
        "d_pos": "1.0",
        "d_start": "-1.0",
        "d_len": "2.0",
        "t_final": "1.0",
    }

    all_pass = True
    for key, exp_val in expected.items():
        got = out.get(key, "<missing>")
        if got != exp_val:
            print(f"  FAIL echo: {key} expected {exp_val!r}, got {got!r}")
            all_pass = False
        else:
            print(f"  OK   echo: {key} = {got}")

    warnings = [l for l in result.stdout.splitlines() if l.startswith("Warning")]
    if warnings:
        print(f"\n  Note: {len(warnings)} physical-range warning(s) printed "
              "(expected for non-physical test parameters):")
        for w in warnings:
            print(f"    {w}")

    if all_pass:
        print("\nRESULT: PASS")
    else:
        print("\nRESULT: FAIL")
    return all_pass


if __name__ == "__main__":
    success = test_fr1()
    sys.exit(0 if success else 1)
