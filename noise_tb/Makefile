# ============================================================
# Makefile for PLL Module Noise Verification
# Simulator: Cadence Xcelium (xrun) + Spectre
# Python:    ~/miniconda3/bin/python (for plots w/ numpy)
# Usage:     source ../env_setup.sh && make <target>
# ============================================================

PROJ_DIR  := $(shell cd .. && pwd)
NOISE_DIR := $(PROJ_DIR)/noise_tb
SRC_DIR   := $(PROJ_DIR)/src
SCRIPT_DIR := $(PROJ_DIR)/scripts

XRUN      := xrun
XRUN_OPTS := -ams -timescale 1ps/1fs +access+r -status

NOISE_CTRL := $(NOISE_DIR)/noise_ctrl.scs
PY         := $(HOME)/miniconda3/bin/python

# ============================================================
# Targets
# ============================================================

.PHONY: all noise_sim noise_analyze noise_plot noise_vco noise_report noise clean help

all: noise_report

# ----------------------------------------------------------
# Quick: analyze existing data (no re-simulation)
# ----------------------------------------------------------
noise_analyze:
	@echo "=== Running noise analysis (pure Python FFT) ==="
	cd $(NOISE_DIR) && $(PY) $(SCRIPT_DIR)/noise_analyze.py

noise_plot:
	@echo "=== Generating PSD plot ==="
	cd $(NOISE_DIR) && $(PY) $(SCRIPT_DIR)/gen_noise_plots.py
	@echo "  -> $(NOISE_DIR)/noise_report.png"

noise_vco:
	@echo "=== VCO PN model verification ==="
	$(PY) $(SCRIPT_DIR)/vco_pn_verify.py

noise_report: noise_analyze noise_plot noise_vco
	@echo ""
	@echo "============================================"
	@echo "  Report:  $(NOISE_DIR)/noise_report.png"
	@echo "============================================"

# ----------------------------------------------------------
# Full simulation + analysis
# ----------------------------------------------------------
noise_sim: noise_sim_cp noise_sim_pfd noise_sim_div

noise_sim_cp: $(NOISE_CTRL)
	@echo "=== CP noise sim ==="
	cd $(NOISE_DIR) && $(XRUN) $(XRUN_OPTS) \
	  -analogcontrol $(NOISE_CTRL) \
	  $(SRC_DIR)/cp.vams tb_cp_noise.vams -top tb_cp_noise

noise_sim_pfd: $(NOISE_CTRL)
	@echo "=== PFD noise sim ==="
	cd $(NOISE_DIR) && $(XRUN) $(XRUN_OPTS) \
	  -analogcontrol $(NOISE_CTRL) \
	  $(SRC_DIR)/pfd.vams tb_pfd_noise.vams -top tb_pfd_noise

noise_sim_div: $(NOISE_CTRL)
	@echo "=== Divider noise sim ==="
	cd $(NOISE_DIR) && $(XRUN) $(XRUN_OPTS) \
	  -analogcontrol $(NOISE_CTRL) \
	  $(SRC_DIR)/divider.vams tb_div_noise.vams -top tb_div_noise

$(NOISE_CTRL):
	@echo 'sim1 tran stop=1u step=20p method=gear2only noisefmin=10k noisefmax=100M noiseseed=123' > $@

# Full flow
noise: noise_sim noise_report

# Clean
clean:
	rm -rf $(NOISE_DIR)/xcelium.d $(NOISE_DIR)/xrun.* \
	       $(NOISE_DIR)/*.log $(NOISE_DIR)/*.key $(NOISE_DIR)/*.diag \
	       $(NOISE_DIR)/cp_noise_data.txt \
	       $(NOISE_DIR)/pfd_noise_data.txt \
	       $(NOISE_DIR)/div_noise_data.txt \
	       $(NOISE_DIR)/noise_report.png

help:
	@echo "============================================"
	@echo " PLL Module Noise Verification"
	@echo "============================================"
	@echo " Quick (existing data):"
	@echo "   make noise_analyze  - FFT analysis"
	@echo "   make noise_plot     - PSD plot (needs numpy)"
	@echo "   make noise_vco      - VCO PN model verify"
	@echo "   make noise_report   - All above"
	@echo ""
	@echo " Full flow (re-run sims):"
	@echo "   make noise_sim      - Run all noise sims"
	@echo "   make noise          - Sim + report"
	@echo "   make clean          - Remove all outputs"
	@echo ""
	@echo " Noise params in noise_ctrl.scs"
	@echo "============================================"
