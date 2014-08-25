from setuptools import setup

setup(
    name='gpxseg',
    version='0.2',
    author='Damian Braun',
    author_email='brunek5252@gmail.com',
    py_modules=['gpxseg'],
    entry_points={
        'console_scripts': ['gpxseg=gpxseg:main']
        },
    install_requires=[
        'docopt',
        'nominatim',
        'pytz',
        'tzlocal'
        ],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console'
        ]
)
