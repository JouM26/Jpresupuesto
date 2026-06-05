[app]

title = JPresupuesto
package.name = jpresupuesto
package.domain = com.joum26

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,txt,md,json
source.exclude_dirs = .git,.github,__pycache__,venv,.venv,build,dist

version = 0.1.0

requirements = python3,kivy==2.3.1,kivymd==1.2.0,fpdf2,pillow

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 0
