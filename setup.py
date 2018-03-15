#!/usr/bin/env python3

'''setuptools module for aiospamc.'''

from pathlib import Path
from setuptools import setup, find_packages


readme = Path(__file__).absolute().parent / 'README.rst'
with readme.open(encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiospamc',
    version='0.4.1',

    description='An asyncio-based library to communicate with SpamAssassin\'s '
                'SPAMD service.',
    long_description=long_description,

    url='https://github.com/mjcaley/aiospamc',

    author='Michael Caley',
    author_email='mjcaley@darkarctic.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'License :: OSI Approved :: MIT License',

        'Topic :: Communications :: Email :: Filters',
    ],

    keywords='spam spamc spamassassin',

    packages=find_packages(exclude=['tests']),

    python_requires='!=2.*,!=3.0,!=3.1,!=3.2,!=3.3,!=3.4',
    setup_requires=['pytest-runner', ],
    tests_require=['pytest-asyncio>=0.6', 'pytest-cov', 'pytest>=3.0', 'asynctest'],
)
