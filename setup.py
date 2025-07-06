import os

from setuptools import setup, find_packages

from yotta.__version__ import __version__

with open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "r") as fh:
    requirements = fh.readlines()

NAME = "yottactl"
DESCRIPTION = (
    "This is a lightweight library that works as a connector to Yottalabs public API."
)

about = {"__version__": __version__}

with open("README.md", "r") as fh:
    about["long_description"] = fh.read()

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=about["long_description"],
    long_description_content_type="text/markdown",
    AUTHOR="yottalabs",
    url="https://github.com/yottalabs/yottactl",
    keywords=["yotta", "Public API"],
    install_requires=[req for req in requirements],
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
