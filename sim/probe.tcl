# ============================================================
# TCL script for waveform recording (SimVision SHM database)
# Usage: xrun ... -input probe.tcl
# After simulation: simvision waves.shm &
# ============================================================

# Create SHM waveform database
database -open waves -shm

# Probe all signals in the testbench (digital + analog)
probe -create tb_pll -all -depth all -database waves

# Run the simulation
run

# Exit when done
quit
