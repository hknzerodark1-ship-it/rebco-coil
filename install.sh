#!/bin/bash
# REBCO-Coil Installer

echo "🚀 Installing REBCO-Coil Simulation Suite..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install numpy tqdm

# Optional: matplotlib for plotting
read -p "Install matplotlib for plotting? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install matplotlib
fi

# Run test
echo ""
echo "✅ Installation complete!"
echo ""
echo "To activate: source venv/bin/activate"
echo "To run demo: python demo.py"
echo "To run Monte Carlo: python run_monte_carlo.py --runs 100"
