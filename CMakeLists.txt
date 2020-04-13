cmake_minimum_required(VERSION 3.5)
set(CMAKE_VERBOSE_MAKEFILE ON CACHE BOOL "ON")

set(FREE5GC_VERSION "v2")
set(UPF_CMAKE_BUILD_TYPE "Debug")

find_program(Docker_EXECUTABLE docker)
if(NOT Docker_EXECUTABLE)
    message(FATAL_ERROR "Cannot find the docker executable!")
endif()

add_custom_target(free5gc_img ALL
    COMMAND
        ${Docker_EXECUTABLE} build
            --tag free5gc:${FREE5GC_VERSION}
            --build-arg UPF_CMAKE_BUILD_TYPE=${UPF_CMAKE_BUILD_TYPE}
            --build-arg FREE5GC_FETCH=${FREE5GC_FETCH}
            --file ${CMAKE_CURRENT_LIST_DIR}/Dockerfile
            ${CMAKE_CURRENT_LIST_DIR}
    VERBATIM
)

add_custom_target(netgraph_img ALL
    COMMAND
        ${Docker_EXECUTABLE} build
            --tag netgraph
            --file ${CMAKE_CURRENT_LIST_DIR}/netgraph/Dockerfile
            ${CMAKE_CURRENT_LIST_DIR}/netgraph
    VERBATIM
)
