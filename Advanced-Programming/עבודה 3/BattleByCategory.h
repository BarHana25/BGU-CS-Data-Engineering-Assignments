
#ifndef BATTLEBYCATEGORY_H_
#define BATTLEBYCATEGORY_H_
#include "Defs.h"

/* Pointer to Battle ADT. */
typedef struct battle_s* Battle;

/*
 * Creates a new battle system that stores elements by string categories.
 * Returns NULL on error.
 * capacity           - max number of elements per category
 * numberOfCategories - number of categories
 * categories         - comma-separated category names, e.g. "cat1,cat2,cat3"
 * generic functions  - function pointers as required by the generic ADT
 */
Battle createBattleByCategory(int capacity,int numberOfCategories,char* categories,equalFunction equalElement,copyFunction copyElement,freeFunction freeElement,getCategoryFunction getCategory,getAttackFunction getAttack,printFunction printElement);

/*
 * Destroys the battle system and frees all internal memory.
 * b - battle pointer to destroy
 */
status destroyBattleByCategory(Battle b);

/*
 * Inserts a new element into the correct category, if possible.
 * b    - battle pointer
 * elem - element to insert
 * Returns status_success on success, error status otherwise.
 */
status insertObject(Battle b, element elem);

/*
 * Prints all elements grouped by categories, from strongest to weakest.
 * b - battle pointer
 */
void displayObjectsByCategories(Battle b);

/*
 * Removes and returns the strongest element in a given category.
 * b        - battle pointer
 * category - category name
 * Returns the removed element, or NULL if none.
 */
element removeMaxByCategory(Battle b,char* category);

/*
 * Returns how many elements exist in a given category.
 * b        - battle pointer
 * category - category name
 */
int getNumberOfObjectsInCategory(Battle b,char* category);

/*
 * Performs a battle between elem and the best matching element in the system.
 * b    - battle pointer
 * elem - challenger element
 * Returns the winning element, or NULL if no opponent exists.
 * Also prints the battle details.
 */
element fight(Battle b,element elem);


#endif /* BATTLEBYCATEGORY_H_ */
