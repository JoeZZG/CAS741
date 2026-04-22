"""
Section 4.1.8: Input-Constraint and Pseudo-Oracle Coverage Summary

This script summarises the coverage mapping between test cases and the two
tables from VnVPlan Section 4.1.8:
  - Table: Input-constraint coverage
  - Table: Pseudo-oracle and output-contract coverage

No additional simulation is run; this script reports the mapping as documented.
"""


def main():
    print("=" * 70)
    print("Section 4.1.8: Input-Constraint and Pseudo-Oracle Coverage Summary")
    print("=" * 70)

    print("""
Input-Constraint Coverage
--------------------------
Constraint                    Reference Behaviour                       Tests
m > 0                         Reject invalid mass + error message       T-INV-1
q > 0                         (GAP) No check; code accepts q=0         T-INV-2 (gap)
t_final > 0                   Reject non-positive t_final + message     T-INV-3
detector orientation          (GAP) Soft warning only for d_orient>1   T-INV-4 (gap)
detector length (d_len > 0)   Reject non-positive d_len + message       T-INV-5
detector location             NOT APPLICABLE (grid-based input)         T-INV-6
region-corner geometry        NOT APPLICABLE (grid-based input)         T-INV-7, T-INV-8
equal region size             NOT APPLICABLE (grid enforces uniformity) T-INV-9
adjacency                     NOT APPLICABLE (grid tiles without gaps)  T-INV-10
no overlap                    NOT APPLICABLE (grid tiles no overlap)    T-INV-11
union rectangle               NOT APPLICABLE (grid union always rect.)  T-INV-12
""")

    print("""
Pseudo-Oracle and Output-Contract Coverage
-------------------------------------------
Category                        Reference Behaviour                        Tests
Pseudo-oracle: field-free       Analytic x(t)=2t, y(t)=t; hit check       T-FR-2
Pseudo-oracle: E-only           Analytic x(t)=0.5*t^2; hit check           T-FR-4
Pseudo-oracle: B-only           Speed conservation: |v^2 - v0^2|/v0^2<=1% T-FR-3, T-FR-5 (post R2)
Pseudo-oracle: multi-region     Field-switch confirmed via speed invariant  T-FR-5
Output contract: no-hit sentinel t_hit = -1 when no crossing              T-FR-3
Output contract: hit payload    t_hit >= 0 and (x_hit, y_hit) reported    T-FR-2, T-FR-4, T-FR-5, T-FR-6
""")

    print("""
Notes on VnVPlan gaps identified during test development
---------------------------------------------------------
1. T-INV-2 (q=0): The generated code has no q>0 hard constraint. The simulation
   runs normally with kappa=0 (no force). The VnVPlan expected an error here.

2. T-INV-4 (invalid orientation): The code uses integer d_orient (0 or 1) and
   only prints a soft Warning for values outside [0,1]; no exception is raised.
   The VnVPlan expected a hard error and a descriptive message.

3. T-INV-6 through T-INV-12: These 7 tests assume a corner-based region input
   where arbitrary non-rectangular, non-adjacent, or overlapping shapes can be
   specified. The actual implementation uses a structured grid (x_grid, y_grid,
   w, h) that always produces uniform, adjacent, axis-aligned tiles forming a
   rectangle. These invalid configurations cannot be expressed in the input
   format, making these tests not applicable.

4. Non-physical parameters: VnVPlan test inputs use m=1 kg, q=1 C, and
   t_final up to 4 s, which all exceed the software's physical constants
   (M_MAX=1e-25 kg, Q_MAX=1e-15 C, T_MAX=1e-4 s). The code issues soft
   warnings for these but continues execution, allowing the mathematical
   correctness to be verified.
""")


if __name__ == "__main__":
    main()
