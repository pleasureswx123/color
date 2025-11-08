"""
Setup script for color correction system
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="color-correction",
    version="1.0.0",
    author="Color Correction Contributors",
    description="Image color correction system using reference color checker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/color-correction",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "scikit-image>=0.22.0",
        "Pillow>=10.0.0",
        "matplotlib>=3.8.0",
        "scikit-learn>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "color-correct=src.cli:main",
        ],
    },
)

