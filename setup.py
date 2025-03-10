from setuptools import setup, find_packages

setup(
    name="prorca",  # This should match what you want in pip install
    version="0.1.0",
    author="Your Team",
    author_email="arunks@profitops.ai",
    description="ProRCA - Root Cause Analysis Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/profitopsai/ProRCA",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        # Add dependencies if needed
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
