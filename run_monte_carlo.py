#!/usr/bin/env python3
"""
Monte Carlo validation suite for REBCO coil
"""

import numpy as np
import json
import argparse
from tqdm import tqdm
from rebco_core import REBCOCoil, QuenchProtection

def run_single_simulation(config=None, randomize=True, max_steps=500, dt=0.01):
    """Run one simulation with optional parameter randomization"""
    protection = QuenchProtection(detection_delay=0.02, dump_resistance=0.5)
    sim = REBCOCoil(protection=protection, config=config)
    
    if randomize:
        # Randomize initial conditions
        sim.T = np.random.uniform(20, 35)
        sim.I = np.random.uniform(0, 800)
        sim.config['Ic0'] = np.random.uniform(700, 900)
        sim.config['k_cool'] = np.random.uniform(4.0, 6.0)
    
    t = 0.0
    max_temp = sim.T
    time_to_quench = None
    history = {'T': [], 'I': [], 'Ic': []}
    
    for step in range(max_steps):
        # Random load spike
        if np.random.rand() < 0.01:
            sim.I *= np.random.uniform(1.1, 1.5)
            sim.I = min(sim.I, sim.config['I_max'])
        
        state = sim.step(dt, t)
        max_temp = max(max_temp, state['T'])
        history['T'].append(state['T'])
        history['I'].append(state['I'])
        history['Ic'].append(state['Ic'])
        
        if state['quench'] and time_to_quench is None:
            time_to_quench = t
        
        t += dt
        
        if state['quench'] and sim.protection.dumped and sim.I < 1.0:
            break
    
    return {
        'max_temp': max_temp,
        'final_damage': sim.damage,
        'quenched': sim.quench,
        'protected': sim.protection.dumped if sim.protection else False,
        'time_to_quench': time_to_quench,
        'steps': step + 1,
        'history': history
    }

def run_monte_carlo(n_runs=1000, max_steps=500, dt=0.01, save_path=None):
    """Run multiple simulations and aggregate statistics"""
    results = []
    
    for _ in tqdm(range(n_runs), desc="Monte Carlo"):
        result = run_single_simulation(max_steps=max_steps, dt=dt)
        results.append(result)
    
    # Aggregate statistics
    quench_rate = np.mean([r['quenched'] for r in results])
    protection_rate = np.mean([r['protected'] for r in results if r['quenched']]) if quench_rate > 0 else 0
    avg_max_temp = np.mean([r['max_temp'] for r in results])
    avg_damage = np.mean([r['final_damage'] for r in results])
    
    stats = {
        'n_runs': n_runs,
        'quench_rate': float(quench_rate),
        'protection_success_rate': float(protection_rate),
        'avg_max_temp_K': float(avg_max_temp),
        'avg_damage': float(avg_damage),
        'survival_rate': float(1 - quench_rate),
        'percentiles': {
            'temp_95': float(np.percentile([r['max_temp'] for r in results], 95)),
            'temp_99': float(np.percentile([r['max_temp'] for r in results], 99))
        }
    }
    
    print("\n" + "="*50)
    print("MONTE CARLO RESULTS")
    print("="*50)
    print(f"Runs: {n_runs}")
    print(f"Quench rate: {quench_rate*100:.1f}%")
    print(f"Protection success: {protection_rate*100:.1f}% (of quench events)")
    print(f"Average peak temperature: {avg_max_temp:.1f} K")
    print(f"Average damage: {avg_damage:.4f}")
    print(f"Survival rate: {(1-quench_rate)*100:.1f}%")
    print(f"95th percentile peak temp: {stats['percentiles']['temp_95']:.1f} K")
    
    if save_path:
        with open(save_path, 'w') as f:
            json.dump({'stats': stats, 'results': results}, f, indent=2)
        print(f"\nSaved to {save_path}")
    
    return results, stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='REBCO Monte Carlo validation')
    parser.add_argument('--runs', type=int, default=100, help='Number of simulations')
    parser.add_argument('--steps', type=int, default=500, help='Max steps per simulation')
    parser.add_argument('--dt', type=float, default=0.01, help='Time step (seconds)')
    parser.add_argument('--save', type=str, default='mc_results.json', help='Output file')
    
    args = parser.parse_args()
    run_monte_carlo(args.runs, args.steps, args.dt, args.save)
