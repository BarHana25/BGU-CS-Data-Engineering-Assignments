//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_CHARACTER_H
#define ASSIGNMENT5_CHARACTER_H
#include <vector>
#include <cstddef>
#include <iostream>
#include "Creature.h"
#include "Card.h"
#include "Deck.h"
#include "CardSet.h"

class Troll;
class Ghost;
class Dragon;

/*
 * Character:
 * Base class for a player character.
 * Inherits from Creature and adds a hand of cards and a hand limit.
 * Can draw cards, print the hand, check if a card set can be played, and play it.
 * Also defines blocking signs against different enemies (Troll, Ghost, Dragon).
 */
class Character : public Creature
{
protected:
    int hand_lim;
    std::vector<Card> hand;
    Character() : Creature(), hand_lim(0){}
    Character(int max_health_points, int hand_lim) : Creature(max_health_points), hand_lim(hand_lim) {}

    /*
     * availableHandSpace:
     * Returns how many cards can still be added to the hand.
     * If the hand is already at the limit, returns 0.
     */
    int availableHandSpace() const;

public:

    /*
     * ~Character:
     * Virtual destructor for Character.
     * Allows deleting derived characters through a Character pointer.
     */
    ~Character() override = default;

    /*
     * getHandLim:
     * Returns the maximum number of cards the character can hold in hand.
     */
    int getHandLim() const {return hand_lim;}

    /*
     * heal:
     * Adds the given amount to the character's health.
     * If amount is 0 or negative, does nothing.
     * Health will not go above max health.
     */
    void heal(int amount);

    /*
     * printHand:
     * Prints the character's hand to the given output stream.
     * Cards are printed from the last card to the first card, separated by spaces.
     */
    void printHand(std::ostream& out) const;

    /*
     * drawCards:
     * Draws up to 2 cards from the deck into the character's hand.
     * Stops if the hand reaches the hand limit.
     * Throws DeckRanOut if the deck is empty when trying to draw.
     * Returns how many cards were drawn.
     */
    int drawCards(Deck& deck);

    /*
     * canPlay:
     * Checks if the given set of cards exists in the character's hand.
     * Each card must appear enough times in the hand (duplicates matter).
     * Returns true if the full set can be played, otherwise false.
     */
    bool canPlay(const CardSet& set_cards) const;

    /*
     * play:
     * Removes the given set of cards from the character's hand.
     * Throws BadCardSetInput if the set of cards is not fully in the hand.
     */
    void play(const CardSet& set_cards);

    /*
     * reFillHand:
     * Draws cards until the hand reaches the hand limit.
     * Throws DeckRanOut if the deck runs out while drawing.
     */
    void reFillHand( Deck& deck);

    /*
     * blockedSignAgainst:
     * Returns the block sign this character uses against a Troll.
     */
    virtual char blockedSignAgainst(const Troll&) const = 0;

    /*
     * blockedSignAgainst:
     * Returns the block sign this character uses against a Ghost.
     */
    virtual char blockedSignAgainst(const Ghost&) const = 0;

    /*
     * blockedSignAgainst:
     * Returns the block sign this character uses against a Dragon.
     */
    virtual char blockedSignAgainst(const Dragon&) const = 0;
};


#endif //ASSIGNMENT5_CHARACTER_H