//
// Created by Bar Hana Yehezkel on 21/11/2025.
//

#include "Pokemon.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Pokemon *createPokemon(const char *name, const char *species, PokemonType type, PokemonBio bio)
{
    Pokemon *p = malloc(sizeof(Pokemon));
    if ( p == NULL )
    {
        return NULL;
    }
    //Allocate and copy name
    p->name = malloc(strlen(name) + 1);
    if ( p->name == NULL )
    {
        free(p);
        return NULL;
    }
    strcpy(p->name, name);
    //Allocate and copy species
    p->species = malloc(strlen(species) + 1);
    if ( p->species == NULL )
    {
        free(p->name);
        free(p);
        return NULL;
    }
    strcpy(p->species, species);
    //Copy type and bio by value
    p->type = type;
    p->bio = bio;
    return p;
}

PokemonType *createPokemonType( const char *type_name)
{  PokemonType *p_t = malloc(sizeof(PokemonType));
    if ( p_t == NULL )
    {
        return NULL;
    }

    p_t->type_name = malloc(strlen(type_name) + 1);
    if ( p_t->type_name == NULL )
    {
        free(p_t);
        return NULL;
    }
    strcpy(p_t->type_name, type_name);
    //We don't do malloc for arrays yet because there is no type in lists yet
    p_t->effective_against_me = NULL;
    p_t->number_of_effective_against_me = 0;
    p_t->effective_against_others = NULL;
    p_t->number_of_effective_against_others = 0;
    p_t->number_of_poke_from_type = 0;

    return p_t;
}

PokemonBio createPokemonBio(double height, double weight, int attack)
{
PokemonBio p_b;
    p_b.height = height;
    p_b.weight = weight;
    p_b.attack = attack;
    return p_b;
}

Result addEffectiveAgainstMe(PokemonType *p1_t, const PokemonType *p2_t)
{
    if (p1_t  == NULL || p2_t == NULL)
    {
        return failure;
    }
    //Check if relation already exists
    for (int i = 0; i < p1_t->number_of_effective_against_me; i++)
    {
        if (p1_t->effective_against_me[i].type_name ==p2_t->type_name)
        {
            return failure;
        }
    }
    int new_effective_against_me = p1_t->number_of_effective_against_me +1;
    //Array to hold one more type
    PokemonType *temp = realloc(p1_t->effective_against_me, (size_t)new_effective_against_me * sizeof(PokemonType));
    if (temp == NULL)
    {
        return out_of_memory;
    }
    p1_t->effective_against_me = temp;
    p1_t->effective_against_me[p1_t->number_of_effective_against_me] = *p2_t;
    p1_t->number_of_effective_against_me = new_effective_against_me;
    return success;
}

Result addEffectiveAgainstOthers(PokemonType *p1_t, const PokemonType *p2_t)
{
    if (p1_t == NULL || p2_t == NULL)
    {
        return failure;
    }
    //Check if relation already exists
    for (int i = 0; i < p1_t->number_of_effective_against_others; i++)
    {
        if (strcmp(p1_t->effective_against_others[i].type_name, p2_t->type_name) == 0)
        {
            return failure;
        }
    }
    int new_effective_against_others = p1_t->number_of_effective_against_others +1;
    //Array to hold one more type
    PokemonType *temp = realloc(p1_t->effective_against_others, (size_t)new_effective_against_others * sizeof(PokemonType));
    if (temp == NULL)
    {
        return out_of_memory;
    }
    p1_t->effective_against_others = temp;
    p1_t->effective_against_others[p1_t->number_of_effective_against_others] = *p2_t;
    p1_t->number_of_effective_against_others = new_effective_against_others;
    return success;
}
int findType(const PokemonType *p_t, int size, const char *type_name)
{
    if (p_t == NULL || type_name == NULL)
    {
        return -1;
    }
    for (int i = 0; i < size; i++)
    {
        if (strcmp(p_t[i].type_name, type_name) == 0)
        {
            return i;
        }
    }
    return -1;
}
Result deleteFromAffectiveAgainstMe(PokemonType *p1_t, const PokemonType *p2_t)
{

    if (p1_t == NULL || p1_t->number_of_effective_against_me == 0 || p1_t->effective_against_me == NULL || p2_t == NULL)
    {
        return failure;
    }
    int type_i = findType(p1_t->effective_against_me, p1_t->number_of_effective_against_me, p2_t->type_name);
    if (type_i == -1)
    {
        return failure;
    }
    //Shift elements left to fill the gap
    for (int i = type_i; i < p1_t->number_of_effective_against_me - 1; i++)
    {
        p1_t->effective_against_me[i] = p1_t->effective_against_me[i + 1];
    }
    p1_t->number_of_effective_against_me--;
    //If no elements left, free the array
    if (p1_t->number_of_effective_against_me == 0)
    {
        free(p1_t->effective_against_me);
        p1_t->effective_against_me = NULL;
        return success;
    }
    //Shrink allocation to the new size
    PokemonType *temp = realloc(p1_t->effective_against_me, (size_t)p1_t->number_of_effective_against_me * sizeof(PokemonType));
    if (temp == NULL)
    {
    return out_of_memory;
    }
    p1_t->effective_against_me = temp;
    return success;
}

Result deleteFromAffectiveAgainstOthers(PokemonType *p1_t, const PokemonType *p2_t)
{
    if (p1_t == NULL || p1_t->number_of_effective_against_others == 0 || p1_t->effective_against_others == NULL || p2_t == NULL)
    {
        return failure;
    }
    int type_i = findType(p1_t->effective_against_others, p1_t->number_of_effective_against_others, p2_t->type_name);
    if (type_i == -1)
    {
        return failure;
    }
    //Shift elements left to fill the gap
    for (int i = type_i; i < p1_t->number_of_effective_against_others - 1; i++)
    {
        p1_t->effective_against_others[i] = p1_t->effective_against_others[i + 1];
    }
    p1_t->number_of_effective_against_others--;
    if (p1_t->number_of_effective_against_others == 0)
    {
        free(p1_t->effective_against_others);
        p1_t->effective_against_others = NULL;
        return success;
    }
    //Shrink allocation to the new size
    PokemonType *temp = realloc(p1_t->effective_against_others, (size_t)p1_t->number_of_effective_against_others * sizeof(PokemonType));
    if (temp == NULL)
    {
        return out_of_memory;
    }
    p1_t->effective_against_others = temp;
    return success;
}

Result printPokemon( const Pokemon *p)
{
if (p == NULL)
{
    return failure;
}
if (p->name == NULL || p->type.type_name == NULL)
{
    return failure;
}
    printf("%s :\n", p->name);
    printf("%s, %s Type.\n", p->species, p->type.type_name);
    printf("Height: %.2f m    Weight: %.2f kg    Attack: %d\n\n", p->bio.height, p->bio.weight, p->bio.attack);
    return success;
}

Result printPokemonType( const PokemonType *p_t)
{
    if (p_t == NULL)
    {
        return failure;
    }
    printf("Type %s -- %d pokemons\n", p_t->type_name, p_t->number_of_poke_from_type);
    if (p_t->number_of_effective_against_me > 0)
    {
        printf("\tThese types are super-effective against %s:", p_t->type_name);
        for (int i = 0; i < p_t->number_of_effective_against_me; i++)
        {
            PokemonType *curr = &p_t->effective_against_me[i];
            if (i == 0)
            {
                printf("%s", curr->type_name);
            }
            else
            {
                printf(" ,%s", curr->type_name);
            }
        }
        printf("\n");
    }
    if (p_t->number_of_effective_against_others > 0)
    {
        printf("\t%s moves are super-effective against:", p_t->type_name);
        for (int i = 0; i < p_t->number_of_effective_against_others; i++)
         {
            PokemonType *curr = &p_t->effective_against_others[i];
            if (i == 0)
            {
                printf("%s", curr->type_name);
            }
            else
            {
                printf(" ,%s", curr->type_name);
            }
         }
        printf("\n");
    }
    printf("\n");
    return success;
}

Result destroyPokemon(Pokemon *p)
{
    if (p == NULL)
    {
        return failure;
    }
    free(p->name);
    free(p->species);
    free(p);
    return success;
}
Result destroyPokemonType(PokemonType *p_t)
{
    if (p_t == NULL)
    {
        return failure;
    }
    free(p_t->type_name);
    free(p_t->effective_against_me);
    free(p_t->effective_against_others);
    free(p_t);
    return success;
}
