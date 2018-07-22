cmake_minimum_required(VERSION 3.4.3)

# CMake modules/macros are in a subdirectory to keep this file cleaner
# This needs to be set before project() in order to pick up toolchain files
#list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# Sets the PROJECT_VERSION variable, as well...
project(gmxpy VERSION 0.0.6)

# Only interpret if() arguments as variables or keywords when unquoted.
cmake_policy(SET CMP0054 NEW)
include(Ccache.cmake)

# If the user is not in a virtual environment and is not a privileged user and has not specified an install location
# for the Python module (GMXAPI_INSTALL_PATH), this option causes the automatic install location to query the user
# site-packages directory instead of using the default site-packages directory for the interpreter.
option(GMXAPI_USER_INSTALL "Override the default site-packages directory with the user-specific Python packages directory. \
       (Do not use with virtual environments.) \
       Has no effect if GMXAPI_INSTALL_PATH is defined or cached. \
       Use -UGMXAPI_INSTALL_PATH to force recalculation." OFF)

# Since a user may have multiple virtual environments with different Python interpreters, it is generally confusing to
# have a package for a virtual environment installed in the user's default user site-packages directory.

unset(PYTHONINTERP_FOUND)
unset(PYTHONLIBS_FOUND)
# This will get cleaner with FindPython in CMake 3.12 and higher. We're a ways from requiring that, but
# we can add logic for it soon to be ready.
find_package(PythonInterp)
if (PYTHONINTERP_FOUND)
    message(STATUS "Found Python interpreter: ${PYTHON_EXECUTABLE}")
    find_package(PythonLibs ${PYTHON_VERSION_STRING} EXACT)
    if (PYTHONLIBS_FOUND)
        if (GMXAPI_USER_INSTALL)
            execute_process(COMMAND ${PYTHON_EXECUTABLE} "-m" "site" "--user-site" OUTPUT_VARIABLE GMXAPI_DEFAULT_SITE_PACKAGES OUTPUT_STRIP_TRAILING_WHITESPACE)
            message(STATUS "Python user site-packages directory is ${GMXAPI_DEFAULT_SITE_PACKAGES}")
        else()
            execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import sys; import os; print(os.path.abspath(os.path.join(sys.prefix, 'lib', 'python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}', 'site-packages')))" OUTPUT_VARIABLE GMXAPI_DEFAULT_SITE_PACKAGES OUTPUT_STRIP_TRAILING_WHITESPACE)
            message(STATUS "Python site-packages directory is ${GMXAPI_DEFAULT_SITE_PACKAGES}")
        endif()
    else()
        message(FATAL_ERROR "Found Python interpreter ${PYTHON_EXECUTABLE} but this Python installation does not have developer tools."
                "Set PYTHON_EXECUTABLE to the Python interpreter that was installed with a working Python.h header file.")
    endif()
else()
    message(FATAL_ERROR "Could not find Python interpreter. Set CMake flag -DPYTHON_EXECUTABLE=/path/to/python to hint.")
endif()

# At some point this may be part of a CMake package with several components for which a single CMAKE_INSTALL_PREFIX does
# not make sense, so let's manage the install path separately.
set(GMXAPI_INSTALL_PATH ${GMXAPI_DEFAULT_SITE_PACKAGES}/gmx CACHE PATH
    "Path to Python module install location (site-packages). For an automatically determined install location based on \
    the Python installation, leave undefined or explicitly undefined with -UGMXAPI_INSTALL_PATH and, optionally, set \
    GMXAPI_USER_INSTALL on or off to specify the installation's site-packages directory or the 'user' site-packages \
    directory.")

message(STATUS "Python module will be installed to GMXAPI_INSTALL_PATH cache value ${GMXAPI_INSTALL_PATH}")

add_subdirectory(pybind11)

add_subdirectory(src/gmx)

add_subdirectory(docs)
