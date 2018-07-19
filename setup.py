# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="yafl",
    version="0.2",
    author="Leonardo Barcaroli",
    url="https://github.com/leophys/YAFL",
    py_modules=['yafl'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'tinydb',
        'uwsgi',
        'Click',
        'pyyaml',
    ],
    install_test=[
        'pytest',
    ],
    entry_points='''
        [console_scripts]
        yafl=yafl.yafl:cli_run
    '''
)
