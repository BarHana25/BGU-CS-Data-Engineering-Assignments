//
// Created by Bar Hana Yehezkel on 21/11/2025.
//

#ifndef POKEMON_H
#define POKEMON_H

#include "Defs.h"

/*
 * Represents a Pokemon type (e.g. Fire, Water).
 *
 * type_name – the type's name.
 * effective_against_me – types that are strong against this type.
 * number_of_effective_against_me – how many such types there are.
 * effective_against_others – types this type is strong against.
 * number_of_effective_against_others – how many such types there are.
 * number_of_poke_from_type – how many Pokemon of this type exist.
 */
typedef struct PokemonType {
    char *type_name;
    struct PokemonType *effective_against_me;
    int number_of_effective_against_me;
    struct PokemonType *effective_against_others;
    int number_of_effective_against_others;
    int number_of_poke_from_type;
} PokemonType;
/*
 * Holds basic bio data about a Pokemon.
 *
 * height – the Pokemon's height.
 * weight – the Pokemon's weight.
 * attack – the Pokemon's attack value.
 */
typedef struct PokemonBio {
    double height;
    double weight;
    int attack;
} PokemonBio;
/*
 * Represents a Pokemon in the system.
 *
 * name – the Pokemon's name.
 * species – the Pokemon's species.
 * type – the Pokemon's type (e.g. Fire, Water).
 * bio – biological data about the Pokemon.
 */
typedef struct Pokemon {
    char *name;
    char *species;
    PokemonType type;
    PokemonBio bio;
} Pokemon;
/*
 * Creates a new Pokemon on the heap.
 *
 * name    – the Pokemon's name (copied).
 * species – the Pokemon's species (copied).
 * type    – the Pokemon's type.
 * bio     – basic biological data of the Pokemon.
 *
 * Returns:
 *   Pointer to a newly allocated Pokemon on success,
 *   or NULL if memory allocation fails.
 */
Pokemon *createPokemon( char *name, char *species, PokemonType type, PokemonBio bio);
/*
 * Creates a new PokemonType on the heap.
 *
 * type_name – the name of the type (copied into the struct).
 *
 * All arrays (effective_against_me / effective_against_others)
 * are initialized to NULL and their counters to 0.
 * number_of_poke_from_type is also initialized to 0.
 *
 * Returns:
 *   Pointer to a newly allocated PokemonType on success,
 *   or NULL if memory allocation fails.
 */
PokemonType *createPokemonType( char *type_name);
/*
 * Creates a PokemonBio value with the given data.
 *
 * height – Pokemon's height.
 * weight – Pokemon's weight.
 * attack – Pokemon's attack value.
 *
 * Returns:
 *   A PokemonBio struct initialized with these values.
 */
PokemonBio createPokemonBio(double height, double weight, int attack);
/*
 * Adds p2_t to p1_t's "effective against me" list if it is not already there.
 * Returns success, failure (invalid args / already exists), or out_of_memory.
 */
status addEffectiveAgainstMe(PokemonType *p1_t, PokemonType *p2_t);
/*
 * Adds p2_t to p1_t's "effective against others" list if it is not already there.
 * Returns success, failure (invalid args / already exists), or out_of_memory.
 */
status addEffectiveAgainstOthers(PokemonType *p1_t, PokemonType *p2_t);
/*
 * Prints all data of a single Pokemon in a formatted way.
 * Returns success on success, or failure if p is NULL or missing mandatory fields.
 */
status printPokemon( Pokemon *p);
/*
 * Prints information about a PokemonType:
 * its name, number of pokemons, and effectiveness lists (if not empty).
 * Returns success, or failure if p_t is NULL.
 */
status printPokemonType( PokemonType *p_t);
/*
 * Frees all memory of a single Pokemon (name, species, and the struct itself).
 * Returns success, or failure if p is NULL.
 */
status destroyPokemon(Pokemon *p);
/*
 * Frees all memory of a PokemonType:
 * the type_name string, both effectiveness arrays, and the struct itself.
 * Returns success, or failure if p_t is NULL.
 */
status destroyPokemonType(PokemonType *p_t);

#endif //POKEMON_H
