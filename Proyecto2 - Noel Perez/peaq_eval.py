"""Evalúa ODG (PEAQ, peaqb-fast) de LPC-10 y configuraciones subbanda.
Uso: python peaq_eval.py ref.wav /ruta/a/peaqb      (peaqb: ./configure && make en peaqb-fast; binario src/peaqb)
peaqb exige 48 kHz, 16 bit, estéreo: se remuestrea y se duplica el canal."""
import sys, re, subprocess, tempfile, os, csv
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
import lpc_subband as L
from scipy.signal import stft

def lsd(x, y, fs):
    n = min(len(x), len(y)); x, y = x[:n], y[:n]
    _, _, X = stft(x, fs, nperseg=512); _, _, Y = stft(y, fs, nperseg=512)
    d = 20*np.log10(np.abs(X)+1e-6) - 20*np.log10(np.abs(Y)+1e-6)
    return float(np.mean(np.sqrt(np.mean(d**2, axis=0))))

def to48(x, fs, path):
    g = np.gcd(48000, fs)
    y = resample_poly(x, 48000 // g, fs // g)
    wavfile.write(path, 48000, (np.clip(np.stack([y, y], 1), -1, 1) * 32767).astype(np.int16))

def odg(x, y, fs, peaqb):
    n = min(len(x), len(y))
    with tempfile.TemporaryDirectory() as d:
        r, t = os.path.join(d, "r.wav"), os.path.join(d, "t.wav")
        to48(x[:n], fs, r); to48(y[:n], fs, t)
        out = subprocess.run([peaqb, "-r", r, "-t", t], capture_output=True, text=True).stdout
    return float(re.findall(r"ODG:\s*(-?[\d.]+)", out)[-1])

if __name__ == "__main__":
    fs, x = wavfile.read(sys.argv[1]); x = x.astype(float) / 32768; peaqb = sys.argv[2]
    o = len(x) * L.BITS['sample']
    rows = []
    def add(sis, cfg, cr, y):
        od = odg(x, y, fs, peaqb)
        rows.append(dict(sistema=sis, config=cfg, CR=round(cr, 1), LSD=round(lsd(x, y, fs), 2), ODG=round(od, 2))); print(rows[-1])
    for w in (22.5, 45, 90):
        fr, N, b = L.lpc_encode(x, fs, 10, w)
        add("LPC-10", f"p=10 w={w}", o / b, L.lpc_decode(fr, N))
    cfgs = [(3, (12,6,4,2), (22.5,)*4), (3, (10,6,4,2), (22.5,)*4), (3, (10,6,4,2), (90,45,22.5,22.5)),
            (3, (10,4,2,2), (90,45,22.5,22.5)), (2, (8,4,2), (360,180,90))]
    for lv, od, wn in cfgs:
        y, b = L.subband_codec(x, fs, orders=od, win_ms=wn, levels=lv)
        add(f"Subbanda L={lv}", f"p={'-'.join(map(str, od))} w={'-'.join(f'{w:g}' for w in wn)}", o / b, y)
    tag = os.path.basename(sys.argv[1])[:-4]
    with open(f"peaq_{tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
