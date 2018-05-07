# Sourcing GMXRC from a GROMACS installation should allow discovery of exported CMake config to import `libgmxapi` target.
# If the libgmxapi dependency is satisfied by allowing setuptools to build GROMACS, it should use GROMACS_DIR to hint
# the location.
#
# find_package should find gmxapiConfig.cmake if the path to `gmx` is in PATH,
# if gmxapi_DIR is set to the GROMACS installation directory, or if
# cmake was invoked with `-DCMAKE_PREFIX_PATH=...` pointing to the GROMACS
# installation directory. We can also check now for a GROMACS_DIR environment
# variable and provide it with the HINTS option.
find_package(gmxapi 0.0.6 REQUIRED
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

include(GNUInstallDirs)

# workaround for relocated package when installing nested gromacs on readthedocs.org
if(DEFINED ENV{READTHEDOCS} OR DEFINED ENV{BUILDGROMACS})
    if(UNIX AND NOT APPLE)
        set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH "$ORIGIN/data/gromacs/${CMAKE_INSTALL_LIBDIR}")
    elseif(APPLE)
        set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH "@loader_path/data/gromacs/${CMAKE_INSTALL_LIBDIR}")
    endif()
endif()
set_target_properties(pygmx_core PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

install(TARGETS pygmx_core
        LIBRARY DESTINATION
        ${CMAKE_INSTALL_PREFIX}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_PREFIX}
        RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX})
