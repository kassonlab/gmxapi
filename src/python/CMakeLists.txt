# Set the rpath of the
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

pybind11_add_module(core gmx_core.cpp)
target_link_libraries(core PRIVATE libgromacs)

# use, i.e. don't skip the full RPATH for the build tree
set_target_properties(core PROPERTIES SKIP_BUILD_RPATH FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
set_target_properties(core PROPERTIES BUILD_WITH_INSTALL_RPATH FALSE)
set_target_properties(core PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${LIB_INSTALL_DIR}")
set_target_properties(core PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

# Install target should copy Python source files into lib/python{version}/gmx
# and properly install core.so into same.

# Create the 'install' target, which is different than the setuptools
# installation location.
set(PYGMX_INSTALL_DIR ${LIB_INSTALL_DIR}/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR} CACHE PATH "Installation directory for python module")
install(DIRECTORY "gmx" DESTINATION ${PYGMX_INSTALL_DIR})
install(CODE "MESSAGE(\"Python module installed to ${CMAKE_INSTALL_PREFIX}/${PYGMX_INSTALL_DIR}.
You will need to update your PYTHONPATH environment variable for python to find it.\")")
# The compiled core module is a submodule of the 'gmx' package.
install(TARGETS core DESTINATION ${PYGMX_INSTALL_DIR}/gmx)

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
