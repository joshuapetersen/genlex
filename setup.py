from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension("genesis_bridge",
        ["genesis_bridge.cpp"],
    ),
    Pybind11Extension("sovereign_spinlock",
        ["spinlock_kernel.cpp"],
    ),
]

setup(
    name="genesis_bridge",
    ext_modules=ext_modules,
    packages=[],
    py_modules=[],
    cmdclass={"build_ext": build_ext},
)
