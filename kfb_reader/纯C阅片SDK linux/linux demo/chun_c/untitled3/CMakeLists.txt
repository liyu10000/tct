project(untitled3)
cmake_minimum_required(VERSION 2.8)
aux_source_directory(. SRC_LIST)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/Debug)
set(CMAKE_C_FLAGS "-ldl")
add_executable(${PROJECT_NAME} ${SRC_LIST})

