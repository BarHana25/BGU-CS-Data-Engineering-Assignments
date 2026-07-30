//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#include "Character.h"
#include "GameExceptions.h"
#include <algorithm>

/*
 * availableHandSpace:
 * Returns how many cards can still be added to the hand.
 * If the hand is already at the limit, returns 0.
 */
int Character::availableHandSpace() const
{
    int current = (int)hand.size();
    if (current >= hand_lim) return 0;
    return hand_lim - current;
}

/*
 * heal:
 * Adds the given amount to the character's health.
 * If amount is 0 or negative, does nothing.
 * Health will not go above max health.
 */
void Character::heal(int amount)
{
    if (amount <= 0) return;
    health_points += amount;
    if (health_points > max_health_points)
        health_points = max_health_points;
}

/*
 * printHand:
 * Prints the character's hand to the given output stream.
 * Cards are printed from the last card to the first card, separated by spaces.
 */
void Character::printHand(std::ostream& out) const
{
    for (int i = static_cast<int>(hand.size()) - 1; i >= 0; --i)
    {
        out << hand[i] << " ";
    }
    out << std::endl;
}

/*
 * drawTopCard:
 * Takes the top card from the deck and removes it from the deck.
 * Throws DeckRanOut if the deck is empty.
 * Returns the drawn card.
 */
static Card drawTopCard(Deck& deck)
{
    if (deck.getSize() == 0) throw DeckRanOut();
    Card top = deck[deck.getSize() - 1];
    deck -= 1;
    return top;
}

/*
 * drawCards:
 * Draws up to 2 cards from the deck into the character's hand.
 * Stops if the hand reaches the hand limit.
 * Throws DeckRanOut if the deck is empty when trying to draw.
 * Returns how many cards were drawn.
 */
int Character::drawCards(Deck& deck)
{
    int drawn = 0;

    while (drawn < 2 && (int)hand.size() < hand_lim)
    {
        hand.push_back(drawTopCard(deck));
        drawn++;
    }

    return drawn;
}

/*
 * canPlay:
 * Checks if the given set of cards exists in the character's hand.
 * Each card must appear enough times in the hand (duplicates matter).
 * Returns true if the full set can be played, otherwise false.
 */
bool Character::canPlay(const CardSet& set_cards) const
{
    std::vector<Card> cards_remaining = hand;
    for (const Card& card : set_cards.getCards())
    {
        auto it = std::find(cards_remaining.begin(), cards_remaining.end(), card);
        if ( it == cards_remaining.end()) return false;
        cards_remaining.erase(it);
    }
    return true;
}

/*
 * play:
 * Removes the given set of cards from the character's hand.
 * Throws BadCardSetInput if the set of cards is not fully in the hand.
 */
void Character::play(const CardSet& set_cards)
{
    if (!canPlay(set_cards))
    {
        throw BadCardSetInput("Card set is not in hand");
    }
    for (const Card& card : set_cards.getCards())
    {
        auto it = std::find(hand.begin(), hand.end(), card);
        if (it != hand.end()) hand.erase(it);
    }
}
/*
 * reFillHand:
 * Draws cards until the hand reaches the hand limit.
 * Throws DeckRanOut if the deck runs out while drawing.
 */

void Character::reFillHand(Deck& deck)
{
    while ((int)hand.size() < hand_lim)
        hand.push_back(drawTopCard(deck));
}

