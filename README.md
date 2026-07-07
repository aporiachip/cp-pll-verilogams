# CP-PLL Verilog-AMS Behavioral Model

Charge-pump PLL behavioral model with full noise verification.

## Specs

| Parameter | Value |
|-----------|-------|
| Reference | 50 MHz |
| Output | 10 GHz |
| Divider | N = 200 |
| Icp | 100 μA |
| Kvco | 50 MHz/V |
| LPF | 2nd-order (R₁=25kΩ, C₁=250pF, C₂=5pF) |
| PM | 71° |
| Lock time | ~25 μs |

## Quick Start

```bash
source env_setup.sh
cd sim

# Run PLL simulation
make run

# Noise verification
cd ../noise_tb
make noise_report      # analyze existing data
make noise             # full flow (sim + report)
```

## Project Structure

```
├── src/                    # Verilog-AMS source
│   ├── pfd.vams            #   Phase-frequency detector (with noise)
│   ├── cp.vams             #   Charge pump (with noise)
│   ├── lpf.vams            #   Loop filter (2nd-order RC)
│   ├── vco.vams            #   VCO (behavioral)
│   ├── vco_pn.vams         #   VCO with parameterized phase noise
│   ├── divider.vams        #   Divider (with noise)
│   └── pll_top.vams        #   Top-level
├── sim/                    # PLL simulation
│   ├── tb_pll.vams         #   Testbench
│   ├── Makefile            #   make run / make clean
│   └── probe.tcl           #   Waveform probing
├── noise_tb/               # Module noise verification
│   ├── Makefile            #   make noise / make noise_report
│   ├── tb_cp_noise.vams    #   CP noise testbench
│   ├── tb_pfd_noise.vams   #   PFD noise testbench
│   └── tb_div_noise.vams   #   Divider noise testbench
├── scripts/                # Analysis scripts
│   ├── noise_analyze.py    #   Pure Python FFT analysis
│   ├── gen_noise_plots.py  #   Matplotlib PSD plots
│   └── vco_pn_verify.py    #   VCO PN model verification
├── env_setup.sh            # Cadence environment
└── analog_control.scs      # Simulation control
```

## Locking Waveform

vctrl locks to 0.900V @ ~25 μs, PM = 71°, ripple < 1 mV:

```
t=0us   0.000 V
t=3us   0.906 V   ← first crossing
t=6us   1.042 V   ← peak overshoot (16%)
t=25us  0.904 V   ← settled
t=34us  0.900 V   ← locked
```

## Noise Verification

All modules verified with transient noise (noisefmax = 100 MHz):

| Module | Type | Meas RMS | Exp RMS | Bias |
|--------|------|----------|---------|------|
| CP | Current | 0.12 μA | 0.14 μA | −15% |
| PFD | Voltage | 0.26 mV | 0.32 mV | −17% |
| Divider | Voltage | 0.09 mV | 0.10 mV | −15% |

Bias is consistent across modules — caused by parasitic capacitance in test circuits reducing effective noise bandwidth from 100 MHz to ~85 MHz.

## VCO Phase Noise Model

3-point parameterized model:

```verilog
vco #(
  .pn_1k(-60),    // dBc/Hz @ 1 kHz
  .pn_10k(-80),   // dBc/Hz @ 10 kHz
  .pn_1M(-120)    // dBc/Hz @ 1 MHz (white floor)
) i_vco (...);
```

Formula: L(f) [dBc/Hz] → S_f(f) = L_lin × 2 × f² [Hz²/Hz] → internal noise modulation → output phase noise.

## Requirements

- Cadence Xcelium 23.09 + Spectre 23.1
- Python 3.6+ (for analysis scripts)
- numpy/scipy/matplotlib (for plot generation only)

## License

MIT
