import os
import setuptools


PACKAGE_NAME = "brainvoyagertools"

def get_version():
    """Get version number."""

    with open(os.path.join("src", PACKAGE_NAME, "__init__.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("'")[1]
    return "None"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = PACKAGE_NAME,
    description=\
    'BrainVoyager Tools - ' \
    'An object-oriented approach to create, read and write common plain-text BrainVoyager input formats with Python',
    author='Florian Krause',
    author_email='me@floriankrause.org',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/fladd/brainvoyagertools',
    version=get_version(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['numpy>=1,<2',
                      'scipy>=1,<2',
                      ],
)
