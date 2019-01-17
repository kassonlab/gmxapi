# Sourcing GMXRC from a GROMACS installation should allow discovery of exported CMake config to import `libgmxapi` target.
# If the libgmxapi dependency is satisfied by allowing setuptools to build GROMACS, it should use GROMACS_DIR to hint
# the location.
#
# find_package should find gmxapiConfig.cmake if the path to `gmx` is in PATH,
# if gmxapi_DIR is set to the GROMACS installation directory, or if
# cmake was invoked with `-DCMAKE_PREFIX_PATH=...` pointing to the GROMACS
# installation directory. We can also check now for a GROMACS_DIR environment
# variable and provide it with the HINTS option.
find_package(gmxapi 0.0.8 REQUIRED
        HINTS "$ENV{GROMACS_DIR}"
        )
if(gmxapi_FOUND)
    set(_suffix "")
    # GROMACS master branch and forked development branches may have divergent
    # pre-release APIs. This check allows us to distinguish them and behave
    # differently if needed. github.com/kassonlab/gromacs-gmxapi devel branch
    # sets gmxapi_EXPERIMENTAL=TRUE. Upstream GROMACS master branch does not.
    # Ref: https://github.com/kassonlab/gmxapi/issues/166
    if(gmxapi_EXPERIMENTAL)
        set(_suffix " (unofficial)")
    endif()
    message(STATUS "Found gmxapi version ${gmxapi_VERSION}${_suffix}")
endif()

add_subdirectory(gmx)

##################
# Create dist-info
##################

# Note: this may not be PEP-376 compliant, but it does the trick for now.
# In the future, we might migrate to scikit-build or at least use more Python
# utilities to generate the packaging information.

option(GMXAPI_DISTINFO
        "Create a Python dist-info directory so that setuptools can see the package is installed.\
        Set this `OFF` if generating an 'egg' with `pip` or `setup.py`."
        ON)
mark_as_advanced(GMXAPI_DISTINFO)

# Make a copy of the source list to prepare the dist-info RECORD
# TRANSFORM available in CMake 3.12
#list(TRANSFORM GMXAPI_PY_STATIC_FILENAMES PREPEND "gmx/" GMXAPI_PY_STATIC_INSTALLED)
#list(TRANSFORM GMXAPI_PY_GENERATED_FILENAMES PREPEND "gmx/" GMXAPI_GENERATED_INSTALLED)
set(GMXAPI_PY_STATIC_INSTALLED)
foreach(_name ${GMXAPI_PY_STATIC_FILENAMES})
    string(APPEND GMXAPI_PY_STATIC_INSTALLED "gmx/${_name}\n")
endforeach()

set(GMXAPI_GENERATED_INSTALLED)
foreach(_name ${GMXAPI_PY_GENERATED_FILENAMES})
    string(APPEND GMXAPI_GENERATED_INSTALLED "gmx/${_name}\n")
endforeach()

# This should be more automatically generated (from setup.py)
set(_METADATA "Metadata-Version: 2.1
Name: gmx
Version: ${PROJECT_VERSION}
Summary: GROMACS Python module
Home-page: https://github.com/kassonlab/gmxapi
Author: M. Eric Irrgang
Author-email: ericirrgang@gmail.com
License: LGPL
Platform: UNKNOWN
Requires-Python: >=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4
Requires-Dist: setuptools (>=28)
Requires-Dist: scikit-build
Requires-Dist: cmake
Requires-Dist: networkx
")

# Write the dist-info files
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info)
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/INSTALLER
        "cmake")
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/METADATA
        ${_METADATA})
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/REQUESTED
        "")

file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD.in
        ${GMXAPI_PY_STATIC_INSTALLED})
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD.in
        ${GMXAPI_GENERATED_INSTALLED})

# These gymnastics try to deal with dependencies of and on generated files.
# For some enlightening discussion, refer to
# https://samthursfield.wordpress.com/2015/11/21/cmake-dependencies-between-targets-and-files-and-custom-commands/
# and
# https://crascit.com/2017/04/18/generated-sources-in-cmake-builds/
# In the future, we should probably stick to either CMake or scikit-build for
# build and install.

add_custom_target(always_update
    COMMAND
        cmake -E echo
    SOURCES
        ${GMXAPI_PY_STATIC_SOURCES}
        ${GMXAPI_PY_GENERATED_SOURCES}
        ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD.in
        )

add_custom_command(
    OUTPUT
        ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
    COMMAND
        cmake -E copy ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD.in
            ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
    COMMAND
        cmake -E echo "gmx/$<TARGET_FILE_NAME:pygmx_core>" >>
            ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
    COMMAND
        cmake -E echo "gmx-${PROJECT_VERSION}.dist-info/INSTALLER" >>
            ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
    COMMAND
        cmake -E echo "gmx-${PROJECT_VERSION}.dist-info/METADATA" >>
            ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
    COMMAND
        cmake -E echo "gmx-${PROJECT_VERSION}.dist-info/RECORD" >>
            ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
    COMMAND
        cmake -E echo "gmx-${PROJECT_VERSION}.dist-info/REQUESTED" >>
            ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
    DEPENDS
        pygmx_core
        always_update
    VERBATIM
)

add_custom_target(make_distinfo_record ALL
    DEPENDS
        pygmx_core
        ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/INSTALLER
        ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/METADATA
        ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/RECORD
        ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info/REQUESTED
    )

if(GMXAPI_DISTINFO)
    install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gmx-${PROJECT_VERSION}.dist-info
            DESTINATION ${GMXAPI_INSTALL_PATH}/..
            PATTERN "*.in" EXCLUDE)
endif(GMXAPI_DISTINFO)
