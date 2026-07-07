#!/usr/bin/env python3
"""PLL Module Noise Verification Suite
======================================
Analyzes transient noise simulation data for CP, PFD, Divider modules.
Computes RMS noise, PSD via FFT, and compares with expected white noise PSD.

Usage: python3 noise_analyze.py <data_file> <module_name> [--white-psd VALUE] [--scale FACTOR]

Data file format: two columns (time, value) as written by $fstrobe
"""

import math
import cmath
import sys


def fft(x):
    """Cooley-Tukey radix-2 FFT (pure Python, no numpy needed)"""
    n = len(x)
    if n <= 1:
        return [complex(x[0], 0)]
    even = fft(x[0::2])
    odd = fft(x[1::2])
    result = [0] * n
    for k in range(n // 2):
        t = cmath.exp(-2j * math.pi * k / n) * odd[k]
        result[k] = even[k] + t
        result[k + n // 2] = even[k] - t
    return result


def welch_psd(signal_data, fs, nperseg=256, window='hann'):
    """Compute PSD using Welch's method (pure Python).
    
    Args:
        signal_data: list of float, the detrended signal
        fs: sampling frequency in Hz
        nperseg: segment length (must be power of 2 for FFT)
        window: 'hann' (default)
    
    Returns:
        (freqs, psd): frequency array and PSD array (one-sided)
    """
    n = len(signal_data)
    if n < nperseg:
        nperseg = n
    
    # Hann window
    win = [0.5 * (1 - math.cos(2 * math.pi * i / (nperseg - 1))) for i in range(nperseg)]
    
    # Single segment (for short data)
    x_pad = list(signal_data[:nperseg]) + [0.0] * (nperseg - len(signal_data[:nperseg]))
    x_win = [x_pad[i] * win[i] for i in range(nperseg)]
    
    # FFT
    X = fft(x_win)
    
    # Normalization
    win_sum_sq = sum(w * w for w in win)
    psd_raw = [abs(x) ** 2 / (fs * win_sum_sq) for x in X]
    
    # One-sided, positive frequencies only
    freqs = [i * fs / nperseg for i in range(nperseg // 2)]
    psd = psd_raw[:nperseg // 2]
    
    return freqs, psd


def load_data(filename, scale=1.0):
    """Load two-column data file, apply optional scaling factor."""
    with open(filename) as f:
        values = []
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                values.append(float(parts[1]) * scale)
    return values


def analyze(filename, module_name, white_psd, scale=1.0, unit='V'):
    """Run full noise analysis on a module's data file.
    
    Args:
        filename: path to $fstrobe output file
        module_name: label for reporting
        white_psd: expected white noise PSD in unit^2/Hz
        scale: multiply data by this factor (e.g. 1/1000 for V->A)
        unit: measurement unit string
    
    Returns:
        dict with all analysis results
    """
    data = load_data(filename, scale)
    n = len(data)
    fs = 1.0e9  # 1 GHz sampling
    
    # DC and AC statistics
    mean_val = sum(data) / n
    ac = [x - mean_val for x in data]
    rms = math.sqrt(sum(x * x for x in ac) / n)
    
    # PSD
    freqs, psd = welch_psd(ac, fs)
    
    # Spot checks
    spot_freqs = [1e4, 1e5, 1e6, 5e6, 1e7]
    spots = {}
    for sf in spot_freqs:
        idx = min(range(len(freqs)), key=lambda i: abs(freqs[i] - sf))
        spots[sf] = {'freq': freqs[idx], 'psd': psd[idx]}
    
    # Integrated noise (1kHz - 100MHz)
    mask = [i for i, f in enumerate(freqs) if 1e3 <= f <= 1e8]
    if mask:
        df = fs / len(freqs*2)  # approximate frequency bin width
        int_noise = math.sqrt(sum(psd[i] * df for i in mask))
    else:
        int_noise = 0.0
    
    # Expected values
    bw = 100e6  # noisefmax
    exp_rms = math.sqrt(white_psd * bw)
    exp_rt = math.sqrt(white_psd)
    
    return {
        'name': module_name,
        'unit': unit,
        'n_samples': n,
        'dc': mean_val,
        'rms': rms,
        'exp_rms': exp_rms,
        'exp_rt': exp_rt,
        'white_psd': white_psd,
        'spots': spots,
        'int_noise': int_noise,
    }


def print_report(results):
    """Print formatted analysis report."""
    r = results
    print(f"=== {r['name']} Noise Analysis ===")
    print(f"  Samples: {r['n_samples']}, DC: {r['dc']:.4f} {r['unit']}")
    print(f"  RMS: {r['rms']:.4e} {r['unit']}  |  Expected: {r['exp_rms']:.4e} {r['unit']}")
    print(f"  White noise density: {r['exp_rt']:.1e} {r['unit']}/rtHz")
    print(f"  Ratio (meas/exp): {r['rms']/r['exp_rms']*100:.0f}%")
    print(f"  Integrated noise (1k-100M): {r['int_noise']:.4e} {r['unit']} RMS")
    print(f"  Spot PSD checks:")
    for sf in sorted(r['spots'].keys()):
        s = r['spots'][sf]
        print(f"    @ {sf/1e3:6.0f} kHz: PSD={s['psd']:.3e} {r['unit']}^2/Hz  "
              f"({math.sqrt(s['psd'])*1e12:.1f} p{r['unit']}/rtHz)")
    print()


# ============================================================
# Main: run on all modules
# ============================================================
if __name__ == '__main__':
    # Module configurations
    modules = [
        {
            'file': '/home/user/workspace_hermes/proj1/noise_tb/cp_noise_data.txt',
            'name': 'CP Charge Pump',
            'white_psd': 2e-22,   # A^2/Hz
            'scale': 1.0 / 1000.0,  # V -> A (1k load)
            'unit': 'A',
        },
        {
            'file': '/home/user/workspace_hermes/proj1/noise_tb/pfd_noise_data.txt',
            'name': 'PFD (UP output)',
            'white_psd': 1e-15,   # V^2/Hz
            'scale': 1.0,
            'unit': 'V',
        },
        {
            'file': '/home/user/workspace_hermes/proj1/noise_tb/div_noise_data.txt',
            'name': 'Divider (clk_out)',
            'white_psd': 1e-16,   # V^2/Hz
            'scale': 1.0,
            'unit': 'V',
        },
    ]
    
    print("=" * 60)
    print("  PLL Module Noise Verification")
    print("  Transient noise: noisefmax=100MHz, 1GHz sampling")
    print("=" * 60)
    print()
    
    summary = []
    for m in modules:
        try:
            r = analyze(m['file'], m['name'], m['white_psd'], m['scale'], m['unit'])
            print_report(r)
            summary.append((r['name'], r['rms'], r['exp_rms']))
        except FileNotFoundError:
            print(f"  [SKIP] {m['name']}: data file not found")
            print()
    
    # Summary table
    print("=" * 60)
    print(f"  {'Module':<25s} {'Meas RMS':>12s} {'Exp RMS':>12s} {'Ratio':>8s}")
    print("  " + "-" * 58)
    for name, rms, exp in summary:
        print(f"  {name:<25s} {rms:>10.2e}  {exp:>10.2e}  {rms/exp*100:>6.0f}%")
    print("=" * 60)
