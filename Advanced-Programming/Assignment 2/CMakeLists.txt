cmake_minimum_required(VERSION 4.0)
project(Pokemon1 C)

set(CMAKE_C_STANDARD 11)

include_directories(.)

add_executable(Pokemon1
        Defs.h
        Pokedex.c
        Pokemon.c
        Pokemon.h)
