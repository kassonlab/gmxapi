cmake_minimum_required(VERSION 3.4.3)

# CMake modules/macros are in a subdirectory to keep this file cleaner
# This needs to be set before project() in order to pick up toolchain files
#list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# Sets the PROJECT_VERSION variable, as well...
project(gmxpy VERSION 0.0.4)

add_subdirectory(pybind11)

add_subdirectory(src/gmx/core)
