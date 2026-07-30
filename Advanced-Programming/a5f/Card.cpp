//
// Created by Bar Hana Yehezkel on 31/12/2025.
//

#include "Card.h"

/* getValue:
 * Returns the game value of this card.
 * Invalid card returns 0.
 */
int Card::getValue() const
{
    if (rank == INVALID_R){return 0;}
    else if (rank == ACE){ return 1;}
    else if(rank == TWO) { return 2;}
    else if(rank == THREE) { return 3;}
    else if(rank == FOUR) { return 4;}
    else if(rank == FIVE) { return 5;}
    else if(rank == SIX) { return 6;}
    else if(rank == SEVEN) { return 7;}
    else if(rank == EIGHT) { return 8;}
    else if(rank == NINE) { return 9;}
    else if(rank == TEN) { return 10;}
    else if(rank == JACK) { return 10;}
    else if(rank == QUEEN) { return 15;}
    else if(rank == KING) { return 20;}
    else {return -1;}
}

/* operator<:
 * Compares two cards.
 * First compares by rank and if ranks are equal compares by sign.
 */
bool Card::operator<(const Card& other) const
{
    if (rank != other.rank)
    {
        return rank < other.rank;
    }
    return sign < other.sign;
}

/* operator<=:
 * Returns true if this card is smaller than or equal to other.
 * Implemented using operator< to keep all ordering logic in one place.
 */
bool Card::operator<=(const Card& other) const
{
    return !(other < *this);
}

/* operator>:
 * Returns true if this card is greater than other.
 * Implemented using operator< to avoid duplicating comparison logic.
 */
bool Card::operator>(const Card& other) const
{
    return other < *this;
}

/* operator>=:
 * Returns true if this card is greater than or equal to other.
 * Implemented using operator< to keep consistent ordering.
 */
bool Card::operator>=(const Card& other) const
{
    return !(*this < other);
}

/* operator=:
 * Copies rank and sign from other into this card.
 * Returns *this by reference so assignments can be chained (a = b = c).
 */
Card& Card::operator=(const Card& other)
{
    if (this == &other)
    {
        return *this;
    }
    rank = other.rank;
    sign = other.sign;
    return *this;
}

/* operator<<:
 * Prints the card as two characters: rank + sign.
 * Returns the output stream by reference so printing can be chained.
 */
std::ostream& operator<<(std::ostream &out, const Card& card)
{
    char rank_c = '?';
    char sign_c = '?';
    switch (card.rank)
    {
        case ACE: rank_c = 'A'; break;
        case TWO: rank_c = '2'; break;
        case THREE: rank_c = '3'; break;
        case FOUR: rank_c = '4'; break;
        case FIVE: rank_c = '5'; break;
        case SIX: rank_c = '6'; break;
        case SEVEN: rank_c = '7'; break;
        case EIGHT: rank_c = '8'; break;
        case NINE: rank_c = '9'; break;
        case TEN: rank_c = 'T'; break;
        case JACK: rank_c = 'J'; break;
        case QUEEN: rank_c = 'Q'; break;
        case KING: rank_c = 'K'; break;
        default: rank_c = '?'; break;
    }
    switch (card.sign)
    {
        case C: sign_c = 'C'; break;
        case D: sign_c = 'D'; break;
        case H: sign_c = 'H'; break;
        case S: sign_c = 'S'; break;
        default: sign_c = '?'; break;
    }
    out << rank_c << sign_c;
    return out;
}

