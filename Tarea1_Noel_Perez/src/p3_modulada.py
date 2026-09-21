import numpy as np
import matplotlib.pyplot as plt

Fs, f0, fc = 1000, 100, 1000
x = lambda t: (1 + 0.5*np.cos(2*np.pi*f0*t))*np.cos(2*np.pi*fc*t)
m = lambda t: np.cos(2*np.pi*f0*t)

t = np.linspace(0, 3/f0, 6000)
n = np.arange(0, int(3*Fs/f0) + 1)
tn = n/Fs
xn = x(tn)
m_rec = 2*(xn - 1)                    # m[n] = 2(x[n]-1)
m_dir = m(tn)
print("Máx |m_rec - m_dir| =", np.max(np.abs(m_rec - m_dir)))
print(np.c_[tn*1e3, m_rec, m_dir])

# e) fase desconocida
for phi in (np.pi/3, np.pi/2):
    xp = (1 + 0.5*np.cos(2*np.pi*f0*tn))*np.cos(2*np.pi*fc*tn + phi)
    print(f"phi={phi:.4f}: cos(phi)={np.cos(phi):.3g}, "
          f"máx|x_phi - cos(phi)(1+m/2)| = {np.max(np.abs(xp - np.cos(phi)*(1+m_dir/2))):.2e}")

fig, (a1, a2) = plt.subplots(2, 1, sharex=True, figsize=(9, 6))
a1.plot(t*1e3, x(t), lw=.8, label="x(t)")
a1.plot(tn*1e3, xn, 'ro', label="x[n]")
a1.set_ylabel("Amplitud"); a1.legend()
a2.plot(t*1e3, m(t), label="m(t)")
a2.plot(tn*1e3, m_rec, 'ro', label="m[n] recuperada")
a2.set(xlabel="t (ms)", ylabel="Amplitud"); a2.legend()
plt.show()
