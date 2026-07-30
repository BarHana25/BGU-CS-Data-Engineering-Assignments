//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_CARDSET_H
#define ASSIGNMENT5_CARDSET_H
#include <vector>
#include <string>
#include "Card.h"

/*
 * CardSet:
 * Represents a set of cards given by the player in one move.
 * The set is built from a text line and stored as Card objects.
 * Provides helper checks like value, legality, and effect (heal/damage) vs block sign.
 */
class CardSet
{
private:
    std::vector<Card> cards; // The cards inside the set

    /*
     * splitByCard:
     * Splits the input string by spaces into card strings.
     * Each returned item should look like "AH" or "7D".
     */
    static std::vector<std::string> splitByCard(const std::string& s);

    /*
     * isValidCard:
     * Checks if a card string is valid.
     * A valid card is exactly 2 characters: one rank and one sign.
     * Returns true if both rank and sign are known.
     */
    static bool isValidCard(const std::string& card);

    /*
     * readRankInput:
     * Reads a rank character (A,2-9,T,J,Q,K) and sets r.
     * Returns 1 if the input is valid, otherwise 0.
     */
    static int readRankInput(char input, Rank& r);

    /*
     * readSignInput:
     * Reads a sign character (C, D, H, S) and sets s.
     * Returns 1 if the input is valid, otherwise 0.
     */
    static int readSignInput(char input, Sign& s);

    /*
     * readCardInput:
     * Converts a 2-char card string into a Card object.
     * Throws BadCardSetInput if the string has a bad length, rank, or sign.
     */
    static Card readCardInput(const std::string& card);
public:

    /*
     * CardSet:
     * Builds a CardSet from a text input line.
     * The line should contain cards separated by spaces (example: "AH 7D 3C").
     * Throws BadCardSetInput if the line is empty or contains an invalid card.
     */
    explicit CardSet(const std::string& input);

    /*
     * getCards:
     * Returns a read-only reference to the cards in the set.
     */
    const std::vector<Card>& getCards() const {return cards;}

    /*
     * cardsSimpleValue:
     * Returns the sum of values of all cards in the set.
     * Uses Card::getValue for each card.
     */
    int  cardsSimpleValue() const;

    /*
     * hasH:
     * Returns true if the set contains at least one Heart card (H).
     */
    bool hasH() const;

    /*
     * hasD:
     * Returns true if the set contains at least one Diamond card (D).
     */
    bool hasD() const;

    /*
     * hasC:
     * Returns true if the set contains at least one Club card (C).
     */
    bool hasC() const;

    /*
     * hasS:
     * Returns true if the set contains at least one Spade card (S).
     */
    bool hasS() const;

    /*
     * operator<<:
     * Prints the card set to the output stream.
     * Cards are printed in order, separated by a single space.
     */
    friend std::ostream& operator<<(std::ostream& os, const CardSet& cs);

    /*
     * isLegal:
     * Checks if this card set is legal by the game rules.
     * Allows a single Ace alone as a legal set.
     * Otherwise checks the set without Aces (or the full set if there are no Aces).
     */
    bool isLegal() const;

    /*
     * valueEffective:
     * Returns the effective value of the set for the current block sign.
     * If the set has both C and S, and the enemy does not block C/S (or 'B'),
     * the value is doubled.
     */
    int valueEffective(char blocked_sign) const;

    /*
     * healingEffective:
     * Returns true if the set can heal against the current block sign.
     * Healing is effective only if the set has H and the enemy does not block 'H'.
     */
    bool healingEffective(char blocked_sign) const;

    /*
     * damageEffective:
     * Returns true if the set can deal damage against the current block sign.
     * Damage is effective only if the set has D and the enemy does not block 'D'.
     */
    bool damageEffective(char blocked_sign) const;


};


#endif //ASSIGNMENT5_CARDSET_H