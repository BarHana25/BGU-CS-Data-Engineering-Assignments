//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#include "Dragon.h"
#include "Character.h"

/*
 * blockedSignFor:
 * Returns the block sign the given character uses against this Dragon.
 * Calls the character's blockedSignAgainst(Dragon) function.
 */
char Dragon::blockedSignFor(const Character& c) const
{
    return c.blockedSignAgainst(*this);
}