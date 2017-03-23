pybind11_add_module(core gmx_core.cpp)
target_link_libraries(core PRIVATE libgromacs)

# use, i.e. don't skip the full RPATH for the build tree
set_target_properties(core PROPERTIES SKIP_BUILD_RPATH FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
set_target_properties(core PROPERTIES BUILD_WITH_INSTALL_RPATH FALSE)
set_target_properties(core PROPERTIES INSTALL_RPATH "${LIB_INSTALL_DIR}")
