#!/usr/bin/env python
"""Build and install gmx Python module against an existing Gromacs install.

Build and install libgromacs and libgmxapi, then

    gmxapi_DIR=/path/to/gromacs python setup.py install --user

or

    pip install path/to/setup_py_dir --user

Note that setup.py by itself doesn't like to be run from other directories than the one in which
it is located. In general, just use pip. If you don't want to use pip, just plan on cluttering your
source directory. Sorry.
"""

import os
import platform
import subprocess
import sys
from warnings import warn

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.test import test as TestCommand

extra_link_args=[]

# readthedocs.org isn't very specific about promising any particular value...
build_for_readthedocs = False
if os.getenv('READTHEDOCS') is not None:
    build_for_readthedocs = True

build_gromacs = False
if build_for_readthedocs:
    build_gromacs = True


def get_gromacs(url, cmake_args=[], build_args=[]):
    """Download, build, and install a local copy of gromacs to a temporary location.
    """
    try:
        import ssl
    except:
        warn("get_gromacs needs ssl support, but `import ssl` fails")
        raise
    import urllib2
    import tempfile
    import tarfile
    import shutil
    # make temporary source directory
    sourcedir = tempfile.mkdtemp()
    try:
        with tempfile.TemporaryFile(suffix='.tgz', dir=sourcedir) as fh:
            fh.write(urllib2.urlopen(url).read())
            fh.seek(0)
            archive = tarfile.open(fileobj=fh)
            # Get top-level directory name in archive
            root = archive.next().name
            # Extract all under top-level to source directory
            archive.extractall(path=sourcedir)
    except:
        shutil.rmtree(sourcedir, ignore_errors=True)
        raise
    # make temporary build directory
    build_temp = tempfile.mkdtemp()
    # run CMake to configure with installation directory in extension staging area
    env = os.environ.copy()
    try:
        subprocess.check_call(['cmake', os.path.join(sourcedir, root)] + cmake_args, cwd=build_temp, env=env)
    except:
        warn("Not removing source directory {} or build directory {}".format(sourcedir, build_temp))
        raise
    # run CMake to build and install
    try:
        subprocess.check_call(['cmake', '--build', '.', '--target', 'install'] + build_args, cwd=build_temp)
    except:
        warn("Not removing source directory {} or build directory {}".format(sourcedir, build_temp))
        raise
    shutil.rmtree(build_temp, ignore_errors=True)
    shutil.rmtree(sourcedir, ignore_errors=True)


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    # if has_flag(compiler, '-std=c++14'):
    if False and has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')

class CMakeGromacsBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):

        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # Note distutils prints extra output if DISTUTILS_DEBUG environement variable is set.
        # The setup.py build command allows a --debug flag that will have set self.debug
        # cfg = 'Debug' if self.debug, else 'Release'
        cfg = 'Release'
        if self.debug:
            cfg = 'Debug'
        build_args = ['--config', cfg]
        cmake_args = ['-DPYTHON_EXECUTABLE=' + sys.executable,
                      ]
        if platform.system() == "Windows":
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j8']

        # Find installed GROMACS
        GROMACS_DIR = os.getenv('GROMACS_DIR')
        if GROMACS_DIR is None:
            gmxapi_DIR = os.getenv('gmxapi_DIR')
            if gmxapi_DIR is not None:
                GROMACS_DIR = gmxapi_DIR
            GROMACS_DIR = ""

        # Build and install a private copy of GROMACS, if necessary.

        # This could be replaced with a pypi gromacs bundle. We also may prefer to move to scikit-build.
        # Refer to the 'cmake' pypi package for a simple example of bundling a non-Python package to satisfy a dependency.
        # There is no caching: gromacs is downloaded and rebuilt each time. On readthedocs that should be okay since
        # libgmxapi is likely to update more frequently than gmxpy.
        if build_gromacs:
            gromacs_url = "https://bitbucket.org/kassonlab/gromacs/get/0.0.0.tar.gz"
            gmxapi_DIR = os.path.join(extdir, 'data/gromacs')

            # Warning: make sure not to recursively build the Python module...
            get_gromacs(gromacs_url,
                        cmake_args + ['-DCMAKE_INSTALL_PREFIX=' + gmxapi_DIR],
                        build_args)
            GROMACS_DIR = gmxapi_DIR

        # print("extdir is {}".format(extdir))
        # gromacs_install_path = os.path.join(os.path.abspath(self.build_temp), 'gromacs')
        staging_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gmx')
        print("__file__ is {}".format(__file__))
        print("staging_dir is {}".format(staging_dir))
        print("build_temp is {}".format(self.build_temp))

        env = os.environ.copy()
        env['GROMACS_DIR'] = GROMACS_DIR
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir]
        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        # We are not relying on distutils to build, so we don't give any sources to Extension
        Extension.__init__(self, name, sources=[])
        # but we will use the sourcedir when our overridden build_extension calls cmake.
        self.sourcedir = os.path.abspath(sourcedir)

package_data = {
        'gmx': ['data/topol.tpr'],
    }
if build_gromacs:
    package_data['gmx'].append('data/gromacs')

setup(
    name='gmx',

    packages=['gmx', 'gmx.test'],
    # package_dir = {'gmx': package_dir},

    # Get version from the most recent tag in the form X.Y.Z
    # from the git repository rooted in the current directory
    use_scm_version = {'root': '.', 'relative_to': __file__},

    # Require Python 2.7 or 3.3+
    python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',

    # Use Git commit and tags to determine Python package version
    # If cmake package causes weird build errors like "missing skbuild", try uninstalling and reinstalling the cmake
    # package with pip in the current (virtual) environment: `pip uninstall cmake; pip install cmake`
    setup_requires=['setuptools_scm', 'cmake'],

    #install_requires=['docutils', 'cmake', 'sphinx_rtd_theme'],
    # optional targets:
    #   docs requires 'docutils', 'sphinx>=1.4', 'sphinx_rtd_theme'
    #   build_gromacs requires 'cmake>=3.4'
    install_requires=[],

    author='M. Eric Irrgang',
    author_email='ericirrgang@gmail.com',
    description='Gromacs Python module',
    license = 'LGPL',
    url = 'https://bitbucket.org/kassonlab/gromacs',
    #keywords = '',

    ext_modules = [CMakeExtension(
        'gmx.core'
    )],

    # Bundle some files needed for testing
    package_data = package_data,
    # test suite to be invoked by `setup.py test`
    tests_require = ['tox', 'numpy'],
    cmdclass={'build_ext': CMakeGromacsBuild,
              'test': Tox},
#    test_suite = 'gmx.test.test_gmx',

    zip_safe=False
)
