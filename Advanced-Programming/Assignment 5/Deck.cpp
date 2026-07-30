//
// Created by Bar Hana Yehezkel on 31/12/2025.
//

#include "Deck.h"

/* resize:
 * Changes the deck size to new_size.
 * If the deck is shrinking, deletes the removed Card objects to avoid memory leaks.
 * Allocates a new pointer array and copies the remaining Card* pointers.
 */
void Deck::resize(int new_size)
{
    if (new_size < 0)
    {
        throw std::invalid_argument("resize: new_size must be 0<=");
    }
    if (new_size == size) return;
    if (new_size == 0)
    {
        for (int i = new_size; i < size; i++)
        {
            delete cards[i];
        }
        delete [] cards;
        cards = nullptr;
        size = 0;
        return;
    }
    Card** new_cards = new Card*[new_size];
    int lim = (new_size < size) ? new_size : size;
    for (int i = 0; i < lim; i++)
    {
        new_cards[i] = cards[i];
    }
    for (int i = lim; i < new_size; i++)
    {
        new_cards[i] = nullptr;
    }
    if (new_size < size)
    {
        for (int i = new_size; i < size; i++)
        {
            delete cards[i];
            cards[i] = nullptr;
        }
    }
    delete [] cards;
    cards = new_cards;
    size = new_size;
}

/* Deck (copy constractor):
 * Creates a deep copy of another deck.
 * Allocates a new pointer array and clones each Card object.
 */
Deck::Deck(const Deck& other) : cards(nullptr), size(other.size)
{
    if (size == 0) return;
    cards = new Card*[size]();
    try
    {
        for (int i = 0; i < size; i++)
        {
            cards[i] = new Card(*(other.cards[i]));
        }
    }
    catch (...)
    {
        for (int i = 0; i < size; i++)
        {
            delete cards[i];
        }
        delete[] cards;
        cards = nullptr;
        size = 0;
        throw; //same error after freeing rethrow to the main
    }
}

/* ~Deck:
 * Frees all allocated memory of the deck.
 * Deletes every Card object and then deletes the pointer array.
 */
Deck::~Deck()
{
    for (int i = 0; i < size; i++)
    {
        delete cards[i];
        cards[i] = nullptr;
    }
    delete[] cards;
    cards = nullptr;
    size = 0;
}

/* operator=:
 * Replaces this deck with a deep copy of other.
 * Returns *this by reference so assignments can be chained (a = b = c).
 */
Deck& Deck::operator=(const Deck& other)
{
    if (this == &other) return *this;
    Card** new_cards = nullptr;
    int new_size = other.size;
    try
    {
        new_cards = new Card*[new_size]();
        for (int i = 0; i < new_size; i++)
        {
            new_cards[i] = new Card(*(other.cards[i]));
        }
    }
    catch (...)
    {
        if (new_cards)
        {
            for (int i = 0; i< new_size; i++)
            {
                delete new_cards[i];
            }
        }
        delete[] new_cards;
        throw; //same error after freeing rethrow to the main
    }
    for (int i = 0; i < size; i++)
    {
        delete cards[i];
    }
    delete [] cards;
    cards = new_cards;
    size = new_size;
    return *this;
}
/* operator+=:
 * Adds a card to  the deck.
 * Creates a new array (size+1), puts the new card first, and shifts old pointers right.
 * Returns *this by reference so operations can be chained.
 */
Deck& Deck::operator+=(const Card& card)
{
    Card** old_cards = cards;
    int old_size = size;
    Card** new_cards = nullptr;
    Card* new_card = nullptr;
    try
    {
        new_cards = new Card*[old_size+1];
        new_card = new Card(card);
        new_cards[0] = new_card;
        for (int i = 0; i < old_size; i++)
        {
            new_cards[i+1] = old_cards[i];
        }
        cards = new_cards;
        size = old_size + 1;
        delete[] old_cards;
        return *this;
    }
    catch (...)
    {
        delete new_card;
        delete[] new_cards;
        cards = old_cards;
        size = old_size;
        throw; //same error after freeing rethrow to the main
    }
}

/* peek:
 * Prints the top x cards.
 * If x is bigger than size, prints all cards.
 * If x is negative, throw invalid_argument.
 */
void Deck::peek(int x) const
{
    if (x<0)
    {
         throw std::invalid_argument("Invalid number");
    }
    int lim = (x> size) ? size : x;
    for (int i = size-1; i >= size-lim; i--)
    {
        std::cout << *(cards[i]) << std::endl;
    }
}

/* operator-=:
 * Removes x cards from the end of the deck.
 * If x <= 0 or deck is empty does nothing.
 * If x >= size clears the entire deck.
 * Returns *this by reference so operations can be chained.
 */
Deck& Deck::operator-=(int x)
{
    if (x<=0 || size==0) return *this;
    if ( x>=size)
    {
        for (int i = 0; i < size; i++)
        {
            delete (cards[i]);
        }
        delete[] cards;
        cards = nullptr;
        size = 0;
        return *this;
    }
    Card** new_cards = new Card*[size-x];
    for (int i = 0; i < size-x; i++)
    {
        new_cards[i] = cards[i];
    }
    for (int i = size-x; i < size; i++)
    {
        delete (cards[i]);
        cards[i] = nullptr;
    }
    delete [] cards;
    cards = new_cards;
    size -= x;
    return *this;
}

const Card& Deck::operator[](int i) const
{
    if (i < 0 || i >= size)
        throw std::out_of_range("Invalid index");
    return *(cards[i]);
}

/* addByIndex:
 * Replaces the card at index i with the given card (deep copy).
 * If i is out of bounds, does nothing.
 */
void Deck::addByIndex(int i, const Card& card)
{
    if (i >= size || i < 0)
    {
        return;
    }
    Card* new_card = new Card(card);
    delete cards[i];
    cards[i] = new_card;
}
/* operator<<:
 * Prints the whole deck in the format: [<card>,<card>,...]
 * Returns the stream by reference so printing can be chained.
 */
std::ostream& operator<<(std::ostream& out, const Deck& d)
{
    out << "[";
    for (int i = 0; i < d.size; i++)
    {
        out << *(d.cards[i]);
        if (i != d.size - 1)
        {
            out << ",";
        }
    }
    out << "]";
    return out;
}
