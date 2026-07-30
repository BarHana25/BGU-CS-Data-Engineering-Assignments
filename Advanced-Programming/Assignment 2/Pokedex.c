//
// Created by Bar Hana Yehezkel on 21/11/2025.
//
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "Pokemon.h"
#include "Defs.h"

/*
 * Searches an array of PokemonType pointers for a type with the given name.
 * Returns a pointer to the type if found, or NULL otherwise.
 */
static  PokemonType *findTypeInArrOfArr(PokemonType **types, int num_of_types, const char *name);
/*
 * Prints the main menu with all available user options.
 */
void printMenu();
/*
 * Reads a line from stdin into buffer and checks if it is a valid integer.
 * On success, stores the value in *val and returns 1, otherwise returns 0.
 */
int readInt(int *val, char buffer[], int size);
/*
 * Reads a line from stdin into buffer and removes the trailing newline.
 * Returns 1 on success, or 0 on failure (EOF / error).
 */
static int readLine(char *buffer, int buffer_size);


// helper func
static  PokemonType *findTypeInArrOfArr(PokemonType **types, int num_of_types, const char *name)
{
    if (types == NULL || name == NULL)
    {
        return NULL;
    }
    for (int i = 0; i < num_of_types; i++)
    {
        if (strcmp(types[i]->type_name, name) == 0)
        {
            return types[i];
        }
    }
    return NULL;
}

void printMenu()
{
    printf("Please choose one of the following numbers:\n");
    printf("1 : Print all Pokemons\n");
    printf("2 : Print all Pokemons types\n");
    printf("3 : Add type to effective against me list\n");
    printf("4 : Add type to effective against others list\n");
    printf("5 : Remove type from effective against me list\n");
    printf("6 : Remove type from effective against others list\n");
    printf("7 : Print Pokemon by name\n");
    printf("8 : Print Pokemons by type\n");
    printf("9 : Exit\n");
}

int readInt(int *val, char buffer[], int size)
{
    if (fgets(buffer, size, stdin) == NULL)
    {
        return 0;
    }
    int i = 0;
    int seen_digit = 0;
    while (buffer[i] != '\0' && buffer[i] != '\n')
    {
        if (!isdigit((unsigned char)buffer[i]))
        {
            return 0;
        }
        seen_digit = 1;
        i++;
    }
    if (!seen_digit)
    {
        return 0;
    }
    *val = atoi(buffer);
    return 1;
}

static int readLine(char *buffer, int buffer_size)
{
    if (fgets(buffer, buffer_size, stdin) == NULL)
    {
        return 0;
    }
    buffer[strcspn(buffer, "\r\n")] = '\0';
    return 1;
}
//main start
int main( int num_of_arg, char *arr_str[])
{
    if (num_of_arg != 4)
    {
        return 1;
    }
    int num_of_types = atoi(arr_str[1]);
    int num_of_pokemon = atoi(arr_str[2]);
    char *file_name = arr_str[3];
    if (num_of_pokemon <= 0 || num_of_types <= 0)
    {
        printf("Invalid numbers in command line\n");
        return 1;
    }
    //Try to open configuration file
    FILE *file = fopen(file_name, "r");
    if (file == NULL)
    {
        printf("Can't open file %s\n", file_name);
        return 1;
    }
    //Allocate arrays for types and pokemons
    PokemonType **types = malloc((size_t)num_of_types * sizeof(PokemonType *));
    if (types == NULL)
    {
        printf("Memory Problem\n");
        fclose(file);
        return 1;
    }
    Pokemon **pokemons = malloc((size_t)num_of_pokemon * sizeof(Pokemon *));
    if (pokemons == NULL)
    {
        printf("Memory Problem\n");
        free(types);
        fclose(file);
        return 1;
    }
    for (int i = 0; i < num_of_pokemon; i++)
    {
        pokemons[i] = NULL;
    }
    char buffer[300];
    //Read Pokemon types from file
    fgets(buffer, 300, file); //skip first line
    fgets(buffer, 300, file); //types line

    int type_i = 0;
    char *type_name = strtok(buffer, ", \r\n");
    while (type_name != NULL && type_i < num_of_types)
    {
        PokemonType *new_type = createPokemonType(type_name);
        if (new_type == NULL)
        {
            printf("Memory Problem\n");
            for (int i = 0; i < type_i; i++)
            {
                destroyPokemonType(types[i]);
            }
            free(pokemons);
            free(types);
            fclose(file);
            return 1;
        }
        types[type_i] = new_type;
        type_i++;
        type_name = strtok(NULL, ", \r\n");
    }
    //Read type effectiveness section
    while (fgets(buffer, 300, file))
    {
        //Stop when we reach the "Pokemons" line
        if (strncmp(buffer, "Pokemons",8) == 0)
        {
            break;
        }
        //Skip empty lines
        if (buffer[0] == '\n'|| buffer[0] == '\r')
        {
            continue;
        }
        char me_name[300];
        sscanf(buffer, "%s", me_name);
        PokemonType *me_type = findTypeInArrOfArr(types, num_of_types, me_name);
        char *list_start = NULL;
        int e_f_me_or_other = 0; //me = 1, other = 2
        //Check which list this line describes
        list_start = strstr(buffer, "effective-against-me:");
        if (list_start != NULL)
        {
            e_f_me_or_other = 1;
            list_start += strlen("effective-against-me:");
        }
        else
        {
            list_start = strstr(buffer, "effective-against-other:");
            if (list_start != NULL)
            {
                e_f_me_or_other = 2;
                list_start += strlen("effective-against-other:");
            }
            else
            {
                continue;
            }
        }
        char *name_e_f_me_or_other = strtok(list_start, ", \r\n");
        while (name_e_f_me_or_other != NULL)
        {
            PokemonType *type_a_f_me_or_other = findTypeInArrOfArr(types, num_of_types, name_e_f_me_or_other);
            if (type_a_f_me_or_other != NULL)
            {
                Result r = success;
                if (e_f_me_or_other == 1)
                {
                    r = addEffectiveAgainstMe(me_type, type_a_f_me_or_other);
                }
                if (e_f_me_or_other == 2)
                {
                    r = addEffectiveAgainstOthers(me_type, type_a_f_me_or_other);
                }
                if (r == out_of_memory)
                {
                    printf("Memory Problem\n");
                    for (int i = 0; i < num_of_types; i++)
                    {
                        if (types[i] != NULL)
                        {
                            destroyPokemonType(types[i]);
                        }
                    }
                    free(pokemons);
                    free(types);
                    fclose(file);
                    return 1;
                }
            }
            name_e_f_me_or_other = strtok(NULL, ", \r\n");
        }
    }
    //Read Pokemons from file
    int poke_i = 0;
    while (poke_i < num_of_pokemon && fgets(buffer, 300, file))
    {
        if (buffer[0] == '\n' || buffer[0] == '\r')
        {
            continue;
        }
        char poke_name[300];
        char poke_specie[300];
        double height = 0.0;
        double weight = 0.0;
        int attack = 0;
        char poke_type[300];
        if (sscanf(buffer, "%[^,],%[^,],%lf,%lf,%d,%[^\r\n]", poke_name, poke_specie, &height, &weight, &attack, poke_type) != 6)
        {
            continue;
        }
        size_t name_len = strlen(poke_name);
        while (name_len > 0 && (poke_name[name_len - 1] == '\r' || poke_name[name_len - 1] == '\n' || poke_name[name_len - 1] == ' '))
        {
            poke_type[--name_len] = '\0';
        }
        PokemonType *def_poke_type = findTypeInArrOfArr(types, num_of_types, poke_type);
        if (def_poke_type == NULL)
        {
            continue;
        }
        PokemonBio bio;
        createPokemonBio(&bio, height, weight, attack);
        Pokemon *new_poke = createPokemon(poke_name, poke_specie, *def_poke_type, bio);
        if (new_poke == NULL)
        {
            printf("Memory Problem\n");
            for (int i = 0; i < poke_i; i++)
            {
                destroyPokemon(pokemons[i]);
            }
            for (int i = 0; i < num_of_types; i++)
            {
                destroyPokemonType(types[i]);
            }
            free(pokemons);
            free(types);
            fclose(file);
            return 1;
        }

        pokemons[poke_i] = new_poke;
        def_poke_type->number_of_poke_from_type++;
        poke_i++;
    }

    int player_input = 0;
    //Displaying menu to the user
    while (1)
    {
        printMenu();
        if (!readInt(&player_input, buffer, sizeof(buffer)))
        {
            printf("Please choose a valid number.\n");
            continue;
        }
        if (player_input < 1 || player_input > 9)
        {
            printf("Please choose a valid number.\n");
            continue;
        }
        if (player_input == 1)
        {
            for (int i = 0; i < num_of_pokemon; i++)
            {
                if (pokemons[i] != NULL)
                {
                    printPokemon(pokemons[i]);
                }
            }
            continue;
        }
        else if (player_input == 2)
        {
            for (int i = 0; i < num_of_types; i++)
            {
                if (types[i] != NULL)
                {
                    printPokemonType(types[i]);
                }
            }
            continue;
        }
        else if (player_input == 3)
        {
            printf("Please enter type name:\n");
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *poke_type = findTypeInArrOfArr(types, num_of_types, buffer);
            if (poke_type == NULL)
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            printf("Please enter type name to add to %s effective against me list:\n", poke_type->type_name);
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *type_to_add = findTypeInArrOfArr(types, num_of_types, buffer);
            if (type_to_add == NULL)
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            Result r = addEffectiveAgainstMe(poke_type, type_to_add);
            if (r == out_of_memory)
            {
                printf("Memory Problem\n");
                break;
            }
            else if (r == failure)
            {
                printf("This type already exist in the list.\n");
                continue;
            }
            printPokemonType(poke_type);
        }
        else if (player_input == 4)
        {
            printf("Please enter type name:\n");
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *poke_type = findTypeInArrOfArr(types, num_of_types, buffer);
            if (poke_type == NULL)
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            printf("Please enter type name to add to %s effective against others list:\n", poke_type->type_name);
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *type_to_add = findTypeInArrOfArr(types, num_of_types, buffer);
            if (type_to_add == NULL)
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            Result r = addEffectiveAgainstOthers(poke_type, type_to_add);
            if (r == out_of_memory)
            {
                printf("Memory Problem\n");
                break;
            }
            else if (r == failure)
            {
                printf("This type already exist in the list.\n");
                continue;
            }

            printPokemonType(poke_type);
        }

        else if (player_input == 5)
        {
            printf("Please enter type name:\n");
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *poke_type = findTypeInArrOfArr(types, num_of_types, buffer);
            if (poke_type == NULL)
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            printf("Please enter type name to remove from %s effective against me list:\n",poke_type->type_name);
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *type_to_remove = findTypeInArrOfArr(types, num_of_types, buffer);
            if (type_to_remove == NULL)
            {
                printf("Type name doesn't exist in the list.\n");
                continue;
            }
            Result r = deleteFromAffectiveAgainstMe(poke_type, type_to_remove);
            if (r == out_of_memory)
            {
                printf("Memory Problem\n");
                break;
            }
            else if (r == failure)
            {
                printf("Type name doesn't exist in the list.\n");
                continue;
            }
            printPokemonType(poke_type);
        }
        else if (player_input == 6)
        {
            printf("Please enter type name:\n");
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *poke_type = findTypeInArrOfArr(types, num_of_types, buffer);
            if (poke_type == NULL)
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            printf("Please enter type name to remove from %s effective against others list:\n", poke_type->type_name);
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *type_to_remove = findTypeInArrOfArr(types, num_of_types, buffer);
            if (type_to_remove == NULL)
            {
                printf("Type name doesn't exist in the list.\n");
                continue;
            }
            Result r = deleteFromAffectiveAgainstOthers(poke_type, type_to_remove);
            if (r == out_of_memory)
            {
                printf("Memory Problem\n");
                break;
            }
            else if (r == failure)
            {
                printf("Type name doesn't exist in the list.\n");
                continue;
            }

            printPokemonType(poke_type);
        }

        else if (player_input == 7)
        {
            printf("Please enter Pokemon name:\n");
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("The Pokemon doesn't exist.\n");
                continue;
            }
            Pokemon *poke = NULL;
            for (int i = 0; i < num_of_pokemon; i++)
            {
                if (pokemons[i] != NULL && strcmp(pokemons[i]->name, buffer) == 0)
                {
                    poke = pokemons[i];
                    break;
                }
            }
            if (poke == NULL)
            {
                printf("The Pokemon doesn't exist.\n");
            }
            else
            {
                printPokemon(poke);
            }
        }
        else if (player_input == 8)
        {
            printf("Please enter type name:\n");
            if (!readLine(buffer, sizeof(buffer)))
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            PokemonType *poke_type = findTypeInArrOfArr(types, num_of_types, buffer);
            if (poke_type == NULL)
            {
                printf("Type name doesn't exist.\n");
                continue;
            }
            int num_of_this_type = 0;
            for (int i = 0; i < num_of_pokemon; i++)
            {
                if (pokemons[i] != NULL &&
                    strcmp(pokemons[i]->type.type_name, poke_type->type_name) == 0)
                {
                    num_of_this_type++;
                }
            }
            if (num_of_this_type == 0)
            {
                printf("There are no Pokemons with this type.\n");
                continue;
            }
            printf("There are %d Pokemons with this type:\n", num_of_this_type);

            for (int j = 0; j < num_of_pokemon; j++)
            {
                if (pokemons[j] != NULL &&
                    strcmp(pokemons[j]->type.type_name, poke_type->type_name) == 0)
                {
                    printPokemon(pokemons[j]);
                }
            }
        }

        else if (player_input == 9)
        {
            for (int i = 0; i < num_of_pokemon; i++)
            {
                if (pokemons[i] != NULL)
                {
                    destroyPokemon(pokemons[i]);
                }
            }
            for (int j = 0; j < num_of_types; j++)
            {
                if (types[j] != NULL)
                {
                    destroyPokemonType(types[j]);
                }
            }
            free(pokemons);
            free(types);
            fclose(file);
            printf("All the memory cleaned and the program is safely closed.\n");
            return 0;
        }
    }
}