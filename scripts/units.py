"""Unit conversions for 1_offcenter_zoom runs (code units Mpc/h, 1e10 Msun/h, km/s; a = scale factor).

    u = Units.from_params(run.params)
    u.mass_msun(m), u.length_kpc(x, a), u.rho_cgs(rho_phys_code), u.energy_erg(e),
    u.power_erg_s(p), u.mdot_msun_yr(md), u.t_gyr(a)
"""
import numpy as np
from scipy.integrate import quad

MSUN = 1.98847e33
MP = 1.67262192e-24
KPC = 3.085678e21
YR = 3.15576e7
GYR = 3.15576e16
C_KMS = 2.99792458e5
KB = 1.380649e-16
XH = 0.76


def nH(rho_cgs):
    """hydrogen number density [cm^-3] from gas density [g/cm^3]"""
    return XH * np.asarray(rho_cgs) / MP


class Units:
    def __init__(self, h, omega_m, omega_l, ul=3.085678e24, um=1.989e43, uv=1e5):
        self.h, self.om, self.ol = float(h), float(omega_m), float(omega_l)
        self.ul, self.um, self.uv = float(ul), float(um), float(uv)
        self.ut = self.ul / self.uv  # code time [s/h]

    @classmethod
    def from_params(cls, p):
        g = lambda k, d=None: float(p[k]) if k in p else d
        return cls(g("HubbleParam"), g("Omega0"), g("OmegaLambda"), g("UnitLength_in_cm", 3.085678e24),
                   g("UnitMass_in_g", 1.989e43), g("UnitVelocity_in_cm_per_s", 1e5))

    def mass_msun(self, m):
        return np.asarray(m) * self.um / MSUN / self.h

    def length_kpc(self, x, a):
        """comoving code length -> physical kpc"""
        return np.asarray(x) * self.ul / KPC / self.h * a

    def rho_cgs(self, rho):
        """physical code density -> g/cm^3 (comoving input: divide by a^3 first)"""
        return np.asarray(rho) * self.um / self.ul**3 * self.h**2

    def energy_erg(self, e):
        return np.asarray(e) * self.um * self.uv**2 / self.h

    def power_erg_s(self, p):
        return np.asarray(p) * self.um * self.uv**3 / self.ul

    def mdot_msun_yr(self, md):
        return np.asarray(md) * self.um / self.ut / (MSUN / YR)

    def t_gyr(self, a):
        """cosmic time since the big bang for flat LCDM (radiation neglected)"""
        hubble_time_gyr = 977.8 / (100.0 * self.h)
        f = lambda x: 1.0 / (x * np.sqrt(self.om / x**3 + self.ol))
        return np.vectorize(lambda aa: quad(f, 1e-8, aa)[0] * hubble_time_gyr)(a) + 0.0
