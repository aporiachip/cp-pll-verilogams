# ============================================================
# Makefile for CP-PLL Verilog-AMS Simulation (Hermes)
# Simulator: Cadence Xcelium (xrun) + Spectre
# Usage: source ../env_setup.sh && make run
# ============================================================

# --- Project paths ---
PROJ_DIR  := $(shell cd .. && pwd)
SIM_DIR   := $(PROJ_DIR)/sim

# --- Source files ---
AMS_SRC   := $(PROJ_DIR)/src/pfd.vams \
             $(PROJ_DIR)/src/cp.vams \
             $(PROJ_DIR)/src/lpf.vams \
             $(PROJ_DIR)/src/vco.vams \
             $(PROJ_DIR)/src/divider.vams \
             $(PROJ_DIR)/src/pll_top.vams
TB_SRC    := $(SIM_DIR)/tb_pll.vams
ALL_SRC   := $(AMS_SRC) $(TB_SRC)

# --- Xcelium/xrun options ---
# -ams:             enable AMS (analog mixed-signal) simulation
# -timescale:       set simulation time precision
# +access+r:        read access to all signals
# -analogcontrol:   Spectre transient analysis control file
# -input:           TCL script to record waveforms (probe.tcl)
XRUN      := xrun
XRUN_OPTS := -ams \
             -timescale 1ps/1fs \
             +access+r \
             -status \
             -analogcontrol $(PROJ_DIR)/analog_control.scs \
             -input $(SIM_DIR)/probe.tcl

# --- Simulation control ---
TOP       := tb_pll

# ============================================================
# Targets
# ============================================================

.PHONY: all run sim clean wave help

all: run

# Run simulation
run: $(SIM_DIR)
	cd $(SIM_DIR) && $(XRUN) $(XRUN_OPTS) \
	  $(ALL_SRC) -top $(TOP)

# Same as run
sim: run

# Create sim directory
$(SIM_DIR):
	mkdir -p $(SIM_DIR)

# Open waveform in SimVision
wave:
	cd $(SIM_DIR) && simvision waves.shm &

# Clean simulation files
clean:
	rm -rf $(SIM_DIR)/xcelium.d $(SIM_DIR)/xrun.* $(SIM_DIR)/waves.shm $(SIM_DIR)/.simvision $(SIM_DIR)/*.log $(SIM_DIR)/*.key $(SIM_DIR)/*.diag

# Help
help:
	@echo "============================================"
	@echo " CP-PLL Verilog-AMS Simulation (Hermes)"
	@echo "============================================"
	@echo " make run    - Run xrun simulation"
	@echo " make sim    - Same as run"
	@echo " make wave   - Open SimVision waveform viewer"
	@echo " make clean  - Clean simulation files"
	@echo " make help   - Show this help"
	@echo ""
	@echo " PLL Specs:"
	@echo "   fref  = 50 MHz"
	@echo "   fout  = 10 GHz (N=200)"
	@echo "   Kvco  = 50 MHz/V"
	@echo "   Icp   = 100 uA"
	@echo "   LPF   = 3rd order passive"
	@echo "============================================"


# ============================================================
# Noise verification
# ============================================================
noise:
	cd $(PROJ_DIR)/noise_tb && source ../env_setup.sh && $(MAKE) noise

noise_report:
	cd $(PROJ_DIR)/noise_tb && source ../env_setup.sh && $(MAKE) noise_report

noise_clean: clean
	cd $(PROJ_DIR)/noise_tb && $(MAKE) -f Makefile clean_noise
