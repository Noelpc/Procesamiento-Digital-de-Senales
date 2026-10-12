# Tarea 3: Señales y Sistemas en Tiempo Discreto 2

Procesamiento Digital de Señales · Maestría en Electrónica · TEC
Estudiante: **[nombre y carné]**

## Contenido

| Archivo | Descripción |
|---|---|
| `problema1.py` | Hacker de Sonar: chirp, correlación cruzada, distancia, resolución y duración mínima/máxima |
| `problema2.py` | Oído de Elefante: identificación de la canción oculta con la DFT |
| `problema3.py` | Pirata de Efectos: clonación de eco y reverberación por respuesta al impulso |
| `sonar_channel.py`, `efectos_fir.py`, `senal_misteriosa.wav` | Recursos proporcionados con el enunciado (sin modificar) |
| `figuras/` | Figuras generadas por los scripts |
| `reporte/` | Reporte en PDF |
| `requirements.txt` | Dependencias de Python |

## Requisitos

- Linux (Ubuntu, Kubuntu, Debian, Fedora, Omarchy, etc.)
- Python 3.10 o superior
- Dependencias: `numpy`, `scipy`, `matplotlib`

## Instalación

```bash
git clone <URL-del-repositorio> tarea3
cd tarea3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

Cada script se ejecuta desde la raíz del repositorio. No abren ventanas; guardan las figuras en `figuras/` y muestran los resultados por consola.

```bash
python3 problema1.py
python3 problema2.py
python3 problema3.py     # también guarda h_tot.npy (FIR equivalente a la cascada)
```

## Resultados principales

**Problema 1**: retardo τ = 200 ms (k = 19 200 muestras) y distancia **R = 150 m** con c = 1500 m/s (supuesto para agua salada). Resolución ΔR = 7,5 cm. Duración del chirp: **2,0 ms ≤ T ≤ 200 ms**.

**Problema 2**: la canción oculta es el **Himno a la Alegría** (Beethoven, Sinfonía n.º 9).

**Problema 3**: L_eco = 44 101 y L_rev = 70 561 muestras (fs = 44,1 kHz). El error máximo contra los efectos originales es del orden de 1e-15. El FIR único de la cascada tiene 114 661 muestras.

## Notas

- La velocidad del sonido c = 1500 m/s es un supuesto, ya que el enunciado no la especifica.
- Las respuestas al impulso del problema 3 dependen de `fs`; si se usa otra frecuencia de muestreo, hay que repetir la identificación.
- `sonar_channel.py` se usa únicamente como caja negra (se llama a la función; no se inspecciona su implementación).

## Entrega

- Repositorio con acceso para el usuario `michaelgruner`.
- Réplica ZIP/TAR del repositorio en TEC Digital (solo respaldo).
