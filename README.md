# Jpresupuesto

Aplicación de cotizaciones en Kivy/KivyMD.

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
- En Android, los PDFs se guardan dentro del almacenamiento de la app y se informa la ruta generada en lugar de abrirlos automaticamente.

### Si falla el workflow

1. Abre la corrida en `Actions`.
2. Revisa el log del workflow Android.

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