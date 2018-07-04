# Reference https://crascit.com/2016/04/09/using-ccache-with-cmake/
#
# Here we try to make sure that ccache is invoked as `/.../ccache compiler args` to best handle more than one local
# compiler or a compiler wrapper, whereas it is otherwise common to replace the default compilers with symbolic links
# to the ccache binary.
#
# ccache only works for gcc compatible compilers. We should test with anything other than CMAKE_<LANG>_COMPILER_ID==GNU
# Clang is reported to work with some caveats. See https://pspdfkit.com/blog/2015/ccache-for-fun-and-profit/
# AppleClang
# Clang
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    # Set up wrapper scripts
    if (CMAKE_C_COMPILER_ID MATCHES "GNU" OR CMAKE_C_COMPILER_ID MATCHES "AppleClang" OR CMAKE_C_COMPILER_ID MATCHES "Clang")
        message(STATUS "Setting up ccache wrapper for ${CMAKE_C_COMPILER_ID} C compiler ${CMAKE_C_COMPILER}")
        set(C_LAUNCHER "${CCACHE_PROGRAM}")
        configure_file(launch-c.in ${CMAKE_BINARY_DIR}/launch-c)
        execute_process(COMMAND chmod a+rx "${CMAKE_BINARY_DIR}/launch-c")
        if(CMAKE_GENERATOR STREQUAL "Xcode")
            # Set Xcode project attributes to route compilation and linking
            # through our scripts
            set(CMAKE_XCODE_ATTRIBUTE_CC "${CMAKE_BINARY_DIR}/launch-c")
            set(CMAKE_XCODE_ATTRIBUTE_LD "${CMAKE_BINARY_DIR}/launch-c")
        else()
            # Support Unix Makefiles and Ninja
            set(CMAKE_C_COMPILER_LAUNCHER "${CMAKE_BINARY_DIR}/launch-c")
        endif()
    else()
        message(STATUS "Skipping ccache set up. Not confirmed to work with compiler ID ${CMAKE_C_COMPILER_ID}.")
    endif() # GNU C compiler
    if (CMAKE_C_COMPILER_ID MATCHES "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "AppleClang" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        message(STATUS "Setting up ccache wrapper for ${CMAKE_CXX_COMPILER_ID} CXX compiler ${CMAKE_CXX_COMPILER}")
        set(CXX_LAUNCHER "${CCACHE_PROGRAM}")
        configure_file(launch-cxx.in ${CMAKE_BINARY_DIR}/launch-cxx)
        execute_process(COMMAND chmod a+rx "${CMAKE_BINARY_DIR}/launch-cxx")

        if(CMAKE_GENERATOR STREQUAL "Xcode")
            # Set Xcode project attributes to route compilation and linking
            # through our scripts
            set(CMAKE_XCODE_ATTRIBUTE_CXX        "${CMAKE_BINARY_DIR}/launch-cxx")
            set(CMAKE_XCODE_ATTRIBUTE_LDPLUSPLUS "${CMAKE_BINARY_DIR}/launch-cxx")
        else()
            # Support Unix Makefiles and Ninja
            set(CMAKE_CXX_COMPILER_LAUNCHER "${CMAKE_BINARY_DIR}/launch-cxx")
        endif()
    else()
        message(STATUS "Skipping ccache set up. Not confirmed to work with compiler ID ${CMAKE_CXX_COMPILER_ID}.")
    endif() # GNU C++ compiler
endif() # ccache program
