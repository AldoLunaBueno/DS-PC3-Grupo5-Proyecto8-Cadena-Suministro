# Bitácora Sprint 1: Arquitectura Local-First y DevSecOps en 3 Capas

Este documento explica la arquitectura "local-first" que estamos implementando y las decisiones de ingeniería detrás de ella.

## 1. Filosofía: Hilo Rojo DevSecOps (3 Capas)

Usamos tres capas de validación (siguiendo la *Lectura 11* del curso sobre Git Hooks y CI/CD) para garantizar calidad y seguridad en el código:

1.  **Capa 1: Hooks de Git (Rápidos):** Se ejecutan en la máquina del desarrollador *antes* de un `git commit` o `git push`. Su objetivo es fallar rápido y validar solo los archivos modificados.
2.  **Capa 2: CI Local (Completo):** Una simulación *completa* del pipeline de CI, ejecutada por el desarrollador (vía `make ci-local` o un hook `pre-push`) *antes* de subir el código.
3.  **Capa 3: CI Remoto (Cumplimiento):** El pipeline real en GitHub Actions. Es la fuente final de verdad que se ejecuta en un entorno limpio.

## 2. Decisión Clave: El `Makefile` como orquestador central

Para evitar duplicar código (principio DRY), **toda la lógica de CI se centraliza en el `Makefile`**.

* Tanto la Capa 2 (CI Local) como la Capa 3 (CI Remoto) **no contendrán lógica de negocio**.
* El script `scripts/ci-local.sh` y el pipe `.github/workflows/ci.yml` solo usarán targets del `Makefile` así: `make test`, `make lint`, `make sast`, etc..
* Por ejemplo, si necesitamos cambiar cómo se ejecuta `bandit`, solo lo editamos en el `Makefile`.

## 3. Decisión Clave: Hooks Manuales vs. Framework `pre-commit`

La *Lectura 11* menciona el framework `pre-commit`, pero hemos decidido **usar scripts de hooks manuales** en `.githooks/` por dos razones:

1.  **Control y Aprendizaje:** Nos obliga a dominar los comandos de Git de bajo nivel (`git diff --cached -z`) en lugar de abstraerlos.
2.  **Entorno Único (DRY):** El framework `pre-commit` crea sus propios entornos aislados. Esto crea dos mundos: las herramientas del hook vs. las herramientas del `Makefile`. Al usar hooks manuales, podemos forzar que **todas las capas usen las mismas versiones de herramientas** definidas en `requirements.txt` o instaladas desde el `Makefile`.

## 4. Solución al "Problema del entorno virtual" en Hooks Manuales

El problema de los hooks manuales es que fallan si el desarrollador olvida activar su entorno virtual (`source .venv/bin/activate`).

**Nuestra solución:** Los scripts en `.githooks/` son robustos. No llaman a `flake8` directamente, sino que usan la ruta explícita al binario instalado por el `Makefile` (`.venv/bin/flake8`). Esto garantiza que el hook use la versión del proyecto, independientemente de si el venv está activado o no, al menos para las herramientas de Python.