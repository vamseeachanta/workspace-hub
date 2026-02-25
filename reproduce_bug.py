import math
from doris.pipeline.dnv_st_f101_collapse import characteristic_collapse_pressure, combined_loading_check

def test_collapse_against_cubic():
    D = 0.3239
    t = 0.01905
    SMYS = 448.0
    alpha_fab = 0.925
    E = 207000.0
    nu = 0.3
    f_o = 0.02 # 2% ovality

    p_el = 2.0 * E * (t / D) ** 3 / (1.0 - nu ** 2)
    smys_d = alpha_fab * SMYS
    p_p = 2.0 * smys_d * t / D

    # Correct C per DNV-ST-F101:2021 Eq (5.12)
    C_correct = p_el * p_p * f_o * (D / t)

    # Calculation in code:
    C_code = p_el * p_p**2 * f_o * (2.0 * t / (D - t))

    print(f"--- Collapse Check (f_o = {f_o}) ---")
    print(f"p_el: {p_el:.3f} MPa")
    print(f"p_p:  {p_p:.3f} MPa")
    print(f"C_correct: {C_correct:.3f}")
    print(f"C_code:    {C_code:.3f}")
    print(f"Ratio C_code/C_correct: {C_code/C_correct:.4f}")

    # Solve for p_c using correct C
    def f_correct(p):
        return p**3 - p_el*p**2 - (p_p**2 + C_correct)*p + p_el*p_p**2

    # Solve by bisection
    lo, hi = 0.0, p_p
    for _ in range(100):
        mid = (lo + hi) / 2
        if f_correct(mid) > 0: lo = mid
        else: hi = mid
    p_c_correct = hi

    p_c_code = characteristic_collapse_pressure(D, t, SMYS, f_o=f_o)

    print(f"p_c (correct): {p_c_correct:.3f} MPa")
    print(f"p_c (code):    {p_c_code:.3f} MPa")
    print(f"Error: {abs(p_c_code - p_c_correct)/p_c_correct*100:.2f} %")

def test_combined_loading():
    # Example values
    D = 0.3239
    t_nom = 0.01905
    SMYS = 448.0
    SMTS = 531.0
    p_li = 15.0
    p_e = 0.0
    M_applied = 500.0 # kN*m

    print("\n--- Combined Loading Check ---")
    result = combined_loading_check(p_li, p_e, M_applied, D, t_nom, SMYS, SMTS)
    print(f"Result utilization: {result['utilization']:.3f}")
    print(f"Pressure term: {result['pressure_term']:.3f}")
    print(f"Bending term:  {result['bending_term']:.3f}")
    
    # In DNV-ST-F101:2021, if p_li > p_e, the check is usually Burst (containment) 
    # and then Combined Loading with alpha_c.
    # The code's formula is (p_li - p_e)/p_b + (M/Mp)^2.
    # This formula is NOT in the standard for 5.4.5.

if __name__ == "__main__":
    test_collapse_against_cubic()
    test_combined_loading()
