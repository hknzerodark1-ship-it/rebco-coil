import numpy as np

class QuenchProtection:
    def __init__(self, detection_delay=0.02, dump_resistance=0.5):
        self.detection_delay = detection_delay
        self.dump_resistance = dump_resistance
        self.trigger_time = None
        self.dumped = False

    def update(self, t, quench_detected):
        if quench_detected and not self.dumped:
            if self.trigger_time is None:
                self.trigger_time = t + self.detection_delay
        if self.trigger_time is not None and t >= self.trigger_time:
            self.dumped = True
        return self.dumped

class REBCOCoil:
    def __init__(self, protection=None):
        self.T = 20.0
        self.I = 500.0
        self.damage = 0.0
        self.quench = False
        self.protection = protection
        self.Ic0 = 800.0
        self.Tc = 90.0
        self.kB = 0.1
        self.R_normal = 0.01
        self.thermal_mass = 500.0
        self.k_cool = 5.0
        self.T_coolant = 15.0

    def Ic(self):
        return self.Ic0 * (1 - (self.T / self.Tc)**2) * (1 / (1 + self.kB * 1.5))

    def step(self, dt, t_global):
        Ic = self.Ic()
        if self.quench:
            R_eff = self.R_normal
        elif self.I < Ic:
            R_eff = 1e-9
        else:
            R_eff = self.R_normal * (self.I / Ic)**20

        quench_detected = (self.T > 80) or (self.I > Ic * 1.1)
        if quench_detected:
            self.quench = True

        dumped = False
        if self.protection:
            dumped = self.protection.update(t_global, quench_detected)

        if dumped:
            L = 0.1
            tau = L / self.protection.dump_resistance
            self.I *= np.exp(-dt / tau)

        P_ac = np.random.normal(0.5, 0.1)
        P_loss = self.I**2 * R_eff + P_ac

        if dumped:
            P_dump = self.I**2 * self.protection.dump_resistance
            P_loss += P_dump

        cooling = self.k_cool * (self.T - self.T_coolant)
        dT = (P_loss - cooling) / self.thermal_mass
        self.T += dT * dt

        if self.T > 30:
            self.damage += (self.T - 30) * 1e-4 * dt
        self.damage = min(self.damage, 1.0)

        return self.T, self.damage, self.quench, dumped
