//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_BOWMAN_H
#define ASSIGNMENT5_BOWMAN_H
#include "Character.h"

/*
 * Bowman:
 * A character type with fixed starting stats.
 * Starts with 50 max health and a hand limit of 7 cards.
 * Defines which block sign it uses against each enemy type.
 */
class Bowman : public Character
{
public:

    /*
     * Bowman:
     * Creates a Bowman with max health 50 and hand limit 7.
     */
    Bowman(): Character(50, 7) {}

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Troll.
     * Returns 'B' (means both 'C' and 'S').
     */
    char blockedSignAgainst(const Troll&) const override {return 'B';} // 'B' = both 'C' and 'S'

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Ghost.
     * Returns 'D'.
     */
    char blockedSignAgainst(const Ghost&) const override {return 'D';}

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Dragon.
     * Returns 'H'.
     */
    char blockedSignAgainst(const Dragon&) const override {return 'H';}
};


#endif //ASSIGNMENT5_BOWMAN_H