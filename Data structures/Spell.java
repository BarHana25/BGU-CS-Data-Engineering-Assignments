public class Spell {
    /**
     * Represents a Spell with name, category, power level, and words.
     * Used in the AVL tree and HashAVLSpellTable data structures.
     * The spell can be searched and sorted based on its power level.
     */
    private String name; // spell name
    private String category; // spell category
    private int powerLevel; // spell power
    private String words;// spell words
    /**
     * Constructor for a Spell object.
     * @param name the name of the spell
     * @param category the category the spell belongs to
     * @param powerLevel the power level of the spell
     * @param words the words used to cast the spell
     */
    public Spell(String name, String category, int powerLevel, String words) {
        this.name = name;
        this.category = category;
        this.powerLevel = powerLevel;
        this.words = words;
    }
    /**
     * Getter for the spell's name.
     * @return name of the spell
     */
    public String getName() {
        return this.name;
    }
    /**
     * Getter for the spell's category.
     * @return category of the spell
     */
    public String getCategory() {
        return this.category;
    }
    /**
     * Getter for the spell's power level.
     * @return power level of the spell
     */
    public int getPowerLevel() {
        return this.powerLevel;
    }
    /**
     * Returns a string representation of the spell (used in testing).
     * @return a readable string describing the spell
     */
    @Override
    public String toString() {
        return name + " (" + category + ") - Power Level: " + powerLevel + ", to cast say: " + words;
    }
}
