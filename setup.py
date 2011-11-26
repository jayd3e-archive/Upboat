#Upboat/setup.py
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

entry_points = """
      [paste.app_factory]
      main = upboat:main
      """

requires = ['pyramid',
            'sqlalchemy',
            'mako']

setup(name='Upboat',
      version='0.1dev',
      description='',
      long_description=README + '\n\n' + CHANGES,
      install_requires=requires,
      url='http://localhost',
      packages=['upboat'],
      test_suite='upboat.tests',
      entry_points = entry_points
)
