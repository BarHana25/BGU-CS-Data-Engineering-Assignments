//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_WIZARD_H
#define ASSIGNMENT5_WIZARD_H
#include "Character.h"

/*
 * Wizard:
 * A character type with fixed starting stats.
 * Starts with 40 max health and a hand limit of 8 cards.
 * Defines which block sign it uses against each enemy type.
 */
class Wizard : public Character
{
    public:

    /*
     * Wizard:
     * Creates a Wizard with max health 40 and hand limit 8.
     */
    explicit Wizard(): Character(40, 8) {}

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Troll.
     * Returns 'D'.
     */
    char blockedSignAgainst(const Troll&) const override {return 'D';}

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Ghost.
     * Returns 'H'.
     */
    char blockedSignAgainst(const Ghost&) const override {return 'H';}

    /*
     * blockedSignAgainst:
     * Returns the block sign used against a Dragon.
     * Returns 'B' (means both 'C' and 'S').
     */
    char blockedSignAgainst(const Dragon&) const override {return 'B';} // 'B' = both 'C' and 'S'

};


#endif //ASSIGNMENT5_WIZARD_H