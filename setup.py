from setuptools import setup

desc = 'time series and statistics library for financial instruments',
packages = ['tserie', 'tserie.config', 'tserie.tests', 'tserie.scripts']
requirements = [x for x in open('requirements.txt', 'r')],

setup(name='tserie',
      version=0.01,
      description=desc,
      url='https://github.com/aberger91',
      author='Andrew Berger',
      packages=packages,
      install_requires=requirements,
      tests_require=['tserie'],
      test_suite='tserie.tests.test.main',
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'tserie-plot = tserie.scripts.plot:main',
              'tserie-corr = tserie.scripts.corr:main',
              'tserie-auto = tserie.scripts.auto:main'
              ]
          }
      )
