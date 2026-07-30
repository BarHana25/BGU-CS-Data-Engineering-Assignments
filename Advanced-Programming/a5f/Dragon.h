//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_DRAGON_H
#define ASSIGNMENT5_DRAGON_H
#include "Enemy.h"

/*
 * Dragon:
 * Enemy type with fixed stats.
 * Starts with 75 max health points and deals 10 damage points.
 * Uses the character to decide which block sign is needed.
 */
class Dragon : public Enemy
{
public:

    /*
     * Dragon:
     * Creates a Dragon with 75 max health and 10 damage.
     */
    Dragon(): Enemy(75, 10){}

    /*
     * blockedSignFor:
     * Returns the block sign required when fighting this Dragon.
     * The result depends on the given character.
     */
    char blockedSignFor(const Character& c) const override;
};


#endif //ASSIGNMENT5_DRAGON_H