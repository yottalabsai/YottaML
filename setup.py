import os

from setuptools import setup, find_packages

print(os.path.dirname(__file__))

with open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "r") as fh:
    requirements = fh.readlines()

print("requirements", requirements)

NAME = "yottactl"
DESCRIPTION = (
    "This is a lightweight library that works as a connector to Yottalabs public API."
)

VERSION = None

about = {}

with open("README.md", "r") as fh:
    about["long_description"] = fh.read()

root = os.path.abspath(os.path.dirname(__file__))

if not VERSION:
    with open(os.path.join(root, "yotta", "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

setup(
    name=NAME,
    version=about["__version__"],
    license="MIT",
    description=DESCRIPTION,
    long_description=about["long_description"],
    long_description_content_type="text/markdown",
    AUTHOR="yottalabs",
    url="https://github.com/yottalabsai/yottactl",
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
