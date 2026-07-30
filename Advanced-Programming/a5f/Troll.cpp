//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#include "Troll.h"
#include "Character.h"
char Troll::blockedSignFor(const Character& c) const
{
    return c.blockedSignAgainst(*this);
}