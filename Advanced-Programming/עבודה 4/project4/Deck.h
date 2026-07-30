//
// Created by Bar Hana Yehezkel on 31/12/2025.
//
#ifndef PROJECT4_DECK_H
#define PROJECT4_DECK_H
#include <iostream>
#include "Card.h"

class Deck
{
private:
    Card** cards; //dynamic array of pointers to Card objects
    int size; // current number of cards in the deck

    /* resize:
     * Changes the deck capacity to new_size.
     * Allocates a new array, copies existing card pointers, and updates the deck.
     * Used internally when adding/removing cards.
     */
    void resize( int new_size);
public:
    /* Deck (default constractor):
     * Creates an empty deck (size = 0, cards = nullptr).
     */
    Deck() : cards(nullptr), size(0) {}
    /* Deck (copy constractor):
     * Creates a deep copy of another deck.
     * Allocates a new array and copies the cards.
     */
    Deck(const Deck& other);
    /* ~Deck:
     * Destroys the deck and frees all allocated memory (cards and the array).
     */
    ~Deck();
    /* getSize:
     * Returns the current number of cards in the deck.
     */
    int getSize() const {return size;}
    /* operator=:
    * Replaces this deck content with a deep copy of other.
    * Returns *this by reference so assignments can be chained (a = b = c).
    */
    Deck& operator=(const Deck& other);
    /* operator+=:
     * Adds a card to the end of the deck.
     * Returns *this by reference so operations can be chained (d += c1 += c2).
     */
    Deck& operator+=(const Card& card);
    /* peek:
     * Prints up to x cards from the top of the deck.
     * If x is bigger than the deck size, prints all cards.
     */
    void peek(int x) const;
    /* operator-=:
     * Removes x cards from the top of the deck.
     * If x is bigger than the deck size, clears the deck.
     * Returns *this by reference so operations can be chained.
     */
    Deck& operator-=(int x);
    /* operator[]:
     * Returns the card at index i by reference.
     * This allows changing the card inside the deck, for example: deck[i] = newCard;
     */
    Card& operator[](int i) {return *(cards[i]);}
    /* operator[] (const):
    * Returns the card at index i by const reference.
    * This is used when the deck is const, and prevents modifying the deck through [].
    * Returning a const reference avoids creating a copy.
    */
    const Card& operator[](int i) const {return *(cards[i]);}
    /* addByIndex:
    * Inserts a card at index i instead of the old card.
    */
    void addByIndex(int i, const Card& card);
    /* operator<<:
     * Prints the whole deck in the required project format.
     * Returns the stream by reference so printing can be chained.
     */
    friend std::ostream& operator<<(std::ostream& out, const Deck& d);
};


#endif //PROJECT4_DECK_H