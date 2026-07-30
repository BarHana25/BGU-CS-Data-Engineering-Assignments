//
// Created by Bar Hana Yehezkel on 31/12/2025.
//

#ifndef PROJECT4_CARD_H
#define PROJECT4_CARD_H
#include <iostream>

/* Rank:
 * Represents the card rank.
 * INVALID_R is used for empty cards.
 */
enum  Rank {INVALID_R = -1, ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING};
/* Sign:
 * Represents the card sign.
 * INVALID_S is used for empty cards.
 * D = Diamonds, H = Hearts, S = Spades, C = Clubs.
 */
enum  Sign {INVALID_S = -1, D, H, S, C };

class Card
{
private:
    Rank rank;
    Sign sign;

public:
    /* Card (default constractor):
     * Creates an invalid card (rank/sign are INVALID).
     */
    Card() : rank(INVALID_R), sign(INVALID_S){}
    /* Card (constractor):
     * Creates a card with a specific rank and sign.
     */
    Card(const Rank r, const Sign s) : rank(r), sign(s) {}
    /* Card (copy constractor):
         * Creates a new card as a copy of another card.
    */
    Card(const Card& other) : rank(other.rank), sign(other.sign) {}
    /* getRank:
     * Returns the card rank.
     */
    Rank getRank() const { return rank; }
    /* getSign:
     * Returns the card suit (sign).
     */
    Sign getSign() const { return sign; }
    /* getValue:
     * Returns the game value of the card.
     */
    int getValue() const;
    /* operator==:
     * Returns true if both rank and sign are equal.
     */
    bool operator==(const Card& other) const {return rank == other.rank && sign == other.sign;}
    /* operator!=:
     * Returns true if rank or sign are different.
     */
    bool operator!=(const Card& other) const {return rank != other.rank || sign != other.sign;}
    /* operator<:
    * Compares two cards by rank first, and if rank is equal then by sign.
    */
    bool operator<(const Card& other) const;
    /* operator<=:
     * Returns true if this card is smaller than or equal to other.
     */
    bool operator<=(const Card& other) const;
    /* operator>:
     * Returns true if this card is greater than other.
     */
    bool operator>(const Card& other) const;
    /* operator>=:
     * Returns true if this card is greater than or equal to other.
     */
    bool operator>=(const Card& other) const;
    /* operator=:
     * Copies rank and sign from other into this card.
     * Returns *this by reference so assignments can be chained (a = b = c).
     */
    Card& operator=(const Card& other);
    /* operator<<:
     * Prints the card in a readable format.
     * The exact format depends on your project output.
     */
    friend std :: ostream& operator<<(std::ostream &out, const Card& card);

};
#endif //PROJECT4_CARD_H
