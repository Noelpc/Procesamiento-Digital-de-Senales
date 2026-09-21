import numpy as np
NOMBRES = ["Do","Do#","Re","Re#","Mi","Fa","Fa#","Sol","Sol#","La","La#","Si"]
def freq(n): return 440*2**(n/12)              # n: semitonos desde La4
def nota(n):
    k = n + 9                                   # semitonos desde Do4
    return f"{NOMBRES[k % 12]}{4 + k // 12}"
Fs = 8000
print(f"Fs = {Fs} Hz, plegado = {Fs/2:.0f} Hz")
n = int(np.floor(12*np.log2(Fs/2/440)))
print(f"Nota más alta: {nota(n)} = {freq(n):.2f} Hz")
n = 42                                          # Mib8 = Re#8
F = freq(n); Fa = F - Fs*round(F/Fs)
print(f"{nota(n)} = {F:.2f} Hz -> alias {Fa:.2f} Hz")
m = round(12*np.log2(abs(Fa)/440))
print(f"Nota más cercana: {nota(m)} = {freq(m):.2f} Hz")
