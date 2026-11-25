# Proyecto 2 PDS - LPC subbanda vs LPC-10
Probado en Linux (Ubuntu). Python 3.

## Instalación
```
pip install -r requirements.txt
```
PEAQ (ITU BS.1387, implementación peaqb-fast):
```
git clone https://github.com/akinori-ito/peaqb-fast.git
cd peaqb-fast && ./configure && make      # binario: src/peaqb
```

## Uso (con referencia_16k.wav y referencia_8k.wav en esta carpeta)
- `python lpc_subband.py referencia_16k.wav`: LPC-10, LPC subbanda, chequeo QMF; genera out_lpc.wav y out_subband.wav
- `python sweep.py referencia_16k.wav`: barrido de 50 configuraciones (CR y LSD) -> sweep_*.csv, cr_vs_lsd_*.pdf, qmf_resp.pdf
- `python peaq_eval.py referencia_16k.wav /ruta/peaqb-fast/src/peaqb`: ODG (PEAQ) de LPC-10 y configuraciones subbanda -> peaq_*.csv
  (peaqb exige 48 kHz/16 bit/estéreo; el script remuestrea y duplica el canal)
- Informe: `latexmk -pdf informe.tex` (requiere qmf_resp.pdf y cr_vs_lsd_referencia_16k.pdf); versión Word: informe.docx
- Guion del video: guion_video.txt

## Archivos
`lpc_subband.py` (codec y QMF), `sweep.py`, `peaq_eval.py`, `informe.*`, `diagrama.tex`, resultados `sweep_*.csv` y `peaq_*.csv`.
Resultado principal: LPC subbanda no mejora la compresión de LPC-10 con calidad perceptual equivalente.
