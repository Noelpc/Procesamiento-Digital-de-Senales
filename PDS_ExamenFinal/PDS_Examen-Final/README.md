# Examen de Procesamiento Digital de Señales (TEC, Maestría en Electrónica)

Solución individual del examen (entrega 26 de noviembre de 2026).

## Contenido

| Archivo | Pregunta |
|---|---|
| `p1_modulacion_am.py` | 1. Modulación por amplitud: 5 canales, FIR Kaiser, demodulación, latencia |
| `p2_filtrado_frecuencia.py` | 2. Convolución vs. filtrado en frecuencia (zero-padding a potencia de 2) |
| `p3_compresion_audio.py` | 3. Compresor/descompresor DCT + cuantización + RLE; CR y SNR vs. FC |
| `p4_iir_pasa_altos.py` | 4. IIR paso altos (Chebyshev I): LP → HP → bilineal, verificación y transitorio |
| `p5_periodograma.py` | 5. Periodograma vs. Welch (`crowd.wav`) |
| `common.py` | Estilo de gráficos (sin rojo) y rutas |
| `data/` | `smash.wav`, `crowd.wav`, `pregunta1.py`, `pregunta2.py` (archivos del enunciado) |
| `figs/` | Figuras generadas |
| `results/` | Resultados numéricos (JSON) que usa el informe |
| `audio_reconstruido/` | `smash.wav` reconstruido con FC = 0.15, 0.30 y 0.50 |
| `informe/` | Informe en Word y PDF, y el script que lo genera |

## Ejecución

```bash
pip install -r requirements.txt
python3 p1_modulacion_am.py
python3 p2_filtrado_frecuencia.py
python3 p3_compresion_audio.py     # tarda un par de minutos (barrido de FC, dos modos)
python3 p4_iir_pasa_altos.py
python3 p5_periodograma.py
```

Cada script imprime sus resultados y guarda sus figuras en `figs/` y sus números en `results/`.
La Pregunta 1 usa `random.seed(2026)` para que las señales sean reproducibles.

Para regenerar el informe Word (requiere Node.js y el paquete `docx`):

```bash
cd informe && node build_docx.js
```
