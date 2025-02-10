from setuptools import setup, find_packages

setup(
    name="supersimplestockmarket",
    version="0.1.0",
    author="Aparna Rajan",
    author_email="aparnapr121@gmail.com",
    description="A simple stock market simulation package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aparnapr121/SimpleSuperStockMarket",
    packages=find_packages(),
    install_requires=[

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
