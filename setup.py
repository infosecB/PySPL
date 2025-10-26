"""
Setup configuration for PySPL
"""

from setuptools import setup, find_packages
import os

# Read version from pyspl/__init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "pyspl", "__init__.py")
    with open(init_path, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError("Version not found")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyspl",
    version=get_version(),
    author="PySPL Contributors",
    author_email="",
    description="A Python library for running Splunk SPL queries against Python dictionaries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/infosecB/PySPL",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - pure Python!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    keywords="splunk spl query search analytics data",
    project_urls={
        "Bug Reports": "https://github.com/infosecB/PySPL/issues",
        "Source": "https://github.com/infosecB/PySPL",
    },
)
