//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#include "Ghost.h"
#include "Character.h"

/*
 * blockedSignFor:
 * Returns the block sign the given character uses against this Ghost.
 * Calls the character's blockedSignAgainst(Ghost) function.
 */
char Ghost::blockedSignFor(const Character& c) const
{
    return c.blockedSignAgainst(*this);
}
