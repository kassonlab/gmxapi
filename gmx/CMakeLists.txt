#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2017, by the GROMACS development team, led by
# Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
# and including many others, as listed in the AUTHORS file in the
# top-level source directory and at http://www.gromacs.org.
#
# GROMACS is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# GROMACS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with GROMACS; if not, see
# http://www.gnu.org/licenses, or write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
#
# If you want to redistribute modifications to GROMACS, please
# consider that scientific software is very special. Version
# control is crucial - bugs must be traceable. We will be happy to
# consider code for inclusion in the official distribution, but
# derived work must not be called official GROMACS. Details are found
# in the README & COPYING files - if they are missing, get the
# official version at http://www.gromacs.org.
#
# To help us fund GROMACS development, we humbly ask that you cite
# the research papers on the package. Check out http://www.gromacs.org.

# Set up the build staging area
# To do: make targets dependent on this. Clean out old .pyc files.
set(GMXPYFILES
    __init__.py
#    __main__.py
	context.py
    data.py
    exceptions.py
    fileio.py
	md.py
	runner.py
    status.py
    system.py
    util.py
    )
# Make the Python module files available in the build directory.
file(COPY ${GMXPYFILES} DESTINATION ${Gromacs_BINARY_DIR}/api/gmx)
file(COPY data/topol.tpr DESTINATION ${Gromacs_BINARY_DIR}/api/gmx/data)
file(COPY
    test/__init__.py
    test/test_pymd.py
    test/test_docstrings.py
    test/test_exceptions.py
    test/test_fileio.py
    test/test_gmx.py
    DESTINATION ${Gromacs_BINARY_DIR}/api/gmx/test)

# Build the C++ extension

#pybind11_add_module(core gmx_core.cpp data.cpp options.cpp runner.cpp trajectory.cpp)
pybind11_add_module(pygmx_core
					core/core.cpp
                    core/pymd.cpp
					#context.cpp
					core/pyrunner.cpp
					#session.cpp
					)

# The target name is for clarity, but the installed module will be gmx.core
set_target_properties(pygmx_core PROPERTIES OUTPUT_NAME core)

# Set the output to the staging area
# For build managed by Python setuptools, use Python package staging area
option(SETUPTOOLS "Tell CMake that it is being invoked by Python setuptools" OFF)
set(PYGMX_LIBRARY_OUTPUT_DIRECTORY
    ${Gromacs_BINARY_DIR}/api/gmx
    CACHE
    PATH
    "Set to override target LIBRARY_OUTPUT_DIRECTORY for Python C++ extension (as by setuptools)")
mark_as_advanced(PYGMX_LIBRARY_OUTPUT_DIRECTORY)
set_target_properties(pygmx_core PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PYGMX_LIBRARY_OUTPUT_DIRECTORY})

target_link_libraries(pygmx_core PRIVATE gmxapi)
target_include_directories(pygmx_core INTERFACE ${PYTHON_INCLUDE_DIRS})

target_include_directories(pygmx_core PRIVATE
	${CMAKE_CURRENT_SOURCE_DIR}
	${CMAKE_CURRENT_BINARY_DIR}
	)

# RPATH managemen
set(PYGMX_RPATH "${CMAKE_INSTALL_PREFIX}/${LIB_INSTALL_DIR}" CACHE PATH
    "Set to override RPATH for Python C++ extension (as by setuptools)")
mark_as_advanced(PYGMX_RPATH)
# don't skip the full RPATH for the build tree
set_target_properties(pygmx_core PROPERTIES SKIP_BUILD_RPATH FALSE)

# (but later on when installing)
if (SETUPTOOLS)
    # If building with setuptools, CMake will not be performing the install
    set_target_properties(pygmx_core PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
else()
    # when building, don't use the install RPATH already
    set_target_properties(pygmx_core PROPERTIES BUILD_WITH_INSTALL_RPATH FALSE)
endif()
set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH ${PYGMX_RPATH})
set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

# Install target should copy Python source files into lib/python{version}/gmx
# and properly install core.so into same.

# Create the 'install' target, which is different than the setuptools
# installation location.
set(PYGMX_INSTALL_DIR ${LIB_INSTALL_DIR}/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR} CACHE PATH "Installation directory for python module")
# Clean destination directory to avoid confusion
install(CODE "MESSAGE(\"Removing existing Python module (if any) at ${CMAKE_INSTALL_PREFIX}/${PYGMX_INSTALL_DIR}/gmx\")")
install(CODE "file(REMOVE_RECURSE ${CMAKE_INSTALL_PREFIX}/${PYGMX_INSTALL_DIR}/gmx)")
# TODO: Be explicit about submodules to install to allow optional subdirectories
# for test, data, documentation, etc.
install(FILES ${GMXPYFILES} DESTINATION ${PYGMX_INSTALL_DIR}/gmx
		COMPONENT python_module)
install(CODE "MESSAGE(\"Python module installed to ${CMAKE_INSTALL_PREFIX}/${PYGMX_INSTALL_DIR}.
You will need to update your PYTHONPATH environment variable for python to find it.\")")
# The compiled core module is a submodule of the 'gmx' package.
install(TARGETS pygmx_core DESTINATION ${PYGMX_INSTALL_DIR}/gmx
		COMPONENT python_module)

# TODO:
# Allow build and installation via setuptools from files configured by CMake.
#
# For user installation of a freshly built gmx module, we need to copy the right
# source files, configure setup.py, and provide a directory from which the user
# can run `pip install`.
# To do: we should probably check somehow that the version of pip matches the
# configured Python executable.

# Perform CMake variable substitution
#configure_file(
#    "${CMAKE_CURRENT_SOURCE_DIR}/setup.py.in"
#    "${CMAKE_BINARY_DIR}/setup.py"
#)
