file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/gmx/data)

configure_file(__init__.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(context.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(data.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(exceptions.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(fileio.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(status.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(system.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(util.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)
configure_file(workflow.py ${CMAKE_BINARY_DIR}/gmx/ COPYONLY)

configure_file(data/topol.tpr ${CMAKE_BINARY_DIR}/gmx/data/ COPYONLY)

configure_file(version.in ${CMAKE_BINARY_DIR}/gmx/version.py @ONLY)

file(COPY test DESTINATION ${CMAKE_BINARY_DIR}/gmx/)

# Todo: we need a target dependent on these files to force fresh configure / copy and to do python -m compileall
# for the install target.

install(DIRECTORY ${CMAKE_BINARY_DIR}/gmx/
        DESTINATION ${GMXAPI_INSTALL_PATH}
        FILES_MATCHING PATTERN "*.py" PATTERN "*.ini"
        )

install(DIRECTORY ${CMAKE_BINARY_DIR}/gmx/data
        DESTINATION ${GMXAPI_INSTALL_PATH})

add_subdirectory(core)
