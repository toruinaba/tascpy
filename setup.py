import re
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import setup
from setuptools import find_packages

with open("src/tascpy/__init__.py", encoding="utf-8") as f:
    VERSION = re.search(r'^__version__ = "([^"]+)"', f.read(), re.M).group(1)

setup(
    name="tascpy",
    version=VERSION,
    description="タスク計測データ処理用のPythonライブラリ",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="toru_inaba",
    author_email="inaba.tooru@takenaka.co.jp",
    url="https://github.com/toruinaba/tascpy",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
    extras_require={"plotly": ["plotly"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            # 必要に応じてCLIエントリポイントを追加
        ],
    },
)
