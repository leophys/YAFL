from setuptools import setup

setup(
    name="yafl",
    version="0.1",
    author="Leonardo Barcaroli",
    url="https://github.com/leophys/YAFL",
    py_modules=['yafl'],
    install_requires=[
        'Flask',
        'tinydb',
        'uwsgi',
        'Click'
    ],
    entry_points='''
        [console_scripts]
        yafl=yafl:cli_run
    '''
)
