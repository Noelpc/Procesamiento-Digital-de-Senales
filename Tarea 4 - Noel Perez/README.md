# Tarea 4 - Audio en C

## Construcción

Asegúrese de tener instalado el servidor Jack y los respectivos archivos de desarrollo:
```bash
sudo apt install jackd libjack-dev
```

Opcionalmente puede instalar también `QJackCtl` la cuál es una
herramienta gráfica que le permite configurar e iniciar de manera sencilla el servidor:
```bash
sudo apt install qjackctl
```

## Ejecución
### Procesamiento desde micrófono

```bash
./jack -c
```

### Procesamiento desde archivo

```bash
./jack < test.wav
```

### Selección del filtro (k, alpha)
Variable de entorno `PRESET`: 0 = 50 ms/0.6 (defecto), 1 = 250 ms/0.4, 2 = 500 ms/0.2
```bash
make
PRESET=2 ./jack < test.wav
```

### Python (polos/ceros y filtrado con lfilter)
```bash
pip install numpy scipy matplotlib
python3 filtro.py test.wav
```
