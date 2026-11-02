/*
 * Copyright (C) 2024
 * Pablo Alvarado
 *
 * This file is part of the EL-5805 Digital Signal Processing Lecture at
 * the Costa Rica Institute of Technology
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the authors nor the names of its contributors may be
 *    used to endorse or promote products derived from this software without
 *    specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

/** 
 * \file   tarea04.c
 *         Contains the processing function
 * \author Pablo Alvarado
 * \author Student
 */

/** 
 * \file   tarea04.c
 *         Contains the processing function
 * \author Pablo Alvarado
 * \author Student
 */

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

/*
 * Filtro H(z) = (1-a) / (1 - a z^-k)
 * Ecuacion de diferencias: y[n] = a*y[n-k] + (1-a)*x[n]
 *
 * Se usa un buffer circular de k muestras con las ultimas salidas.
 * Preset seleccionable con la variable de entorno PRESET (0, 1 o 2):
 *   0: k = Fs*50 ms,  a = 0.6   (por defecto)
 *   1: k = Fs*250 ms, a = 0.4
 *   2: k = Fs*500 ms, a = 0.2
 * Ejemplo: PRESET=2 ./jack < test.wav
 */
static const float  alphas[3] = {0.6f, 0.4f, 0.2f};
static const float  delays[3] = {0.050f, 0.250f, 0.500f}; /* segundos */

static float*       ybuf  = NULL; /* ultimas k salidas */
static unsigned int K     = 1;    /* retardo en muestras */
static unsigned int pos   = 0;    /* posicion actual en el buffer circular */
static float        alpha = 0.6f;

void init(const unsigned int Fs) {
  int p = 0;
  const char* env = getenv("PRESET");
  if (env != NULL) p = atoi(env);
  if (p < 0 || p > 2) p = 0;

  alpha = alphas[p];
  K     = (unsigned int)(Fs * delays[p] + 0.5f);
  if (K < 1) K = 1;

  free(ybuf);
  ybuf = (float*)calloc(K, sizeof(float));
  pos  = 0;
  fprintf(stderr, "Preset %d: k=%u muestras, alpha=%.2f\n", p, K, alpha);
}

/**
 * Process a buffer of data (mono).
 *
 * @return zero if everything is ok (valor esperado por jack).
 */
int process(const unsigned int Fs,
            const int nframes,
            const float* in,
            float* out) {
  const float g = 1.0f - alpha;
  int n;
  if (ybuf == NULL) { /* sin init: pasar la senal */
    memcpy(out, in, sizeof(float)*nframes);
    return 0;
  }
  for (n = 0; n < nframes; ++n) {
    const float y = alpha*ybuf[pos] + g*in[n]; /* ybuf[pos] = y[n-k] */
    ybuf[pos] = y;
    out[n]    = y;
    if (++pos == K) pos = 0;
  }
  return 0; /* everything is ok */
}
