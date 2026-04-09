import json
import numpy as np
import matplotlib.pyplot as plt

# Load results
with open('results_tuned.json', 'r') as f:
    data = json.load(f)

results = data['results']
stats = data['stats']

# Create figure with 2x2 subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('REBCO Coil Monte Carlo Results (500 runs)', fontsize=16)

# 1. Peak temperature histogram
temps = [r['max_temp'] for r in results]
axes[0,0].hist(temps, bins=30, edgecolor='black', alpha=0.7, color='red')
axes[0,0].axvline(np.percentile(temps, 95), color='orange', linestyle='--', label=f'95th: {stats["percentiles"]["temp_95"]:.0f}K')
axes[0,0].axvline(stats['avg_max_temp_K'], color='red', linestyle='-', label=f'Mean: {stats["avg_max_temp_K"]:.0f}K')
axes[0,0].set_xlabel('Peak Temperature (K)')
axes[0,0].set_ylabel('Frequency')
axes[0,0].set_title(f'Peak Temperature Distribution\nQuench rate: {stats["quench_rate"]*100:.1f}%')
axes[0,0].legend()

# 2. Damage histogram
damage = [r['final_damage'] for r in results]
axes[0,1].hist(damage, bins=30, edgecolor='black', alpha=0.7, color='blue')
axes[0,1].axvline(stats['avg_damage'], color='red', linestyle='-', label=f'Mean: {stats["avg_damage"]:.4f}')
axes[0,1].set_xlabel('Cumulative Damage')
axes[0,1].set_ylabel('Frequency')
axes[0,1].set_title('Damage Accumulation Distribution')
axes[0,1].legend()

# 3. Time to quench (for quenched runs)
times = [r['time_to_quench'] for r in results if r['time_to_quench'] is not None]
if times:
    axes[1,0].hist(times, bins=30, edgecolor='black', alpha=0.7, color='green')
    axes[1,0].axvline(np.mean(times), color='red', linestyle='-', label=f'Mean: {np.mean(times):.2f}s')
    axes[1,0].set_xlabel('Time to Quench (seconds)')
    axes[1,0].set_ylabel('Frequency')
    axes[1,0].set_title('Time to Quench Distribution')
    axes[1,0].legend()

# 4. Quench vs Survive pie chart
quenched_count = sum(1 for r in results if r['quenched'])
survived_count = len(results) - quenched_count
axes[1,1].pie([quenched_count, survived_count], labels=['Quenched', 'Survived'], 
              autopct='%1.1f%%', colors=['red', 'green'], startangle=90)
axes[1,1].set_title('Coil Fate')

plt.tight_layout()
plt.savefig('rebco_results.png', dpi=150)
print("✅ Plot saved to rebco_results.png")
