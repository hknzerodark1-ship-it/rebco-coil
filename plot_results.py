import json
import matplotlib.pyplot as plt

with open('results_tuned.json', 'r') as f:
    data = json.load(f)

temps = [r['max_temp'] for r in data['results']]
plt.hist(temps, bins=30, color='red', alpha=0.7)
plt.xlabel('Peak Temperature (K)')
plt.ylabel('Frequency')
plt.title(f"REBCO Monte Carlo: {len(temps)} runs\nQuench Rate: {data['stats']['quench_rate']*100:.1f}%")
plt.savefig('rebco_results.png', dpi=150)
print("✅ Plot saved: rebco_results.png")
