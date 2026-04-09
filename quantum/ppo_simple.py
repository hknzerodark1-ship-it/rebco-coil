import numpy as np
import matplotlib.pyplot as plt

print("=" * 60)
print("PPO + Qubitization Proxy - FeMo-co Resource Optimizer")
print("=" * 60)

lambda_values = [500, 1000, 2000, 3000, 5000]
epsilon_values = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2]

best_runtime = float('inf')
best_config = None
best_error = float('inf')

print("\nSearching optimal (λ, ε) for FeMo-co LLDUC...\n")
print(f"{'λ':>8} | {'ε':>10} | {'Runtime (h)':>12} | {'Error (Ha)':>12} | {'Chem Acc?':>10}")
print("-" * 65)

for lam in lambda_values:
    for eps in epsilon_values:
        runtime = (lam / eps) * 1e-3
        error = eps * np.sqrt(lam) * 10
        chem_accurate = error < 0.0016
        status = "YES" if chem_accurate else "NO"
        
        if chem_accurate and error < best_error:
            best_error = error
            best_runtime = runtime
            best_config = (lam, eps)
            
        print(f"{lam:8d} | {eps:10.0e} | {runtime:12.2f} | {error:12.5f} | {status:>10}")

print("\n" + "=" * 60)
print("OPTIMAL CONFIGURATION:")
print(f"   λ = {best_config[0]}")
print(f"   ε = {best_config[1]:.0e} Ha")
print(f"   Runtime = {best_runtime:.2f} hours")
print(f"   Error = {best_error:.5f} Ha")
print("=" * 60)

# Create plot
plt.figure(figsize=(10, 6))
for lam in lambda_values:
    errors = [eps * np.sqrt(lam) * 10 for eps in epsilon_values]
    runtimes = [(lam / eps) * 1e-3 for eps in epsilon_values]
    plt.plot(runtimes, errors, 'o-', label=f'λ={lam}', linewidth=2, markersize=8)

plt.axhline(0.0016, color='red', linestyle='--', linewidth=2, label='Chemical accuracy (1.6 mHa)')
plt.xlabel('Runtime (hours)', fontsize=12)
plt.ylabel('Energy Error (Hartree)', fontsize=12)
plt.title('FeMo-co LLDUC: Runtime vs Accuracy Tradeoff', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('femoco_tradeoff.png', dpi=150)
print("\nPlot saved: femoco_tradeoff.png")
