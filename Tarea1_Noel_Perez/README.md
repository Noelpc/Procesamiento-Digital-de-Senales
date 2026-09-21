# Tarea 1 – Señales, Sistemas y Procesamiento Digital de Señales

Maestría en Electrónica, TEC. Entrega individual.

## Estructura
```
reporte/reporte.pdf      Reporte final
src/p1_notas.py          Problema 1: notas, alias, frecuencia escuchada
src/p2_alias.py          Problema 2: señal, alias y muestras
src/p3_modulada.py       Problema 3: recuperación de m[n] por aliasing
src/p4_punto_fijo.py     Problema 4: formatos Qm.n y SQNR
requirements.txt
```

## Instalación (Ubuntu/Debian/Fedora/Arch)
```bash
sudo apt install python3 python3-venv     # Fedora: sudo dnf install python3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución
```bash
python src/p1_notas.py
python src/p2_alias.py 0.714286 1 7      # F(Hz) Fs(Hz) ciclos
python src/p2_alias.py 5000 8000 5
python src/p3_modulada.py                # grafica y error numérico
python src/p4_punto_fijo.py
```
Para guardar figuras sin ventana: `MPLBACKEND=Agg python src/p2_alias.py ...` (usar `--out fig.png`).

## Dependencias
Python >= 3.9, numpy, matplotlib.
