//
// Created by Bar Hana Yehezkel on 14/01/2026.
//

#include "Creature.h"
#include "GameExceptions.h"

/*
 * setHealthPoints:
 * Sets the creature's current health to h_p.
 * Throws InvalidHealthPoints if h_p is negative.
 * If h_p is higher than max health, sets health to max health.
 */
void Creature::setHealthPoints(int h_p)
{
    if (h_p < 0)
    {
        throw InvalidHealthPoints("health_points cannot be negative");
    }
    if (h_p > max_health_points)
    {
        health_points = max_health_points;
    }
    else
    {
        health_points = h_p;
    }
}

/*
 * setMaxPoints:
 * Sets the creature's max health to max_h_p.
 * Throws InvalidHealthPoints if max_h_p is negative.
 * If the new max is lower than current health, current health is lowered to the new max.
 */
void Creature::setMaxPoints(int max_h_p)
{
    if (max_h_p < 0)
    {
        throw InvalidHealthPoints("max_health_points cannot be negative");
    }
    if (max_h_p < health_points)
    {
        health_points = max_h_p;
    }
    else
    {
        max_health_points = max_h_p;
    }

}

/*
 * takeDamage:
 * Lowers the creature's health by the given amount.
 * If amount is 0 or negative, does nothing.
 * Health will not go below 0.
 */

void Creature :: takeDamage(int amount)
{
    if (amount <= 0) return;
    health_points -= amount;
    if (health_points < 0) health_points = 0;
}
