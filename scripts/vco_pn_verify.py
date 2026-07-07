#!/usr/bin/env python3
"""VCO Phase Noise Model Verification
======================================
Verifies that the 3-point parameterized VCO phase noise model
produces the correct L(f) values at specified frequencies.

Model formula:
  L(f) [dBc/Hz] -> L_lin = 10^(dB/10)
  S_f(f) = L_lin * 2 * f^2           [Hz^2/Hz, frequency noise PSD]
  S_f_white = S_f(f_M)               [white noise floor]
  K_f = (S_f(f_L) - S_f_white) * f_L [flicker coefficient: S_f,fl = K_f/f]
  
  V(nz) <+ white_noise(S_f_white)     -> produces 1/f^2 phase noise
  V(nz) <+ flicker_noise(K_f, 1.0)    -> produces 1/f^3 phase noise
  freq = f0 + Kvco*(Vctrl-Vctrl0) + V(nz)  [1V = 1Hz frequency deviation]

Usage: python3 vco_pn_verify.py [pn_1k] [pn_10k] [pn_1M]
       python3 vco_pn_verify.py -60 -80 -120
"""

import math
import sys


def verify_vco_pn(pn_1k_db, pn_10k_db, pn_1M_db):
    """Compute and verify VCO phase noise model.
    
    Args:
        pn_1k_db:  target L(f) at 1 kHz  [dBc/Hz]
        pn_10k_db: target L(f) at 10 kHz [dBc/Hz]
        pn_1M_db:  target L(f) at 1 MHz  [dBc/Hz] (white floor)
    
    Returns:
        dict with model parameters and verification results
    """
    # Convert dBc/Hz to linear
    L_1k = 10 ** (pn_1k_db / 10)
    L_10k = 10 ** (pn_10k_db / 10)
    L_1M = 10 ** (pn_1M_db / 10)
    
    # Step 1: Frequency noise PSD at each anchor point
    # S_f(f) = L(f) * 2 * f^2
    S_f_1k = L_1k * 2 * (1e3) ** 2
    S_f_10k = L_10k * 2 * (10e3) ** 2
    S_f_white = L_1M * 2 * (1e6) ** 2
    
    # Step 2: Separate white and flicker components
    # White: constant S_f
    # Flicker: S_f(f) = K_f / f
    K_f = max((S_f_1k - S_f_white) * 1e3, 0.0)
    
    # Step 3: Verify at multiple frequencies
    test_freqs = [1e2, 1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7]
    results = []
    for f_test in test_freqs:
        S_f_total = S_f_white + K_f / f_test
        L_calc = S_f_total / (2 * f_test ** 2)
        L_calc_db = 10 * math.log10(L_calc)
        results.append((f_test, L_calc_db))
    
    # Step 4: Period jitter from white noise
    f0 = 10e9  # 10 GHz
    sigma_T = math.sqrt(S_f_white / (2 * f0 ** 3))  # period jitter RMS [s]
    
    return {
        'pn_1k_db': pn_1k_db, 'pn_10k_db': pn_10k_db, 'pn_1M_db': pn_1M_db,
        'L_1k': L_1k, 'L_10k': L_10k, 'L_1M': L_1M,
        'S_f_1k': S_f_1k, 'S_f_10k': S_f_10k, 'S_f_white': S_f_white,
        'K_f': K_f,
        'sigma_T': sigma_T,
        'results': results,
    }


def print_report(r):
    """Print formatted verification report."""
    print("=" * 70)
    print("  VCO Phase Noise Model Verification")
    print("=" * 70)
    print(f"\n  Target points:")
    print(f"    L(1kHz)  = {r['pn_1k_db']:>4d} dBc/Hz")
    print(f"    L(10kHz) = {r['pn_10k_db']:>4d} dBc/Hz")
    print(f"    L(1MHz)  = {r['pn_1M_db']:>4d} dBc/Hz")
    
    print(f"\n  Derived parameters:")
    print(f"    S_f_white  = {r['S_f_white']:.1f} Hz^2/Hz  (white freq noise)")
    print(f"    K_f        = {r['K_f']:.1f}            (flicker: S_f,fl = K_f/f)")
    print(f"    sigma_T    = {r['sigma_T']*1e15:.1f} fs/cycle  (period jitter @ 10GHz)")
    
    print(f"\n  {'Offset':>10s}  {'L(f) calc':>10s}  {'Note':>20s}")
    print(f"  {'-'*45}")
    for f_test, L_db in r['results']:
        note = ""
        if abs(f_test - 1e3) < 1: note = f"(target: {r['pn_1k_db']} dBc)"
        if abs(f_test - 1e4) < 1: note = f"(target: {r['pn_10k_db']} dBc)"
        if abs(f_test - 1e6) < 1: note = f"(target: {r['pn_1M_db']} dBc)"
        marker = " ✓" if any(abs(f_test - f) < 1 for f in [1e3, 1e4, 1e6]) and \
                 abs(L_db - [r['pn_1k_db'], r['pn_10k_db'], r['pn_1M_db']][
                     [1e3, 1e4, 1e6].index(f_test)]) < 0.1 else ""
        print(f"  {f_test/1e3:>8.1f}kHz  {L_db:>8.1f} dBc  {note}{marker}")
    
    print(f"\n  VCO model formula in Verilog-AMS:")
    print(f"    V(nz) <+ white_noise({r['S_f_white']:.1f}, \"vco_freq_white\");")
    if r['K_f'] > 0:
        print(f"    V(nz) <+ flicker_noise({r['K_f']:.1f}, 1.0, \"vco_freq_fl\");")
    print(f"    freq = f0 + kvco*(Vctrl-Vctrl0) + V(nz);")
    print()


if __name__ == '__main__':
    # Parse command line or use defaults
    if len(sys.argv) >= 4:
        pn_1k = float(sys.argv[1])
        pn_10k = float(sys.argv[2])
        pn_1M = float(sys.argv[3])
    else:
        pn_1k, pn_10k, pn_1M = -60, -80, -120
    
    r = verify_vco_pn(pn_1k, pn_10k, pn_1M)
    print_report(r)
    
    # Also show a few alternate configurations
    print("\n  === Alternative configurations ===")
    for (a, b, c) in [(-50, -70, -110), (-70, -90, -120)]:
        r2 = verify_vco_pn(a, b, c)
        print(f"  pn_1k={a}, pn_10k={b}, pn_1M={c}: K_f={r2['K_f']:.0f}, sigma_T={r2['sigma_T']*1e15:.1f} fs")
