#!/usr/bin/env python
"""Build and install gmx Python module against an existing Gromacs install.

Build and install libgromacs and libgmxapi, then

    gmxapi_DIR=/path/to/gromacs python setup.py install --user

or

    pip install path/to/setup_py_dir --user
"""

import os
import platform
import subprocess
import sys
from warnings import warn

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

#import gmx.version
__version__ = '0.0.7'

extra_link_args=[]

# Check for the GROMACS installation we will use or build.
build_for_readthedocs = False
# readthedocs.org isn't very specific about promising any particular value...
if os.getenv('READTHEDOCS') is not None:
    build_for_readthedocs = True

if os.getenv('BUILDGROMACS') is not None:
    build_gromacs = True
else:
    if build_for_readthedocs:
        build_gromacs = True
    else:
        build_gromacs = False
# Offer a user-friendly configuration check.
if not build_gromacs:
    if os.getenv('gmxapi_DIR') is None and os.getenv('GROMACS_DIR') is None:
        raise RuntimeError("Either set gmxapi_DIR or GROMACS_DIR to an existing installation\n"
                           "or set BUILDGROMACS to get a private copy. See installation docs...")

def get_gromacs(url, cmake_args=(), build_args=(), install_dir=None):
    """Download, build, and install a local copy of gromacs to a temporary location.
    """
    if os.path.exists(install_dir):
        # Exit early if we've already got it.
        cmake_config_dir = os.path.join(install_dir, 'share', 'cmake', 'gmxapi')
        if not os.path.isdir(cmake_config_dir):
            raise RuntimeError(
                "No gmxapi cmake hints at {}. GROMACS built without gmxapi enabled?".format(
                    cmake_config_dir))
        return

    cmake_args = list(cmake_args) + ['-DCMAKE_INSTALL_PREFIX=' + install_dir]
    try:
        import ssl
    except:
        warn("get_gromacs needs ssl support, but `import ssl` fails")
        raise
    try:
        from urllib.request import urlopen
    except ImportError:
        try:
            from urllib2 import urlopen
        except ImportError:
            raise RuntimeError("Need urllib or urllib2 package to download GROMACS.")
    import tempfile
    # import tarfile
    import zipfile
    import shutil
    # make temporary source directory
    sourcedir = tempfile.mkdtemp()
    try:
        with tempfile.TemporaryFile(suffix='.zip', dir=sourcedir) as fh:
            fh.write(urlopen(url).read())
            fh.seek(0)
            # archive = tarfile.open(fileobj=fh)
            archive = zipfile.ZipFile(fh)
            # # Get top-level directory name in archive
            # root = archive.next().name
            root = archive.namelist()[0]
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
        import cmake
        cmake_bin = os.path.join(cmake.CMAKE_BIN_DIR, 'cmake')
    except:
        raise
    try:
        subprocess.check_call([cmake_bin, os.path.join(sourcedir, root)] + cmake_args, cwd=build_temp, env=env)
    except:
        warn("Not removing source directory {} or build directory {}".format(sourcedir, build_temp))
        raise
    # run CMake to build and install
    try:
        subprocess.check_call([cmake_bin, '--build', '.', '--target', 'install'] + build_args, cwd=build_temp)
    except:
        warn("Not removing source directory {} or build directory {}".format(sourcedir, build_temp))
        raise
    shutil.rmtree(build_temp, ignore_errors=True)
    shutil.rmtree(sourcedir, ignore_errors=True)

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
            import cmake
            cmake_bin = os.path.join(cmake.CMAKE_BIN_DIR, 'cmake')
        except:
            raise
        try:
            out = subprocess.check_output([cmake_bin, '--version'])
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
        env = os.environ.copy()
        if 'CC' in env:
            cmake_args.append("-DCMAKE_C_COMPILER={}".format(env['CC']))
        if 'CXX' in env:
            cmake_args.append("-DCMAKE_CXX_COMPILER={}".format(env['CXX']))

        if platform.system() == "Windows":
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            if build_for_readthedocs:
                # save some RAM
                # We're pushing the limits of the readthedocs build host provisions. We might soon need
                # a binary package or mock library for libgmxapi / libgromacs.
                build_args += ['--', '-j4']
            else:
                build_args += ['--', '-j8']

        # Find installed GROMACS
        GROMACS_DIR = os.getenv('GROMACS_DIR')
        if GROMACS_DIR is None:
            gmxapi_DIR = os.getenv('gmxapi_DIR')
            if gmxapi_DIR is not None:
                GROMACS_DIR = gmxapi_DIR
            else:
                GROMACS_DIR = ""

        # Build and install a private copy of GROMACS, if necessary.

        # This could be replaced with a pypi gromacs bundle. We also may prefer to move to scikit-build.
        # Refer to the 'cmake' pypi package for a simple example of bundling a non-Python package to satisfy a dependency.
        # There is no caching: gromacs is downloaded and rebuilt each time. On readthedocs that should be okay since
        # libgmxapi is likely to update more frequently than gmxpy.
        # Linking is a pain because the package is relocated to the site-packages directory. We should really do this
        # in two stages.
        if build_gromacs:
            gromacs_url = "https://github.com/gromacs/gromacs/archive/release-2019.zip"
            gmxapi_DIR = os.path.join(extdir, 'data/gromacs')
            if build_for_readthedocs:
                extra_cmake_args = ['-DGMX_FFT_LIBRARY=fftpack',
                                    '-DGMX_GPU=OFF',
                                    '-DGMX_OPENMP=OFF',
                                    '-DGMX_SIMD=None',
                                    '-DGMX_USE_RDTSCP=OFF',
                                    '-DGMX_MPI=OFF',
                                    '-DGMXAPI=ON',
                                    ]
            else:
                extra_cmake_args = ['-DGMX_BUILD_OWN_FFTW=ON',
                                    '-DGMX_GPU=OFF',
                                    '-DGMX_THREAD_MPI=ON',
                                    '-DGMXAPI=ON',
                                    ]

            # Warning: make sure not to recursively build the Python module...
            get_gromacs(gromacs_url,
                        cmake_args + extra_cmake_args,
                        build_args, gmxapi_DIR)
            GROMACS_DIR = gmxapi_DIR
        env['GROMACS_DIR'] = GROMACS_DIR

        #
        staging_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gmx')
        print("__file__ is {} at {}".format(__file__, os.path.abspath(__file__)))

        # Compiled library will be put directly into extdir by CMake
        print("extdir is {}".format(extdir))
        print("staging_dir is {}".format(staging_dir))

        # CMake will be run in working directory build_temp
        print("build_temp is {}".format(self.build_temp))

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir]
        cmake_args += ['-DGMXAPI_INSTALL_PATH=' + extdir]
        cmake_args += ['-DGMXAPI_DISTINFO=OFF']
        # if platform.system() == "Windows":
        #     cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
        try:
            import cmake
            cmake_bin = os.path.join(cmake.CMAKE_BIN_DIR, 'cmake')
        except:
            raise

        cmake_command = [cmake_bin, ext.sourcedir] + cmake_args
        print("Calling CMake: {}".format(' '.join(cmake_command)))
        subprocess.check_call(cmake_command, cwd=self.build_temp, env=env)

        cmake_command = [cmake_bin, '--build', '.', '--target', 'install'] + build_args
        print("Calling CMake: {}".format(' '.join(cmake_command)))
        subprocess.check_call(cmake_command, cwd=self.build_temp)

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        # We are not relying on distutils to build, so we don't give any sources to Extension
        Extension.__init__(self, name, sources=[])
        # but we will use the sourcedir when our overridden build_extension calls cmake.
        self.sourcedir = os.path.abspath(sourcedir)

package_dir=os.path.join('src','gmx')

# This is probably here for the wrong reason. It triggers certain install behavior
# that we need to trigger, but probably has more state and circular dependencies than
# we have in mind.
package_data = {
        'gmx': ['data/topol.tpr'],
    }
if build_gromacs:
    package_data['gmx'].append('data/gromacs')

setup(
    name='gmx',

    version=__version__,

    # Require Python 2.7 or 3.3+
    python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',

    # If cmake package causes weird build errors like "missing skbuild", try uninstalling and reinstalling the cmake
    # package with pip in the current (virtual) environment: `pip uninstall cmake; pip install cmake`
    setup_requires=['setuptools>=28', 'scikit-build', 'cmake'],

    #install_requires=['docutils', 'cmake', 'sphinx_rtd_theme'],
    # optional targets:
    #   docs requires 'docutils', 'sphinx>=1.4', 'sphinx_rtd_theme'
    #   build_gromacs requires 'cmake>=3.4'
    install_requires=['setuptools>=28', 'cmake>=3.4', 'networkx>2'],

    author='M. Eric Irrgang',
    author_email='ericirrgang@gmail.com',
    description='GROMACS Python module',
    license = 'LGPL',
    url = 'https://github.com/kassonlab/gmxapi',
    #keywords = '',

    ext_modules = [CMakeExtension(
        'gmx.core'
    )],

    # Bundle some files needed for testing
    package_data = package_data,

    cmdclass={'build_ext': CMakeGromacsBuild},

    zip_safe=False
)
