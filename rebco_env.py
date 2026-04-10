import numpy as np
from rebco_core import REBCOCoil, QuenchProtection

try:
    import gym
    from gym import spaces
except ImportError:
    import gymnasium as gym
    from gymnasium import spaces

class REBCOEnv(gym.Env):
    def __init__(self, dt=0.01, max_steps=500):
        super().__init__()
        self.dt = dt
        self.max_steps = max_steps
        self.action_space = spaces.Box(
            low=np.array([0.0, 0.8]), high=np.array([1200.0, 1.5]), dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=np.array([20.0, 0.0, 0.0, 0.0, 0.7, -10.0]),
            high=np.array([120.0, 1200.0, 1000.0, 1.0, 1.3, 10.0]),
            dtype=np.float32
        )
        self.sim = None
        self.cooling_base = 5.0

    def reset(self):
        protection = QuenchProtection()
        self.sim = REBCOCoil(protection=protection)
        self.sim.config['k_cool'] = self.cooling_base
        return self._get_obs()

    def _get_obs(self):
        cooling_eff = self.sim.config['k_cool'] / self.cooling_base
        return np.array([self.sim.T, self.sim.I, self.sim.Ic(), self.sim.damage, cooling_eff, 0.0])

    def step(self, action):
        current_target, cooling_boost = action
        self.sim.config['k_cool'] = self.cooling_base * np.clip(cooling_boost, 0.8, 1.5)
        k_ramp = 0.1
        self.sim.I += k_ramp * (current_target - self.sim.I) * self.dt
        state = self.sim.step(self.dt, 0)
        reward = - (state['T'] / 120.0)**2 - 0.5 * state['damage'] - 100.0 * int(state['quench'])
        done = state['quench'] or state['T'] > 120 or state['damage'] > 0.5
        return self._get_obs(), reward, done, False, {}
