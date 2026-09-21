import numpy as np

A = 3.0
def sqnr(delta): return 10*np.log10(6*A**2/delta**2)   # (A²/2)/(Δ²/12)

def q_info(m, n):
    d = 2.0**-n
    return -2.0**(m-1), 2.0**(m-1) - d, d

formatos = {
    "a) 256 niveles uniformes": 6/255,
    "b) Q3.5": q_info(3, 5)[2],
    "d) suma Q4.4": q_info(4, 4)[2],
    "d) producto Q5.3": q_info(5, 3)[2],
}
print(f"{'Formato':28s}{'Δ (V)':>12s}{'SQNR (dB)':>12s}")
for k, d in formatos.items():
    print(f"{k:28s}{d:12.5f}{sqnr(d):12.2f}")
for m, n in ((3, 5), (4, 4), (5, 3)):
    lo, hi, d = q_info(m, n)
    print(f"Q{m}.{n}: rango [{lo}, {hi}], Δ={d}")
