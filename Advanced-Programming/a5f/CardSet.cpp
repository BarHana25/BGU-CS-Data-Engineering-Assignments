//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#include "CardSet.h"
#include <sstream>

#include "GameExceptions.h"

/*
 * splitByCard:
 * Splits the input string by spaces into card strings.
 * Each returned item should look like "AH" or "7D".
 */
std::vector<std::string> CardSet::splitByCard(const std::string& s)
{
    std::istringstream in(s);
    std::vector<std::string> cards;
    std::string card;
    while (in >> card) cards.push_back(card);
    return cards;
}

/*
 * isValidCard:
 * Checks if a card string is valid.
 * A valid card is exactly 2 characters: one rank and one sign.
 * Returns true if both rank and sign are known.
 */
bool CardSet::isValidCard(const std::string& card)
{
    if (card.size() != 2) return false;
    Rank r;
    Sign s;
    if (!readRankInput(card[0], r)) return false;
    if (!readSignInput(card[1], s)) return false;
    return true;
}

/*
 * readCardInput:
 * Converts a 2-char card string into a Card object.
 * Throws BadCardSetInput if the string has a bad length, rank, or sign.
 */
Card CardSet::readCardInput(const std::string& card)
{
    if (card.size() !=2)
    {
        throw BadCardSetInput("Bad card length: " + card);
    }
    Rank r;
    Sign s;
    if (!readRankInput(card[0], r))
    {
        throw BadCardSetInput("Bad card rank: " + card);
    }
    if (!readSignInput(card[1], s))
    {
        throw BadCardSetInput("Bad card sign: " + card);
    }
    return Card(r, s);
}

/*
 * CardSet:
 * Builds a CardSet from a text input line.
 * The line should contain cards separated by spaces (example: "AH 7D 3C").
 * Throws BadCardSetInput if the line is empty or contains an invalid card.
 */
CardSet::CardSet(const std::string& input)
{
    auto card_strings  = splitByCard(input);

    if (card_strings.empty())
    {
        throw BadCardSetInput("Empty line");
    }
    for (const auto& card_string : card_strings)
    {
        cards.push_back(readCardInput(card_string));
    }

}

/*
 * readRankInput:
 * Reads a rank character (A,2-9,T,J,Q,K) and sets r.
 * Returns 1 if the input is valid, otherwise 0.
 */
int CardSet::readRankInput(char input, Rank& r)
{
    switch (input) {
    case 'A': r = ACE;   return 1;
    case '2': r = TWO;   return 1;
    case '3': r = THREE; return 1;
    case '4': r = FOUR;  return 1;
    case '5': r = FIVE;  return 1;
    case '6': r = SIX;   return 1;
    case '7': r = SEVEN; return 1;
    case '8': r = EIGHT; return 1;
    case '9': r = NINE;  return 1;
    case 'T': r = TEN;   return 1;
    case 'J': r = JACK;  return 1;
    case 'Q': r = QUEEN; return 1;
    case 'K': r = KING;  return 1;
    default: return 0;
    }
}

/*
 * readSignInput:
 * Reads a sign character (C, D, H, S) and sets s.
 * Returns 1 if the input is valid, otherwise 0.
 */
int CardSet::readSignInput(char input, Sign& s)
{
    switch (input)
    {
    case 'C': s = C; return 1;
    case 'D': s = D; return 1;
    case 'H': s = H; return 1;
    case 'S': s = S; return 1;
    default:  return 0;
    }
}

/*
 * cardsSimpleValue:
 * Returns the sum of values of all cards in the set.
 * Uses Card::getValue for each card.
 */
int CardSet::cardsSimpleValue() const
{
    int result = 0;
    for (const auto& card : cards)
    {
        result += card.getValue();
    }
    return result;
}

/*
 * hasH:
 * Returns true if the set contains at least one Heart card (H).
 */
bool CardSet::hasH() const
{
    for (const auto& card : cards)
    {
        if (card.getSign() == H) return true;
    }
    return false;
}

/*
 * hasD:
 * Returns true if the set contains at least one Diamond card (D).
 */
bool CardSet::hasD() const
{
    for (const auto& card : cards)
    {
        if (card.getSign() == D) return true;
    }
    return false;
}

/*
 * hasC:
 * Returns true if the set contains at least one Club card (C).
 */
bool CardSet::hasC() const
{
    for (const auto& card : cards)
    {
        if (card.getSign() == C) return true;
    }
    return false;
}

/*
 * hasS:
 * Returns true if the set contains at least one Spade card (S).
 */
bool CardSet::hasS() const
{
    for (const auto& card : cards)
    {
        if (card.getSign() == S) return true;
    }
    return false;
}

/*
 * operator<<:
 * Prints the card set to the output stream.
 * Cards are printed in order, separated by a single space.
 */
std::ostream& operator<<(std::ostream& os, const CardSet& cs)
{
    for (size_t i = 0; i <cs.cards.size(); i++)
    {
        os << cs.cards[i];
        if ( i+1 < cs.cards.size())
        {
            os << " ";
        }
    }
    return os;
}
/*
 * isLegalWithoutAce:
 * Checks if a set is legal when there are no Aces in it.
 * Rules:
 * - Empty set is not legal.
 * - One card is always legal.
 * - More than one card: all cards must have the same rank.
 * - The sum of card values must be 10 or less.
 */

static bool isLegalWithoutAce(const std::vector<Card>& base_set)
{
    if (base_set.empty()) return false;
    if (base_set.size() == 1) return true;
    const Rank rank = base_set[0].getRank();
    for (size_t i = 1; i < base_set.size(); i++)
    {
        if (base_set[i].getRank() != rank) return false;
    }
    int sum = 0;
    for (const Card& card : base_set) sum += card.getValue();
    return sum <= 10;
}

/*
 * isLegal:
 * Checks if this card set is legal by the game rules.
 * Allows a single Ace alone as a legal set.
 * Otherwise checks the set without Aces (or the full set if there are no Aces).
 */
bool CardSet :: isLegal() const
{
    if (cards.empty()) return false;
    int aces = 0;
    std::vector<Card> base_set;
    base_set.reserve(cards.size());
    for (const Card& card : cards)
    {
        if (card.getRank() == ACE) aces++;
        else
        {
            base_set.push_back(card);
        }
    }
    if (aces == 1 && base_set.empty()) return true;
    return isLegalWithoutAce(base_set.empty() ? cards : base_set);
}

/*
 * valueEffective:
 * Returns the effective value of the set for the current block sign.
 * If the set has both C and S, and the enemy does not block C/S (or 'B'),
 * the value is doubled.
 */
int CardSet::valueEffective(char blocked_sign) const
{
    int val = cardsSimpleValue();
    if (hasC() && hasS() && blocked_sign != 'C' && blocked_sign != 'S' && blocked_sign != 'B')
    {
        val *= 2;
    }
    return val;
}


/*
 * healingEffective:
 * Returns true if the set can heal against the current block sign.
 * Healing is effective only if the set has H and the enemy does not block 'H'.
 */
bool CardSet::healingEffective(char blocked_sign) const
{
    return hasH() && blocked_sign != 'H';
}

/*
 * damageEffective:
 * Returns true if the set can deal damage against the current block sign.
 * Damage is effective only if the set has D and the enemy does not block 'D'.
 */
bool CardSet::damageEffective(char blocked_sign) const
{
    return hasD() && blocked_sign != 'D';
}
