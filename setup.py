from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import setup
from setuptools import find_packages

setup(
    name="tascpy",
    version="0.0.2",
    description="Data processing for tasc data.",
    author="1500197",
    author_email="",
    url="",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[]
)
