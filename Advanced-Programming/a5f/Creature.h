//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_CREATURE_H
#define ASSIGNMENT5_CREATURE_H

/*
 * Creature:
 * Base class for any creature in the game.
 * Stores current health points and max health points.
 * Gives simple getters and setters, and a takeDamage function.
 */
class Creature
{
protected:
    int health_points;
    int max_health_points;
    Creature(): health_points(0), max_health_points(0) {}
    explicit Creature(int max_health_points) : health_points(max_health_points), max_health_points(max_health_points){}
public:
    /*
     * ~Creature:
     * Virtual destructor for Creature.
     * Allows deleting derived objects through a Creature pointer.
     */
    virtual ~Creature() = default;

    /*
    * getHealthPoints:
    * Returns the current health points of the creature.
    */
    int getHealthPoints() const {return health_points;}

    /*
     * getMaxHealthPoints:
     * Returns the max health points of the creature.
     */
    int getMaxHealthPoints() const { return max_health_points;}
    /*
     * setHealthPoints:
     * Sets the current health points to h_p.
     * Should keep the value in a valid range.
     */
    void setHealthPoints(int h_p) ;
    /*
     * setMaxPoints:
     * Sets the max health points to max_h_p.
     * If the current health is bigger than the new max, it should be adjusted down to the new max.
     */
    void setMaxPoints(int max_h_p) ;
    /*
     * takeDamage:
     * Reduces the creature's health by the given amount.
     * If the amount is bigger than the current health, health should not go below 0.
     */
    void takeDamage(int amount);

};


#endif //ASSIGNMENT5_CREATURE_H