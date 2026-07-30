//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_FIGHTER_H
#define ASSIGNMENT5_FIGHTER_H
#include "Character.h"
/*
 * Fighter:
 * A character type with fixed starting stats.
 * Starts with 60 max health and a hand limit of 6 cards.
 * Defines which block sign it uses against each enemy type.
 */
class Fighter : public Character
{
public:

    /*
     * Fighter:
     * Creates a Fighter with max health 60 and hand limit 6.
     */
    Fighter() : Character(60, 6) {}

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Troll.
     * Returns 'H'.
     */
    char blockedSignAgainst(const Troll&) const override {return 'H';}

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Ghost.
     * Returns 'B' (means both 'C' and 'S').
     */
    char blockedSignAgainst(const Ghost&) const override {return 'B';} // 'B' = both 'C' and 'S'

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Dragon.
     * Returns 'D'.
     */
    char blockedSignAgainst(const Dragon&) const override {return 'D';}
};


#endif //ASSIGNMENT5_FIGHTER_H