import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version:
    VERSION = version.read().strip()

setup(
    name="redismutex",
    version=VERSION,
    description="Python implementation of mutex using redis",
    url="https://github.com/esquarer/py-redismutex",
    author="Abeer Upadhyay",
    author_email="ab.esquarer@gmail.com",
    license='MIT',
    keywords="python redis mutex",
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'future==0.16.0',
        'redis==2.10.6'
    ],
    project_urls={
        'Source': 'https://github.com/esquarer/py-redismutex/',
        'Documentation': 'http://py-redismutex.readthedocs.io/en/latest/',
        'Tracker': 'https://github.com/esquarer/py-redismutex/issues/',
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ]
)
