# Tarea 2 - Señales y Sistemas en Tiempo Discreto (PDS, TEC)

## Contenido
| Archivo | Descripción |
|---|---|
| `reporte.pdf` / `reporte.tex` | Reporte (fuente LaTeX incluida) |
| `wav_io.py` | Punto 1: lectura, inspección y escritura de WAV |
| `convolucion.py` | Punto 2: convolución de `señal.wav` con `respuesta_al_impulso.npy` |
| `eco.py` | Punto 3: eco mediante convolución |
| `requirements.txt` | Dependencias de Python |

## Instalación (Ubuntu/Debian/Fedora/Omarchy, Python 3.9+)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
`soundfile` incluye `libsndfile` en sus ruedas (wheels) de pip. Si su sistema no lo instala, use
`sudo apt install libsndfile1` (Debian/Ubuntu) o `sudo dnf install libsndfile` (Fedora).

## Construcción del reporte (opcional)
```bash
pdflatex reporte.tex && pdflatex reporte.tex
```

## Ejecución
Colocar `señal.wav` y `respuesta_al_impulso.npy` en esta carpeta.

```bash
# Punto 1: inspecciona e imprime formato; reescribe con otro ancho de muestra
python3 wav_io.py señal.wav señal_reescrita.wav

# Punto 2: genera señal_convolucionada.wav
python3 convolucion.py señal.wav respuesta_al_impulso.npy señal_convolucionada.wav

# Punto 3: amplitud relativa (0..1) y retraso (s); produce archivo_out.wav
python3 eco.py archivo.wav 0.5 0.25
```
