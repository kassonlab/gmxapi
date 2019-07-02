# Build the C++ extension
include_directories(${PYTHON_INCLUDE_DIRS})

pybind11_add_module(pygmx_core
                    core.cpp
                    export_context.cpp
                    export_md.cpp
                    export_system.cpp
                    pycontext.cpp
                    export_tprfile.cpp
                    pymdmodule.cpp
                    pysystem.cpp
                    tprfile.cpp
                    )

# The target name is for clarity, but the installed module will be gmx.core
set_target_properties(pygmx_core PROPERTIES OUTPUT_NAME core)

set_target_properties(pygmx_core PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/gmx)

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
        LIBRARY DESTINATION ${GMXAPI_INSTALL_PATH}
        ARCHIVE DESTINATION ${GMXAPI_INSTALL_PATH}
        RUNTIME DESTINATION ${GMXAPI_INSTALL_PATH})
