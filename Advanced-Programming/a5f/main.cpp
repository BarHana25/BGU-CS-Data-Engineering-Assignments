//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#include <iostream>
using namespace std;
#include <string>
#include <new> //to catch bad_alloc
#include "Deck.h"
#include "CardSet.h"
#include "Fighter.h"
#include "Wizard.h"
#include "Bowman.h"
#include "Troll.h"
#include "Dragon.h"
#include "Ghost.h"
#include "GameExceptions.h"

/* readLine:
 * Reads one full line from input into 'line'.
 * Returns false when input ends.
 */
static bool readLine(std::string& line)
{
    return static_cast<bool>(std::getline(std::cin, line));
}

/* readIntChoice:
 * Reads an int from input.
 */
static int readIntChoice()
{ //dont need to check input
    int choice;
    std::cin >> choice;
    std::string remaining;
    std::getline(std::cin, remaining);
    return choice;
}

/* createDeckFromLines:
 * Builds the deck from input lines until 00.
 * Each line should be a single card. Bad lines are ignored.
 */
static Deck createDeckFromLines()
{
    std::cout << "Initialize deck" << std::endl;
    Deck deck;
    std::string line;
    while (readLine(line))
    {
        if (line == "00") break;
        try
        {
            CardSet tempCardSet(line);
            const auto& cards = tempCardSet.getCards();
            if (cards.size() == 1) //one card in line
            {
                deck +=cards[0];
            }
        }
        catch (const BadCardSetInput&)
        {
            // ignore in case of bad input line
        }
    }
    return deck;
}

/* main:
 * Runs the game:
 * - read deck
 * - choose player and enemy
 * - loop: player plays a set, then enemy attacks
 * If deck runs out: print "Deck ran out" and exit.
 * If memory fails: print "Memory Error" and exit.
 */
int main()
{
    try
    {
        Deck deck = createDeckFromLines();
        std::cout << "Choose player character:" << std::endl;
        std::cout << "(1) Fighter (2) Sorcerer (3) Ranger" << std::endl;
        int character_c = readIntChoice();
        std::cout << "Choose enemy character:" << std::endl;
        std::cout << "(1) Troll (2) Ghost (3) Dragon" << std::endl;
        int enemy_c = readIntChoice();
        //are created on the stack, to produce a pointer to the player's choice
        Fighter fighter;
        Wizard wizard;
        Bowman bowman;
        Character* character =
            (character_c == 1) ? static_cast<Character*>(&fighter) :
            (character_c == 2) ? static_cast<Character*>(&wizard) :
                                 static_cast<Character*>(&bowman);
        //are created on the stack, to produce a pointer to the player's choice for enemy
        Troll troll;
        Dragon dragon;
        Ghost ghost;
        Enemy* enemy =
            (enemy_c == 1) ? static_cast<Enemy*>(&troll) :
            (enemy_c == 2) ? static_cast<Enemy*>(&ghost) :
                            static_cast<Enemy*>(&dragon);
        character->reFillHand(deck); // first fill of the player's hand
        std::cout << "Player health: " << character->getHealthPoints() << std::endl;
        std::cout << "Enemy health: " << enemy->getHealthPoints() << std::endl;
        std::cout << "Player hand" << std::endl;
        character->printHand(std::cout);

        while (true)
        {
            std::cout << "Insert card set to play" << std::endl;
            std::string line;
            if (!readLine(line)) break; // if finish inserting cards
            if (line == "exit") return 0;
            try
            {
                CardSet temp_set(line);
                if (!temp_set.isLegal() || !character->canPlay(temp_set)) //check set and player's play
                {
                    std::cout << "Card set is not valid" << std::endl;
                    continue;
                }
                char blocked_sign = enemy->blockedSignFor(*character);
                int set_value = temp_set.valueEffective(blocked_sign); //player attack
                enemy->takeDamage(set_value);
                std::cout << "Player dealt " << set_value << " points of damage" << std::endl;
                if (enemy->getHealthPoints() <=0)
                {
                    std::cout << "Player won" << std::endl;
                    return 0;
                }
                if (temp_set.healingEffective(blocked_sign)) //if H
                {
                    int before = character->getHealthPoints();
                    character->heal(set_value);
                    int healed = character->getHealthPoints() - before;

                    if (healed > 0)
                    {
                        std::cout << "Player healed " << healed << " points of damage" << std::endl;
                    }
                }
                int damage_taken = enemy->getDamagePoints(); //enemy attack
                if (temp_set.damageEffective(blocked_sign))
                {
                    damage_taken -= set_value;
                }
                if (damage_taken < 0)
                {
                    damage_taken = 0;
                }
                character->takeDamage(damage_taken);
                std::cout << "Player took " << damage_taken << " points of damage" << std::endl;
                if (character->getHealthPoints() <= 0)
                {
                    std::cout << "Player lost" << std::endl;
                    return 0;
                }
                character->play(temp_set); //remove used cards
                character->drawCards(deck); //add cards
                std::cout << "Player health: " << character->getHealthPoints() << std::endl;
                std::cout << "Enemy health: " << enemy->getHealthPoints() << std::endl;
                std::cout << "Player hand" << std::endl;
                character->printHand(std::cout);
            }
            catch (const std::bad_alloc&)
            {
                throw MemoryProblem();
            }
            catch (const DeckRanOut&)
            {
                std::cout << "Deck ran out" << std::endl;
                return 0;
            }
            catch (const BadCardSetInput&)
            {
                std::cout << "Card set is not valid" << std::endl;
            }
        }
    }
    catch (const DeckRanOut&)
    {
        // can happen in the hand creat
        std::cout << "Deck ran out" << std::endl;
        return 0;
    }
    catch (const MemoryProblem& e)
    {
        std::cout << e.what() << std::endl;
        return 0;
    }
    return 0;
}