if(NOT DEFINED STDLIB_MAKE_UNIQUE)
    execute_process(COMMAND ${CMAKE_COMMAND} -E echo_append "-- Checking for std::make_unique(): ")
    # Language standard arguments are required before CMake 3.8 or if CMP0067 set to "OLD"
    try_compile(TEST_MAKE_UNIQUE
                ${CMAKE_CURRENT_BINARY_DIR}
                ${CMAKE_CURRENT_LIST_DIR}/test_make_unique.cpp
                OUTPUT_VARIABLE _output
                CXX_STANDARD 14
                CXX_STANDARD_REQUIRED ON
            )
    if(TEST_MAKE_UNIQUE)
        execute_process(COMMAND ${CMAKE_COMMAND} -E echo "found")
        set(STDLIB_MAKE_UNIQUE
            ${TEST_MAKE_UNIQUE} CACHE INTERNAL
            "Whether std::make_unique is available.")
    else()
        execute_process(COMMAND ${CMAKE_COMMAND} -E echo " NOT FOUND")
        message(STATUS ${_output})
    endif()
    unset(_output)
    unset(TEST_MAKE_UNIQUE)
endif()
