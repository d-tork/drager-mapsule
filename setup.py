from setuptools import setup, find_packages

setup(
    name='business-vicinity',
    version='1.0',
    author='Daniel Torkelson',
    packages=find_packages(include=['vicinity', 'vicinity.*']),
    install_requires=[
        'numpy',
        'pandas',
        'PyYAML',
        ],
    extras_require={
        'dev': ['pytest', 'wheel']
    }
)
