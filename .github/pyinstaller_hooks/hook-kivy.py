from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Minimal custom hook to avoid CI failures in upstream hook-kivy.
datas = collect_data_files("kivy", include_py_files=False)
binaries = collect_dynamic_libs("kivy")
hiddenimports = [
    "kivy_deps.angle",
    "kivy_deps.glew",
    "kivy_deps.sdl2",
]
