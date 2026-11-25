"""Proyecto 2 PDS - LPC tradicional vs LPC subbanda (esqueleto funcional).
Deps: numpy, scipy.   Uso: python lpc_subband.py referencia_16k.wav
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.linalg import solve_toeplitz
from scipy.signal import firwin, lfilter, resample_poly

# ---------- Bits asumidos por parámetro (ajustables, para factor de compresión) ----------
BITS = dict(coef=8, gain=5, pitch=7, voiced=1, sample=16)

# ============================ LPC ============================
def lpc_autocorr(x, p):
    """Yule-Walker (autocorrelación). Devuelve a (p), ganancia G^2 = error de predicción."""
    r = np.correlate(x, x, "full")[len(x) - 1:len(x) + p]
    if r[0] < 1e-9:
        return np.zeros(p), 0.0
    r[0] *= 1.0001  # regularización
    a = solve_toeplitz(r[:p], r[1:p + 1])
    err = r[0] - a @ r[1:p + 1]
    return a, max(err, 0) / len(x)          # x~[n] = sum a_k x[n-k] + G e[n]

def pitch_autocorr(x, fs, fmin=60, fmax=400):
    lo, hi = int(fs / fmax), min(int(fs / fmin), len(x) - 1)
    if hi <= lo + 1:
        return 0
    r = np.correlate(x, x, "full")[len(x) - 1:]
    return lo + int(np.argmax(r[lo:hi]))      # periodo en muestras

def lpc_encode(x, fs, p=10, win_ms=22.5, e_thr=None, zc_thr=0.25, preemph=0.68):
    """Devuelve lista de ventanas comprimidas y número de bits."""
    N = int(round(win_ms * 1e-3 * fs))
    x = lfilter([1, -preemph], [1], x)
    w = np.hamming(N)
    if e_thr is None:
        e_thr = 0.05 * np.mean(x ** 2) * N     # umbral relativo a energía media
    frames = []
    for i in range(0, len(x) - N + 1, N):     # ventanas sin traslape
        seg = x[i:i + N]
        E = np.sum(seg ** 2)
        ZC = 0.5 * np.sum(np.abs(np.diff(np.sign(seg)))) / N
        voiced = (E > e_thr) and (ZC < zc_thr)
        a, G2 = lpc_autocorr(seg * w, p)
        T = pitch_autocorr(seg, fs) if voiced else 0
        voiced = voiced and T > 0
        if voiced:   # potencia con número entero de periodos (como indica el enunciado)
            L = (N // T) * T
            P = np.mean(seg[:L] ** 2)
        else:
            P = np.mean(seg ** 2)
        # ganancia: escala el error de predicción a la potencia medida
        frames.append(dict(a=a, G=np.sqrt(G2), T=T, voiced=voiced, P=P))
    bits = len(frames) * (p * BITS['coef'] + BITS['gain'] + BITS['voiced']) \
        + sum(BITS['pitch'] for f in frames if f['voiced'])
    return frames, N, bits

def lpc_decode(frames, N, preemph=0.68, seed=0):
    rng = np.random.default_rng(seed)
    out, zi, phase = [], None, 0
    for f in frames:
        if f['voiced']:
            e = np.zeros(N)
            idx = np.arange(phase, N, f['T'])
            e[idx] = np.sqrt(f['T'])            # potencia unitaria
            phase = (idx[-1] + f['T']) - N if len(idx) else 0
        else:
            e = rng.standard_normal(N)
        a = np.concatenate(([1.0], -f['a']))
        if zi is None or len(zi) != len(a) - 1:
            zi = np.zeros(len(a) - 1)
        y, zi = lfilter([f['G']], a, e, zi=zi)  # H(z)=G/(1-sum a_k z^-k)
        out.append(y)
    y = np.concatenate(out)
    return lfilter([1], [1, -preemph], y)        # de-énfasis

# ============================ QMF ============================
def qmf_bank(ntaps=64, delta=0.12 * np.pi):
    """Banco CQF (reconstrucción casi perfecta, potencia complementaria).
    h0: pasa-bajos con transición coseno-elevado (|H0|^2+|H0(pi-w)|^2=cte).
    h1[n]=(-1)^n h0[N-1-n]; síntesis: g0=h0 invertido, g1=h1 invertido."""
    K = 4096
    w = np.linspace(0, np.pi, K // 2 + 1)
    mag = np.where(w < np.pi / 2 - delta, 1.0, 0.0)
    t = (w >= np.pi / 2 - delta) & (w <= np.pi / 2 + delta)
    mag[t] = np.cos(0.5 * np.pi * (w[t] - (np.pi / 2 - delta)) / (2 * delta))
    h = np.fft.irfft(mag, K)                                     # fase cero
    h = np.concatenate((h[-(ntaps // 2):], h[:ntaps // 2]))      # centrar
    h0 = h * np.kaiser(ntaps, 8.0)
    h0 /= np.sqrt(np.sum(h0 ** 2))
    h1 = h0[::-1] * (-1) ** np.arange(ntaps)
    return h0, h1, h0[::-1], h1[::-1]

def analysis2(x, h0, h1):
    return lfilter(h0, 1, x)[::2], lfilter(h1, 1, x)[::2]

def synthesis2(lo, hi, g0, g1):
    def up(v):
        u = np.zeros(2 * len(v)); u[::2] = v; return u
    return lfilter(g0, 1, up(lo)) + lfilter(g1, 1, up(hi))

def decompose(x, levels=3, ntaps=64):
    """Árbol de Fig. 5 (octavas): devuelve [b0(0-fs/16), b1(fs/16-fs/8)... ] de menor a mayor frecuencia."""
    h0, h1, _, _ = qmf_bank(ntaps)
    bands, cur = [], x
    for _ in range(levels):
        lo, hi = analysis2(cur, h0, h1)
        bands.append(hi); cur = lo
    bands.append(cur)
    return bands[::-1]                           # [LF, ..., HF]

def qmf_delay(levels=3, ntaps=64):
    return (2 ** levels - 1) * (ntaps - 1)

def compose(bands, ntaps=64):
    """Síntesis del árbol; retarda cada banda alta para alinear con la rama baja anidada."""
    _, _, g0, g1 = qmf_bank(ntaps)
    cur, D = bands[0], 0
    for hi in bands[1:]:
        hi = np.concatenate((np.zeros(D), hi))
        n = min(len(cur), len(hi))
        cur = synthesis2(cur[:n], hi[:n], g0, g1)
        D = 2 * D + (ntaps - 1)
    return cur                                   # retardo total = qmf_delay()

# ========================= LPC subbanda =========================
def subband_codec(x, fs, orders=(10, 6, 4, 2), win_ms=(90, 45, 22.5, 11.25), levels=3):
    """orders/win_ms por banda [LF..HF]. win_ms es la duración en tiempo real de la ventana."""
    bands = decompose(x, levels)
    # frecuencia de muestreo de cada banda
    fss = [fs / 2 ** levels, fs / 2 ** levels] + [fs / 2 ** k for k in range(levels - 1, 0, -1)]
    rec, bits = [], 0
    for b, fb, p, wm in zip(bands, fss, orders, win_ms):
        fr, N, nb = lpc_encode(b, fb, p, wm)
        bits += nb
        y = lpc_decode(fr, N)
        rec.append(y)
    y = compose(rec)[qmf_delay(levels):]   # compensa retardo; cada banda conserva su longitud
    return y, bits

# ============================ main ============================
if __name__ == "__main__":
    fs, x = wavfile.read(sys.argv[1])
    x = x.astype(float) / 32768
    orig_bits = len(x) * BITS['sample']

    fr, N, b = lpc_encode(x, fs)
    y = lpc_decode(fr, N)
    print(f"LPC-10 tradicional: CR = {orig_bits / b:.1f}:1")
    wavfile.write("out_lpc.wav", fs, (np.clip(y, -1, 1) * 32767).astype(np.int16))

    y2, b2 = subband_codec(x, fs)
    print(f"LPC subbanda:      CR = {orig_bits / b2:.1f}:1")
    wavfile.write("out_subband.wav", fs, (np.clip(y2, -1, 1) * 32767).astype(np.int16))

    # Sanity QMF: reconstrucción perfecta (salvo retardo/ganancia)
    xr = compose(decompose(x))
    d = qmf_delay(3)
    n = min(len(x) - d, len(xr) - d)
    print("QMF error relativo:", np.linalg.norm(x[:n] - xr[d:d + n]) / np.linalg.norm(x[:n]))
