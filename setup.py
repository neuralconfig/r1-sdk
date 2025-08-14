"""
Setup script for the RUCKUS One Python SDK.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ruckus-one",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Python SDK for the RUCKUS One (R1) network management system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neuralconfig/r1-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
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
        "requests>=2.25.0",
        "cmd2>=2.4.0",
    ],
    entry_points={
        'console_scripts': [
            'ruckus-cli=ruckus_one.cli.main:main',
            'ruckus-interactive=ruckus_one.cli.interactive:main',
        ],
    },
    scripts=[
        'bin/ruckus-cli',
    ],
)