#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='nose-excel',
    version='2.0.0',
    url='https://github.com/efpato/nose-excel',
    author='Sergey Demenok',
    author_email='sergey.demenok@gmail.com',
    description='Nose plugin for excel report',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ],
    py_modules=['excel'],
    entry_points={
        'nose.plugins.0.10': [
            'excel = excel:Excel'
        ]
    },
    install_requires=[
        'xlwt-future>=0.8.0'
    ]
)
