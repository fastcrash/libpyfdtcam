import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libpyfdtcam",
    version="1.0.0",
    author="losse83",
    author_email="losse83@posteo.de",
    description="A lib to contro FDT IP cameras.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastcrash/libpyfdtcam",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
