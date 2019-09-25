import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
import platform

# Package meta-data.
NAME = 'graph_clustering'
DESCRIPTION = 'Clusters objects found in astronomical images by their visual similarity'
URL = 'https://github.com/garrethmartin/HSC_UML'
EMAIL = 'g.martin4@herts.ac.uk'
AUTHOR = 'garrethmartin'

# What packages are required for this module to be executed?
with open('requirements.txt', 'r') as f:
    REQUIRED = f.readlines()

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)

if platform.system() == 'Windows':
    c_install_command = "install.bat"
else:
    c_install_command = "./install.sh"

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        check_call(c_install_command)
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        check_call(c_install_command)
        install.run(self)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    #long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    scripts=['scripts/classify.py'],
    #If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    entry_points={},
    install_requires=REQUIRED,
    include_package_data=True,
    package_data={'': []},
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
        'develop': PostDevelopCommand,  # pip silences the success output of these commands.
        'install': PostInstallCommand,  # pip silences the success output of these commands.
    },
)
