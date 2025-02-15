from cx_Freeze import setup, Executable

setup(
   name="Elmos",
   version="1.3",
   description="Project",
   executables=[Executable("start.py", base="gui")],
)