"""
Setup configuration for PySPL
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyspl",
    version="0.1.0",
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
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
