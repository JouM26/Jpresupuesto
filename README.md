# Jpresupuesto

Aplicación de cotizaciones en Kivy/KivyMD.

## Build de app en GitHub Actions (Windows)

Este repositorio ya incluye un workflow para compilar la app a ejecutable Windows con PyInstaller.

Archivo del workflow:
- `.github/workflows/build-windows.yml`

Dependencias de build:
- `requirements.txt`
- `requirements-build.txt`

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

## Ejecutar localmente (desarrollo)

```bash
pip install -r requirements.txt
python app.py
```