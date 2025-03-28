from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name="atom_count",
    ext_modules=cythonize("atom_count.pyx"),
    include_dirs=[numpy.get_include()],
)

