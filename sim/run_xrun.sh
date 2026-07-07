#!/bin/bash
# run_xrun.sh — One-click CP-PLL simulation with xrun
# Usage: ./run_xrun.sh [sim_time]
#        sim_time: e.g., 20u, 50u, 100u (default: 20u)

set -e

SIMTIME="${1:-20u}"
PROJ_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="${PROJ_DIR}/src"
SIM_DIR="${PROJ_DIR}/sim"

echo "================================================"
echo " CP-PLL Verilog-AMS Simulation"
echo "================================================"
echo " Project dir : ${PROJ_DIR}"
echo " Source dir  : ${SRC_DIR}"
echo " Sim dir     : ${SIM_DIR}"
echo " Sim time    : ${SIMTIME}"
echo "================================================"

# Check if xrun is available
if ! command -v xrun &> /dev/null; then
    echo "ERROR: xrun not found in PATH"
    echo "  Please source the Cadence setup script first, e.g.:"
    echo "  source /path/to/cadence/XCELIUM*/tools/bin/cadence_welcome.sh"
    exit 1
fi

# Create wave directory
mkdir -p "${SIM_DIR}/waves"

# Clean previous run
rm -rf "${SIM_DIR}/xcelium.d" "${SIM_DIR}/xrun.*" "${SIM_DIR}/cov_work"

# Run simulation
cd "${SIM_DIR}"

echo ""
echo "=== Compiling & running simulation ==="
xrun -64bit -ams \
    -access +rwc \
    -timescale 1ps/1ps \
    -mess -status \
    "${SRC_DIR}/pfd.vams" \
    "${SRC_DIR}/cp.vams" \
    "${SRC_DIR}/lpf.vams" \
    "${SRC_DIR}/vco.vams" \
    "${SRC_DIR}/divider.vams" \
    "${SRC_DIR}/pll_top.vams" \
    "${SIM_DIR}/tb_pll.vams" \
    -sim_end "${SIMTIME}" \
    -input probe.tcl

echo ""
echo "=== Simulation complete ==="
echo "Waveform database: ${SIM_DIR}/waves/waves.shm"

# Offer to open SimVision
echo ""
read -p "Open SimVision? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    simvision waves/waves.shm &
fi
