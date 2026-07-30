//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#ifndef ASSIGNMENT5_ENEMY_H
#define ASSIGNMENT5_ENEMY_H
#include "Creature.h"
class Character;

/*
 * Enemy:
 * Base class for enemies in the game.
 * Inherits from Creature and adds damage points.
 * Each enemy can tell what block sign a given character uses against it.
 */
class Enemy : public Creature
{
protected:
    int damage_points;
    Enemy() : Creature(), damage_points(0){}
    Enemy(int health_points_max, int damage_points) : Creature(health_points_max), damage_points(damage_points){}
public:

    /*
     * ~Enemy:
     * Virtual destructor for Enemy.
     * Allows deleting derived enemies through an Enemy pointer.
     */
    ~Enemy() override = default;

    /*
     * getDamagePoints:
     * Returns how much damage this enemy deals.
     */
    int getDamagePoints() const { return damage_points; }

    /*
     * blockedSignFor:
     * Returns the block sign that the given character uses against this enemy.
     * Implemented by each specific enemy type.
     */
    virtual char blockedSignFor(const Character& c) const = 0;
};


#endif //ASSIGNMENT5_ENEMY_H