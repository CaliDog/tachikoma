from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))

with open('requirements.txt') as f:
    dependencies = f.read().splitlines()

long_description = """
Tachikoma is a jobs pipeline for connecting to services, processing results, and sending notifications. It handles
all the magic bits like storage and diffing for you, and all you have to do is focus on the meat and potatos of
what you want to do! 
"""

setup(
    name='tachikoma',
    version="1.4",
    url='https://github.com/CaliDog/tachikoma/',
    author='Ryan Sears',
    install_requires=dependencies,
    setup_requires=dependencies,
    author_email='ryan@calidog.io',
    description='Tachikoma is an alerting pipeline so smart it\'s scary',
    long_description=long_description,
    packages=['tachikoma',],
    include_package_data=True,
    license = "MIT",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Framework :: AsyncIO"
    ],
)