cmake_minimum_required(VERSION 3.10)
project(GenesisBridge)

set(CMAKE_CXX_STANDARD 17)

# Attempt to find pybind11
find_package(pybind11 REQUIRED)

pybind11_add_module(genesis_bridge genesis_bridge.cpp)
