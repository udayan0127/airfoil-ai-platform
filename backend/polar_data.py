"""
Generates drag polar data (Cl vs Cd curves) for each airfoil.
Real XFOIL data would be ideal, but for our MVP we generate physically
plausible curves using a quadratic drag polar approximation:
    Cd = Cd_min + K * (Cl - Cl_ldmax)^2
where Cl_ldmax is the Cl at best L/D ratio, and K is a curvature factor.
"""
import math


def cl_to_alpha(cl, alpha_zero_lift=-2.0, slope=6.0):
    """
    Simple empirical conversion: CL to angle of attack (degrees).
    For most cambered airfoils near cruise, alpha ≈ CL * 5-7 degrees,
    with zero-lift AoA around -2 degrees. This is an approximation,
    not a substitute for real XFOIL/wind tunnel polar data.
    """
    return round(alpha_zero_lift + cl * slope, 2)


def generate_polar(airfoil: dict, num_points: int = 40) -> dict:
    """
    Given an airfoil dict with cl_max, cd_min, best_cl_cd,
    generate a drag polar curve (Cl vs Cd vs Alpha vs L/D).
    """
    cl_max = airfoil["cl_max"]
    cd_min = airfoil["cd_min"]
    ld_max = airfoil["best_cl_cd"]

    # Cl at which drag is minimum (near L/D max point)
    cl_ldmax = cd_min * ld_max  # from L/D = Cl/Cd => Cl = LD * Cd

    # Curvature factor - controls how fast drag rises off min
    # Fit so that at cl_max, Cd is roughly 2x cd_min (realistic for many airfoils)
    delta = cl_max - cl_ldmax
    if delta <= 0:
        K = 0.01  # fallback
    else:
        K = (cd_min * 1.5) / (delta * delta)

    # Generate points across Cl range
    cl_min = -0.4  # negative lift (inverted flight)
    curve = []
    for i in range(num_points):
        cl = cl_min + (cl_max - cl_min) * (i / (num_points - 1))

        # Quadratic polar: Cd rises as Cl departs from cl_ldmax
        cd = cd_min + K * (cl - cl_ldmax) ** 2

        # Add stall behavior - Cd rises sharply near cl_max
        if cl > cl_max * 0.9:
            stall_factor = ((cl - cl_max * 0.9) / (cl_max * 0.1)) ** 2
            cd += stall_factor * cd_min * 3

        # L/D at this point
        ld = cl / cd if cd > 0 else 0

        curve.append({
            "cl": round(cl, 4),
            "cd": round(cd, 6),
            "ld": round(ld, 2),
            "alpha": cl_to_alpha(cl)
        })

    return {
        "name": airfoil["name"],
        "curve": curve,
        "cl_ldmax": round(cl_ldmax, 3),
        "operating_point": {
            "cl": cl_ldmax,
            "cd": cd_min
        }
    }


def generate_ld_vs_airspeed(airfoil: dict, weight_g: float, wing_area_m2: float,
                              v_min: float = 5.0, v_max: float = 30.0,
                              num_points: int = 50) -> dict:
    """
    Generate L/D ratio vs airspeed curve for level flight.
    For level flight: Cl_required = 2*W / (rho * V^2 * S)
    Cd is then computed from the same quadratic polar model used in generate_polar().
    """
    rho = 1.225  # kg/m^3, sea level
    weight_n = weight_g * 9.81 / 1000

    cl_max = airfoil["cl_max"]
    cd_min = airfoil["cd_min"]
    ld_max = airfoil["best_cl_cd"]
    cl_ldmax = cd_min * ld_max

    delta = cl_max - cl_ldmax
    K = (cd_min * 1.5) / (delta * delta) if delta > 0 else 0.01

    curve = []
    stall_speed_ms = None

    for i in range(num_points):
        v = v_min + (v_max - v_min) * (i / (num_points - 1))

        cl_required = (2 * weight_n) / (rho * v**2 * wing_area_m2)

        # Flag/clamp points beyond stall - level flight isn't achievable here
        stalled = cl_required > cl_max
        if stalled and stall_speed_ms is None:
            stall_speed_ms = round(v, 2)
        cl_used = min(cl_required, cl_max)

        cd = cd_min + K * (cl_used - cl_ldmax) ** 2
        ld = cl_used / cd if cd > 0 else 0

        curve.append({
            "v_ms": round(v, 2),
            "v_kmh": round(v * 3.6, 2),
            "cl": round(cl_used, 4),
            "cd": round(cd, 6),
            "ld": round(ld, 2),
            "stalled": stalled
        })

    valid_ld = [p["ld"] for p in curve if not p["stalled"]]

    return {
        "name": airfoil["name"],
        "curve": curve,
        "max_ld": max(valid_ld) if valid_ld else 0,
        "stall_speed_ms": stall_speed_ms
    }


if __name__ == "__main__":
    # Test
    test_airfoil = {
        "name": "NACA 2412",
        "cl_max": 1.4,
        "cd_min": 0.0075,
        "best_cl_cd": 65
    }
    polar = generate_polar(test_airfoil)
    print(f"Generated {len(polar['curve'])} points")
    print(f"First 3: {polar['curve'][:3]}")
    print(f"Last 3: {polar['curve'][-3:]}")
    print(f"Cl at L/D max: {polar['cl_ldmax']}")

    ld_curve = generate_ld_vs_airspeed(test_airfoil, weight_g=990, wing_area_m2=0.197)
    print(f"\nL/D vs airspeed: {len(ld_curve['curve'])} points")
    print(f"Max L/D: {ld_curve['max_ld']}, Stall speed: {ld_curve['stall_speed_ms']} m/s")