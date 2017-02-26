from setuptools import setup

setup(name='tserie',
      version=0.01,
      description='time series and statistics library for financial instruments',
      url='https://github.com/aberger91',
      author='Andrew Berger',
      packages=['tserie', 'tserie.tests', 'tserie.config'],
      install_requires=[x for x in open('requirements.txt', 'r')],
      zip_safe=False
      )
