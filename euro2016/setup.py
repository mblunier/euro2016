import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid_exclog',
    'pyramid_simpleform',
    'pyramid_beaker',
    'SQLAlchemy',
    'transaction',
    'cryptacular',
    'zope.sqlalchemy',
    'waitress',
    ]

setup(name='euro2016',
      version='0.1',
      description='euro2016',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Markus Blunier',
      author_email='mblunier@gmx.ch',
      url='http://euro2016.rolotec.ch',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='euro2016',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = euro2016:main
      [console_scripts]
      initialize_euro2016_db = euro2016.scripts.initializedb:main
      """,
      )
