#!/usr/bin/env python3
"""Pregunta 4 - Filtro IIR pasa altos: prototipo analógico (Chebyshev I) -> HP -> bilineal.

Las transformaciones se implementan paso a paso (analíticamente) y se verifican con scipy.signal.
"""
import numpy as np
import scipy.signal as sg
import matplotlib.pyplot as plt
from common import savefig, save_json

Fs, fp, fs_, Rp, As = 8000.0, 2000.0, 1200.0, 0.5, 40.0

# ---------------------------------------------------------------- 4.A/4.B orden: comparación de aproximaciones
Wp = 2 * Fs * np.tan(np.pi * fp / Fs)          # pre-distorsión de frecuencias (bilineal, T = 1/Fs)
Ws = 2 * Fs * np.tan(np.pi * fs_ / Fs)
wsn = Wp / Ws                                  # prototipo pasa bajos normalizado (wp = 1)
ordenes = {
    "Butterworth": sg.buttord(Wp, Ws, Rp, As, analog=True)[0],
    "Chebyshev I": sg.cheb1ord(Wp, Ws, Rp, As, analog=True)[0],
    "Chebyshev II": sg.cheb2ord(Wp, Ws, Rp, As, analog=True)[0],
    "Elíptico": sg.ellipord(Wp, Ws, Rp, As, analog=True)[0],
}
eps = np.sqrt(10 ** (Rp / 10) - 1)
n_cheb_formula = np.arccosh(np.sqrt((10 ** (As / 10) - 1) / eps ** 2)) / np.arccosh(wsn)
n_butt_formula = np.log10((10 ** (As / 10) - 1) / eps ** 2) / (2 * np.log10(wsn))
n = int(np.ceil(n_cheb_formula))
print(f"Wp={Wp:.2f} rad/s  Ws={Ws:.2f} rad/s  Ws_norm={wsn:.4f}  eps={eps:.4f}")
print("órdenes scipy:", ordenes, f" fórmula cheb={n_cheb_formula:.3f} butter={n_butt_formula:.3f}")

# ---------------------------------------------------------------- 4.C prototipo pasa bajos normalizado Chebyshev I
a = np.arcsinh(1 / eps) / n
th = (2 * np.arange(1, n + 1) - 1) * np.pi / (2 * n)
p_lp = -np.sinh(a) * np.sin(th) + 1j * np.cosh(a) * np.cos(th)      # polos de H_LP(s), wp = 1
K = np.real(np.prod(-p_lp))                                         # n impar -> H_LP(0) = 1
print("polos LP normalizado:", np.round(p_lp, 5), " K =", K)

# ---------------------------------------------------------------- 4.D LP -> HP:  s -> Wp/s
q_hp = Wp / p_lp                                                    # polos HP analógico
z_hp = np.zeros(n)                                                  # n ceros en s = 0
b_hp = np.real(np.poly(z_hp)); a_hp = np.real(np.poly(q_hp))        # H_HP(s) = s^n / prod(s - q_k)
print("polos HP analógico:", np.round(q_hp, 2))

# ---------------------------------------------------------------- 4.E respuesta del HP analógico
W = np.linspace(1, 40000, 8000)
_, Hs = sg.freqs(b_hp, a_hp, worN=W)
Hs_db = 20 * np.log10(np.abs(Hs))
Hp_an = 20 * np.log10(np.abs(sg.freqs(b_hp, a_hp, worN=[Wp])[1][0]))
Hs_an = 20 * np.log10(np.abs(sg.freqs(b_hp, a_hp, worN=[Ws])[1][0]))
plt.figure(figsize=(8, 3.8))
plt.plot(W, Hs_db, color="#1f4e9c")
plt.axvline(Ws, ls="--", color="#555555"); plt.axvline(Wp, ls="--", color="#555555")
plt.axhline(-As, ls=":", color="#2e7d32"); plt.axhline(-Rp, ls=":", color="#2e7d32")
plt.plot([Ws, Wp], [Hs_an, Hp_an], "o", color="#e09f00")
plt.text(Ws, -75, f"Ω_s={Ws:.0f}\n{Hs_an:.1f} dB", fontsize=7, ha="right")
plt.text(Wp, -25, f"Ω_p={Wp:.0f}\n{Hp_an:.2f} dB", fontsize=7, ha="left")
plt.ylim(-90, 5); plt.xlabel("Ω [rad/s]"); plt.ylabel("|H_HP(jΩ)| [dB]")
plt.title("Filtro analógico pasa altos Chebyshev I (n=5)")
savefig("p4_analogico.png")

# ---------------------------------------------------------------- 4.F bilineal  s = 2Fs (z-1)/(z+1)
c = 2 * Fs
p_z = (c + q_hp) / (c - q_hp)                                       # polos digitales
G = np.real(c ** n / np.prod(c - q_hp))                             # ganancia
b = G * np.real(np.poly(np.ones(n)))                                # n ceros en z = 1
a_d = np.real(np.poly(p_z))
b_ref, a_ref = sg.cheby1(n, Rp, fp, btype="high", fs=Fs)            # verificación con scipy
print("b =", b, "\na =", a_d)
print("max|b-b_scipy| =", np.max(np.abs(b - b_ref)), " max|a-a_scipy| =", np.max(np.abs(a_d - a_ref)))

# ---------------------------------------------------------------- 4.G respuesta digital
w, Hd = sg.freqz(b, a_d, worN=8192, fs=Fs)
mag = 20 * np.log10(np.abs(Hd) + 1e-15)
fig, ax = plt.subplots(2, 1, figsize=(8, 5.6), sharex=True)
ax[0].plot(w, mag, color="#1f4e9c")
ax[0].axvline(fs_, ls="--", color="#555555"); ax[0].axvline(fp, ls="--", color="#555555")
ax[0].axhline(-As, ls=":", color="#2e7d32"); ax[0].axhline(-Rp, ls=":", color="#2e7d32")
ax[0].set_ylim(-100, 5); ax[0].set_ylabel("|H(e^{jω})| [dB]")
ax[0].set_title("Filtro digital pasa altos (bilineal, Fs = 8 kHz)")
ax[1].plot(w, np.unwrap(np.angle(Hd)), color="#6a3d9a"); ax[1].set_ylabel("Fase [rad]"); ax[1].set_xlabel("Frecuencia [Hz]")
savefig("p4_digital_respuesta.png")

fig, ax = plt.subplots(figsize=(4.6, 4.6))
ax.add_patch(plt.Circle((0, 0), 1, fill=False, color="#555555"))
ax.plot(p_z.real, p_z.imag, "x", color="#1f4e9c", ms=9, label="polos")
ax.plot(np.ones(n), np.zeros(n), "o", mfc="none", color="#2e7d32", ms=9, label=f"ceros (x{n})")
ax.axhline(0, color="#999999", lw=0.5); ax.axvline(0, color="#999999", lw=0.5)
ax.set_aspect("equal"); ax.set_xlim(-1.3, 1.5); ax.set_ylim(-1.3, 1.3); ax.legend(fontsize=7, loc="lower left")
ax.set_title("Diagrama de polos y ceros"); ax.set_xlabel("Re"); ax.set_ylabel("Im")
savefig("p4_polos_ceros.png")

f_chk = lambda f0: 20 * np.log10(np.abs(sg.freqz(b, a_d, worN=[f0], fs=Fs)[1][0]))
g_fp, g_fs = f_chk(fp), f_chk(fs_)
pb = (w >= fp)
rizado = float(-mag[pb].min()); max_rej = float(mag[w <= fs_].max())
print(f"|H(2000)|={g_fp:.3f} dB  |H(1200)|={g_fs:.2f} dB  rizado paso={rizado:.3f} dB  máx banda eliminada={max_rej:.2f} dB")

# ---------------------------------------------------------------- 4.H transitorio con salida de 16 bits
delta = np.zeros(40000); delta[0] = 1
hn = sg.lfilter(b, a_d, delta)
umbral = 2.0 ** -15                                               # 1 LSB de un dato de 16 bits normalizado
idx = np.flatnonzero(np.abs(hn) >= umbral)
n_trans = int(idx[-1] + 1)
r_max = float(np.max(np.abs(p_z)))
n_est = float(np.log(umbral) / np.log(r_max))
print(f"r_max={r_max:.5f}  n_trans={n_trans} muestras = {n_trans/Fs*1e3:.2f} ms ; estimación ln(2^-15)/ln(r)={n_est:.1f}")
plt.figure(figsize=(8, 3.4))
plt.semilogy(np.arange(600), np.abs(hn[:600]) + 1e-20, color="#1f4e9c", lw=0.8, label="|h(n)|")
plt.axhline(umbral, color="#2e7d32", ls="--", label="1 LSB (2⁻¹⁵)")
plt.axvline(n_trans, color="#e09f00", ls=":", label=f"n = {n_trans}")
plt.ylim(1e-8, 2); plt.xlabel("n"); plt.legend(fontsize=7); plt.title("Respuesta al impulso y fin del transitorio")
savefig("p4_transitorio.png")

save_json("p4.json", dict(Fs=Fs, Wp=Wp, Ws=Ws, wsn=wsn, eps=eps, ordenes=ordenes, n_cheb_formula=n_cheb_formula,
         n_butt_formula=n_butt_formula, n=n, a_lp=a, p_lp=[[z.real, z.imag] for z in p_lp], K=K,
         q_hp=[[z.real, z.imag] for z in q_hp], p_z=[[z.real, z.imag] for z in p_z], G=G, b=b, a=a_d,
         err_b=float(np.max(np.abs(b - b_ref))), err_a=float(np.max(np.abs(a_d - a_ref))),
         g_fp=g_fp, g_fs=g_fs, rizado=rizado, max_rej=max_rej, Hp_an=Hp_an, Hs_an=Hs_an,
         r_max=r_max, n_trans=n_trans, t_trans_ms=n_trans / Fs * 1e3, n_est=n_est))

# polinomios expandidos del prototipo y del HP analógico (los usa el informe)
save_json("p4_extra.json", dict(den_lp=np.real(np.poly(p_lp)), den_hp=np.real(np.poly(q_hp)), a_lp=a))
