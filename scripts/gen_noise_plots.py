#!/usr/bin/env python3
"""Generate PSD comparison plots for PLL module noise verification.
Requires: numpy, scipy, matplotlib
Usage: python3 gen_noise_plots.py
Output: noise_report.png (4-panel figure)
"""

import numpy as np
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# Data directory
DATA_DIR = '/home/user/workspace_hermes/proj1/noise_tb'
OUTPUT = 'noise_report.png'

fs = 1e9  # 1 GHz sampling
nperseg = 256

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# ============================================================
# Panel 1: CP Current Noise
# ============================================================
data = np.loadtxt(os.path.join(DATA_DIR, 'cp_noise_data.txt'))
v = signal.detrend(data[:, 1]) / 1000.0  # V -> A through 1k load
f, psd = signal.welch(v, fs=fs, nperseg=nperseg, scaling='density')
mask = (f >= 1e3) & (f <= 100e6)

ax = axes[0, 0]
ax.loglog(f[mask], psd[mask], 'b-', alpha=0.7, label='Simulated')
ax.axhline(2e-22, color='r', ls='--', lw=2, label='Expected: 2e-22 A$^2$/Hz')
ax.set_xlabel('Frequency [Hz]')
ax.set_ylabel('PSD [A$^2$/Hz]')
ax.set_title('CP Output Current Noise')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ============================================================
# Panel 2: PFD Voltage Noise
# ============================================================
data = np.loadtxt(os.path.join(DATA_DIR, 'pfd_noise_data.txt'))
v = signal.detrend(data[:, 1])
f, psd = signal.welch(v, fs=fs, nperseg=nperseg, scaling='density')
mask = (f >= 1e3) & (f <= 100e6)

ax = axes[0, 1]
ax.loglog(f[mask], psd[mask], 'b-', alpha=0.7, label='Simulated')
ax.axhline(1e-15, color='r', ls='--', lw=2, label='Expected: 1e-15 V$^2$/Hz')
ax.set_xlabel('Frequency [Hz]')
ax.set_ylabel('PSD [V$^2$/Hz]')
ax.set_title('PFD UP Output Voltage Noise')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ============================================================
# Panel 3: Divider Voltage Noise
# ============================================================
data = np.loadtxt(os.path.join(DATA_DIR, 'div_noise_data.txt'))
v = signal.detrend(data[:, 1])
f, psd = signal.welch(v, fs=fs, nperseg=nperseg, scaling='density')
mask = (f >= 1e3) & (f <= 100e6)

ax = axes[1, 0]
ax.loglog(f[mask], psd[mask], 'b-', alpha=0.7, label='Simulated')
ax.axhline(1e-16, color='r', ls='--', lw=2, label='Expected: 1e-16 V$^2$/Hz')
ax.set_xlabel('Frequency [Hz]')
ax.set_ylabel('PSD [V$^2$/Hz]')
ax.set_title('Divider Output Voltage Noise')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ============================================================
# Panel 4: VCO Phase Noise Model (analytical)
# ============================================================
pn_1k, pn_10k, pn_1M = -60, -80, -120  # dBc/Hz
f_vco = np.logspace(2, 7, 100)  # 100 Hz to 10 MHz
L = np.zeros_like(f_vco)

for i, fv in enumerate(f_vco):
    L1k = 10 ** (pn_1k / 10)
    L1M = 10 ** (pn_1M / 10)
    Sf_white = L1M * 2 * (1e6) ** 2
    Kf = max((L1k * 2 * (1e3) ** 2 - Sf_white) * 1e3, 0)
    Sf = Sf_white + Kf / fv
    L[i] = 10 * np.log10(Sf / (2 * fv ** 2))

ax = axes[1, 1]
ax.semilogx(f_vco, L, 'b-', lw=2, label='Model output')
ax.scatter([1e3, 1e4, 1e6], [pn_1k, pn_10k, pn_1M],
           c='r', s=80, zorder=5, label='Target points')
ax.set_xlabel('Offset Frequency [Hz]')
ax.set_ylabel('Phase Noise [dBc/Hz]')
ax.set_title('VCO Phase Noise Model (3-point parameterized)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_ylim(-130, -50)

# ============================================================
# Finish
# ============================================================
plt.suptitle('PLL Module Noise Verification Report', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT, dpi=150, bbox_inches='tight')
print(f'Saved {OUTPUT}')
