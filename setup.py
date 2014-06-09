from setuptools import setup

setup(
        name='gpxseg',
        version='0.1',
        author='Damian Braun',
        author_email='brunek5252@gmail.com',
        packages=['nominatim'],
        py_modules=['gpxseg'],
        entry_points={
            'console_scripts': ['gpxseg=gpxseg:main']
            },
        install_requires=[
            'docopt'
            ],
        classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7'
            ]
)
