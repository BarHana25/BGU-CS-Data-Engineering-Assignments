//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_TROL_H
#define ASSIGNMENT5_TROL_H
#include "Enemy.h"

/*
 * Troll:
 * Enemy type with fixed stats.
 * Starts with 100 max health points and deals 5 damage points.
 * Uses the character to decide which block sign is needed.
 */
class Troll : public Enemy
{
    public:

    /*
     * Troll:
     * Creates a Troll with 100 max health and 5 damage.
     */
    Troll(): Enemy(100, 5){}

    /*
     * blockedSignFor:
     * Returns the block sign required when fighting this Troll.
     * The result depends on the given character.
     */
    char blockedSignFor(const Character& c) const override;
};


#endif //ASSIGNMENT5_TROL_H