from cx_Freeze import setup, Executable

setup(
   name="Elmos",
   version="1.0",
   description="Project",
   executables=[Executable("start.py", base="gui")],
)