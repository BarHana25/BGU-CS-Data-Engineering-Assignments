//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_GAMEEXCEPTIONS_H
#define ASSIGNMENT5_GAMEEXCEPTIONS_H
#include <stdexcept>
#include <string>
#include <exception>

/*
 * DeckRanOut:
 * Exception thrown when trying to draw a card but the deck is empty.
 */
class DeckRanOut : public std::runtime_error {
public:
    DeckRanOut() : std::runtime_error("Deck ran out") {}
};

/*
 * BadCardSetInput:
 * Exception thrown when the given card set is not valid for the action.
 * For example: trying to play cards that are not in the hand.
 * msg explains what was wrong.
 */
class BadCardSetInput : public std::invalid_argument
{
public:
    explicit BadCardSetInput(const std::string& msg)
        : std::invalid_argument(msg) {}
};

/*
 * InvalidHealthPoints:
 * Exception thrown when health values are not valid.
 * For example: negative health or negative max health.
 * msg explains what was wrong.
 */
class InvalidHealthPoints : public std::logic_error
{
public:
    explicit InvalidHealthPoints(const std::string& msg)
        : std::logic_error(msg) {}
};

/* MemoryProblem:
 * Exception thrown when a memory allocation failure occurs.
 * Used to signal a general Memory Error in the program.
 */
class MemoryProblem : public std::exception
{
public:
    const char* what() const noexcept override
    {
        return "Memory Error";
    }
};

#endif //ASSIGNMENT5_GAMEEXCEPTIONS_H