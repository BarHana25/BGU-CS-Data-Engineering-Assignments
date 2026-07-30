cmake_minimum_required(VERSION 4.0)
project(_3 C)

set(CMAKE_C_STANDARD 11)

include_directories(.)

add_executable(_3
        BattleByCategory.h
        Defs.h
        LinkedList.c
        LinkedList.h
        MaxHeap.c
        MaxHeap.h
        Pokemon.c
        Pokemon.h
        PokemonsBattleCenter.c
        BattleByCategory.c)

