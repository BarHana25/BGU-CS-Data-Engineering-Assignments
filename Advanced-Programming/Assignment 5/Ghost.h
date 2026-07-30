//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_GHOST_H
#define ASSIGNMENT5_GHOST_H
#include "Enemy.h"

/*
 * Ghost:
 * Enemy type with fixed stats.
 * Starts with 50 max health points and deals 15 damage points.
 * Uses the character to decide which block sign is needed.
 */
class Ghost : public Enemy
{
public:

    /*
     * Ghost:
     * Creates a Ghost with 50 max health and 15 damage.
     */
    Ghost(): Enemy(50, 15){}

    /*
     * blockedSignFor:
     * Returns the block sign required when fighting this Ghost.
     * The result depends on the given character.
     */
    char blockedSignFor(const Character& c) const override;
};



#endif //ASSIGNMENT5_GHOST_H