//
// Created by Bar Hana Yehezkel on 21/11/2025.
//

#ifndef DEFS_H
#define DEFS_H

typedef enum e_bool { false, true } bool;
typedef enum e_status {success, failure, out_of_memory
} status;

typedef void * element;

typedef element(*copyFunction) (element);
typedef status(*freeFunction) (element);
typedef status(*printFunction) (element);

/* equalFunction :Compares two elements:
returns: 1 if first > second,
     0 if they are equal,
    -1 if first < second.  */
typedef int(*equalFunction) (element, element);

typedef char*(*getCategoryFunction)(element);

/* getAttackFunction :Calculates the attack of both elements.
Returns (attackFirst - attackSecond) and stores each attack value in the
given pointers. */
typedef int(*getAttackFunction)(element firstElem ,element secondElem ,int* attackFirst,int* attackSecond);


#endif //DEFS_H
