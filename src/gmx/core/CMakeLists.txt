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


# Sourcing GMXRC from a GROMACS installation should allow discovery of exported CMake config to import `libgmxapi` target.
# If the libgmxapi dependency is satisfied by allowing setuptools to build GROMACS, it should use GROMACS_DIR to hint
# the location.
#
# find_package should find gmxapiConfig.cmake if the path to `gmx` is in PATH,
# if gmxapi_DIR is set to the GROMACS installation directory, or if
# cmake was invoked with `-DCMAKE_PREFIX_PATH=...` pointing to the GROMACS
# installation directory. We can also check now for a GROMACS_DIR environment
# variable and provide it with the HINTS option.
find_package(gmxapi 0.0.4 REQUIRED
             HINTS "$ENV{GROMACS_DIR}"
             )

# Build the C++ extension

pybind11_add_module(pygmx_core
                    core.h
					core.cpp
					export_context.cpp
					export_md.cpp
					export_system.cpp
					gmxpy_api.h
					pymdmodule.h
					pymdmodule.cpp
					pysystem.h
					pysystem.cpp
					)

# The target name is for clarity, but the installed module will be gmx.core
set_target_properties(pygmx_core PROPERTIES OUTPUT_NAME core)


#set(PYGMX_DIRECTORY "${CMAKE_INSTALL_PREFIX}"
#    CACHE PATH "Full path to the gmx module installation")

# Set the output to the staging area
# For installs that are part of a GROMACS install, we probably want to stage differently
# set_target_properties(
#    pygmx_core
#    PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${PYGMX_DIRECTORY}")

target_include_directories(pygmx_core PRIVATE
	${CMAKE_CURRENT_SOURCE_DIR}
	${CMAKE_CURRENT_BINARY_DIR}
	)

# RPATH management
#set(PYGMX_RPATH "${CMAKE_INSTALL_PREFIX}/${LIB_INSTALL_DIR}" CACHE PATH
#    "Set to override RPATH for Python C++ extension (as by setuptools)")
#mark_as_advanced(PYGMX_RPATH)
# don't skip the full RPATH for the build tree
set_target_properties(pygmx_core PROPERTIES SKIP_BUILD_RPATH FALSE)

# (but later on when installing)
# If building with setuptools, CMake will not be performing the install
set_target_properties(pygmx_core PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
#set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH ${PYGMX_RPATH})

target_link_libraries(pygmx_core PRIVATE Gromacs::gmxapi)

# workaround for relocated package when installing nested gromacs on readthedocs.org
if(DEFINED ENV{READTHEDOCS} OR DEFINED ENV{BUILDGROMACS})
	if(UNIX AND NOT APPLE)
    	set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH "$ORIGIN/data/gromacs/lib/")
	elseif(APPLE)
		set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH "@loader_path/data/gromacs/lib")
	endif()
endif()
set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

install(TARGETS pygmx_core
		LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}
		ARCHIVE DESTINATION ${CMAKE_INSTALL_PREFIX}
		RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}
		)
