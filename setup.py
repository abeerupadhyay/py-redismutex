import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version:
    VERSION = version.read().strip()

setup(
    name="redismutex",
    version=VERSION,
    description="Python implementation of Mutex using Redis",
    author="Abeer Upadhyay",
    author_email="ab.esquarer@gmail.com",
    url="https://github.com/esquarer/py-redismutex",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'future==0.16.0',
        'redis==2.10.6',
        'six==1.10.0'
    ],
    zip_safe=False,
    keywords="python redis mutex",
    classifiers=[
        'License :: MIT',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
