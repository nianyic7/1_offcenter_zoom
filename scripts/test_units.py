#!/usr/bin/env python3
"""Tests for scripts/units.py against independent reference values."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U

u = U.Units.from_params({"HubbleParam": "0.6774", "Omega0": "0.3089", "OmegaLambda": "0.6911"})
h = 0.6774
rel = lambda x, y: abs(x - y) / abs(y)
checks = [
    # rho_crit = 27.754 (1e10 Msun/h)/(Mpc/h)^3 = 1.87847e-29 h^2 g/cm^3
    ("rho_crit", rel(u.rho_cgs(27.7536627), 1.87847e-29 * h**2) < 1e-3),
    # code Mdot unit: 1e10 Msun/h per (977.8 Gyr/h) = 0.010227 Msun/yr (h cancels; Mpc/h time unit)
    ("mdot", rel(u.mdot_msun_yr(1.0), 0.010227) < 2e-3),
    ("mass", rel(u.mass_msun(1.0), 1.989e43 / U.MSUN / h) < 1e-12),
    ("length", rel(u.length_kpc(1.0, 0.5), 500.0 / h) < 1e-12),
    ("energy", rel(u.energy_erg(1.0), 1.989e43 * 1e10 / h) < 1e-12),
    # code power unit = um*uv^3/ul (h cancels)
    ("power", rel(u.power_erg_s(1.0), 1.989e43 * 1e15 / 3.085678e24) < 1e-12),
    # Planck15-like age of the universe
    ("t0", abs(u.t_gyr(1.0) - 13.80) < 0.03),
    ("nH", rel(U.nH(1.6726e-24 / 0.76), 1.0) < 1e-3),
]
bad = [n for n, ok in checks if not ok]
if bad:
    print("FAIL test_units:", bad, f"rho={u.rho_cgs(27.7536627):.4e} mdot={u.mdot_msun_yr(1):.4f} t0={u.t_gyr(1):.3f}")
    sys.exit(1)
print(f"PASS test_units: {len(checks)} checks (t0={u.t_gyr(1.0):.3f} Gyr)")
