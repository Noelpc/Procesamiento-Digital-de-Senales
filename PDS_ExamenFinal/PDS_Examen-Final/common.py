"""Utilidades comunes: estilo de gráficos (sin rojo, según el enunciado) y rutas."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler

ROOT = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(ROOT, "figs")
RES = os.path.join(ROOT, "results")
DATA = os.path.join(ROOT, "data")
os.makedirs(FIGS, exist_ok=True)
os.makedirs(RES, exist_ok=True)

# Paleta sin rojo (el rojo está reservado para la calificación)
COLORS = ["#1f4e9c", "#2a9d8f", "#e09f00", "#6a3d9a", "#2e7d32", "#555555"]
plt.rcParams.update({
    "axes.prop_cycle": cycler(color=COLORS),
    "figure.dpi": 130, "savefig.dpi": 160, "axes.grid": True,
    "grid.alpha": 0.3, "font.size": 9, "axes.titlesize": 10,
})

def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, name))
    plt.close()

def save_json(name, d):
    with open(os.path.join(RES, name), "w") as f:
        json.dump(d, f, indent=2, default=lambda o: o.tolist() if hasattr(o, 'tolist') else float(o))
