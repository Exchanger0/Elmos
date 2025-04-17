from cx_Freeze import setup, Executable

build_exe_option = {"include_files": [("files", "files")]}

setup(
   name="Elmos",
   version="1.3",
   description="Math calculator",
   options={"build_exe": build_exe_option},
   executables=[Executable("start.py", base="gui")],
)