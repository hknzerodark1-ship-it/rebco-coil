#!/usr/bin/env python3
"""
Quick demo of REBCO coil simulation
"""

import time
from rebco_core import REBCOCoil, QuenchProtection

def main():
    print("🔥 REBCO Coil Simulation Demo")
    print("="*40)
    
    # Create coil with protection
    protection = QuenchProtection(detection_delay=0.02, dump_resistance=0.5)
    sim = REBCOCoil(protection=protection)
    
    print(f"Initial: T={sim.T:.1f}K, I={sim.I:.0f}A, Ic={sim.Ic():.0f}A")
    
    dt = 0.01
    t = 0.0
    
    # Force a current spike to trigger quench
    spike_time = 1.0
    spike_duration = 0.5
    
    print("\nRunning simulation...")
    print("-"*40)
    
    for step in range(500):
        # Apply current spike
        if spike_time <= t < spike_time + spike_duration:
            sim.I = 1200.0
        else:
            sim.I = 500.0
        
        state = sim.step(dt, t)
        
        if step % 50 == 0:
            status = "QUENCHED!" if state['quench'] else "OK"
            print(f"t={t:.2f}s: T={state['T']:.1f}K, I={state['I']:.0f}A, {status}")
        
        t += dt
        
        if state['quench'] and sim.protection.dumped and sim.I < 1.0:
            print(f"\nQuench event at t={t:.2f}s")
            print(f"Peak temperature: {state['T']:.1f}K")
            print(f"Protection triggered: {state['dumped']}")
            break
    
    print("\n" + "="*40)
    print("Demo complete.")
    print(f"Final damage: {sim.damage:.4f}")
    print(f"Coil {'survived' if not sim.quench else 'failed'}")

if __name__ == "__main__":
    main()
