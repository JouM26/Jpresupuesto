# Jpresupuesto

Aplicación de cotizaciones en Kivy/KivyMD.

## Build de app en GitHub Actions (Windows)

Este repositorio ya incluye un workflow para compilar la app a ejecutable Windows con PyInstaller.

Archivo del workflow:
- `.github/workflows/build-windows.yml`

Dependencias de build:
- `requirements.txt`
- `requirements-build.txt`

Nota de estabilidad CI: requirements-build.txt fija pyinstaller-hooks-contrib en una versión alineada con PyInstaller para evitar errores de hooks en builds de Kivy.

Generacion de PDF: el proyecto usa fpdf2 (compatible con Android) para mantener la exportacion de cotizaciones e historial tambien en celular.

Adicionalmente, el workflow usa un hook local en .github/pyinstaller_hooks/hook-kivy.py para evitar fallos del hook oficial de Kivy en runners de GitHub Actions.

### Como ejecutar el build

1. Sube estos cambios a GitHub en la rama `main`.
2. Ve a la pestaña `Actions` del repositorio.
3. Ejecuta el workflow `Build Windows App` con `Run workflow`.
4. Al terminar, descarga el artefacto `JPresupuesto-windows`.

### Build automatico en release

Si creas un release en GitHub, el workflow tambien se ejecuta y adjunta:
- `JPresupuesto-windows.zip`

### Resultado esperado

El zip contiene la app compilada en:
- `dist/JPresupuesto/`

## Build de app para celular (Android APK)

Este repositorio tambien incluye build automatico Android:
- `.github/workflows/build-android.yml`
- `buildozer.spec`

### Como generar el APK

1. Haz push a `main` o ejecuta manualmente el workflow `Build Android APK` en `Actions`.
2. Verifica que `buildozer.spec` este en la raiz del repositorio y subido a GitHub.
3. Al finalizar, descarga el artefacto:
- `JPresupuesto-android-apk`
4. Ese artefacto contiene el archivo `.apk` para instalar en Android.

### Notas Android

- El primer build Android puede tardar bastante (descarga SDK/NDK dentro del contenedor).
- En Android, al generar PDF la app informa la ruta del archivo en lugar de abrirlo automaticamente.

### Si falla el workflow

1. Abre la corrida en `Actions`.
2. Descarga el artefacto `build-logs-windows`.
3. Revisa `pyinstaller.log` para ver el error exacto de compilación.

Nota: en GitHub Actions se fuerza `KIVY_WINDOW=mock` y `KIVY_GL_BACKEND=mock` porque el runner no tiene OpenGL real; esto afecta solo al build, no al uso normal de la app instalada.

## Ejecutar localmente (desarrollo)

```bash
pip install -r requirements.txt
python app.py
```

## Build manual recomendado (Windows)

```bash
pip install -r requirements-build.txt
python -m PyInstaller --noconfirm --clean --windowed --name JPresupuesto --hidden-import kivy_deps.angle --hidden-import kivy_deps.glew --hidden-import kivy_deps.sdl2 --hidden-import kivymd --exclude-module kivy.tests app.py
```