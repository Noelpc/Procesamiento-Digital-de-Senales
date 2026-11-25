"""Barrido de configuraciones LPC subbanda vs LPC-10. Uso: python sweep.py ref.wav
Métrica perceptual provisional: distancia log-espectral (LSD, dB) sobre STFT. Reemplazar/complementar con PEAQ."""
import sys, itertools, csv
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, freqz
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import lpc_subband as L

def lsd(x, y, fs):
    n = min(len(x), len(y)); x, y = x[:n], y[:n]
    _, _, X = stft(x, fs, nperseg=512); _, _, Y = stft(y, fs, nperseg=512)
    d = 20*np.log10(np.abs(X)+1e-6) - 20*np.log10(np.abs(Y)+1e-6)
    return float(np.mean(np.sqrt(np.mean(d**2, axis=0))))

fn = sys.argv[1]; tag = fn.split("/")[-1][:-4]
fs, x = wavfile.read(fn); x = x.astype(float)/32768
orig = len(x)*L.BITS['sample']
rows = []
fr, N, b = L.lpc_encode(x, fs); y = L.lpc_decode(fr, N)
rows.append(dict(sistema="LPC-10", levels=0, orders="10", wins="22.5", CR=orig/b, LSD=lsd(x, y, fs)))
orders_opts = {2: [(10,4,2),(10,6,2),(8,4,2),(10,6,4)],
               3: [(10,6,4,2),(10,4,2,2),(12,6,4,2),(8,4,2,2)],
               4: [(10,6,4,2,2),(10,4,2,2,2)]}
win_scales = [(1,1,1,1,1),(4,2,1,1,1),(8,4,2,1,1),(16,8,4,2,1),(8,4,2,2,2)]
for lv in (2, 3, 4):
    for od in orders_opts[lv]:
        assert len(od) == lv+1
        for ws in win_scales:
            wins = tuple(22.5*ws[i] for i in range(lv+1))
            try:
                y2, b2 = L.subband_codec(x, fs, orders=od, win_ms=wins, levels=lv)
            except Exception as e:
                print("skip", lv, od, ws, e); continue
            rows.append(dict(sistema="Subbanda", levels=lv, orders="-".join(map(str,od)),
                             wins="-".join(f"{w:g}" for w in wins), CR=orig/b2, LSD=lsd(x, y2, fs)))
rows.sort(key=lambda r: r["LSD"])
with open(f"sweep_{tag}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
base = rows[[r["sistema"] for r in rows].index("LPC-10")] if False else [r for r in rows if r["sistema"]=="LPC-10"][0]
better = [r for r in rows if r["sistema"]=="Subbanda" and r["LSD"] <= base["LSD"]*1.02 and r["CR"] > base["CR"]]
print("LPC-10:", base)
print("Mejores subbanda (LSD<=base+2%, CR>base):", sorted(better, key=lambda r:-r["CR"])[:5])
print("Top 5 por CR:", sorted([r for r in rows if r["sistema"]=="Subbanda"], key=lambda r:-r["CR"])[:5])
plt.figure(figsize=(4.5,3))
s = [r for r in rows if r["sistema"]=="Subbanda"]
plt.scatter([r["CR"] for r in s], [r["LSD"] for r in s], s=10, label="Subbanda")
plt.scatter([base["CR"]], [base["LSD"]], c="r", marker="*", s=80, label="LPC-10")
plt.xlabel("Factor de compresión"); plt.ylabel("LSD [dB]"); plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(f"cr_vs_lsd_{tag}.pdf"); plt.savefig(f"cr_vs_lsd_{tag}.png", dpi=200)
# Respuesta en frecuencia QMF
h0,h1,_,_ = L.qmf_bank(); w,H0 = freqz(h0,worN=2048); _,H1 = freqz(h1,worN=2048)
plt.figure(figsize=(4.5,3)); plt.plot(w/np.pi,20*np.log10(abs(H0)+1e-9),label="$H_0$"); plt.plot(w/np.pi,20*np.log10(abs(H1)+1e-9),label="$H_1$")
plt.ylim(-80,5); plt.xlabel("$\\omega/\\pi$"); plt.ylabel("|H| [dB]"); plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig("qmf_resp.pdf"); plt.savefig("qmf_resp.png", dpi=200)
