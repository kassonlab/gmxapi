configure_file(version.in ${CMAKE_BINARY_DIR}/gmx/version.py @ONLY)

add_subdirectory(core)

# Everything that needs to get installed that isn't installed with install(TARGET...)
set(_pure_sources
        __init__.py
        context.py
        data.py
        exceptions.py
        fileio.py
        status.py
        system.py
        util.py
        workflow.py
        )
set(_test_sources
        test/pytest.ini
        test/conftest.py
        test/test_context.py
        test/test_docstrings.py
        test/test_exceptions.py
        test/test_fileio.py
        test/test_gmx.py
        test/test_mpiarraycontext.py
        test/test_pymd.py
        test/test_workflow.py
        )
set(_data_sources
        data/topol.tpr
        )
set(GMXAPI_PY_STATIC_FILENAMES ${_pure_sources} ${_test_sources} ${_data_sources}
        PARENT_SCOPE
        )
set(GMXAPI_PY_GENERATED_FILENAMES
        version.py
        PARENT_SCOPE
        )

# TRANSFORM available in CMake 3.12
#list(TRANSFORM GMXAPI_PY_STATIC_FILENAMES PREPEND "${CMAKE_CURRENT_SOURCE_DIR}/" GMXAPI_PY_STATIC_SOURCES)
#list(TRANSFORM GMXAPI_PY_GENERATED_FILENAMES PREPEND "${CMAKE_CURRENT_BINARY_DIR}/" GMXAPI_GENERATED_SOURCES)

install(FILES ${_pure_sources}
        DESTINATION ${GMXAPI_INSTALL_PATH}
        )
install(FILES ${CMAKE_BINARY_DIR}/gmx/version.py
        DESTINATION ${GMXAPI_INSTALL_PATH}
        )
install(FILES ${_test_sources}
        DESTINATION ${GMXAPI_INSTALL_PATH}/test
        )
install(FILES ${_data_sources}
        DESTINATION ${GMXAPI_INSTALL_PATH}/data
        )
