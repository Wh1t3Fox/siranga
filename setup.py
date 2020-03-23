#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
version = '0.1'

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='siranga',
    version=version,
    description='SSH Utility',
    license="MIT",
    long_description=long_description,
    author='Wh1t3Fox',
    author_email='dev@exploit.design',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],
    keywords='ssh',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['prompt_toolkit==3.0.4', 'ssh-config==0.0.19', 'prettytable==0.7.2'],
    extras_require={
        'dev': ['ipython==7.13.0','pytest==4.6.7'],
    },
    entry_points={
        'console_scripts': [
            'siranga = siranga.__main__:main',
        ],
    },
    include_package_data = True,
)
