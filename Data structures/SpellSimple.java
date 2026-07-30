public class SpellSimple {
    /**
     * A class that represents a spell structure.
     * Each spell has a name and words that must be said to activate it.
     */
    private String name;//spell name
    private String words;//words that must be said to activate
    //Spell constructor by name and words
    SpellSimple(String name, String words) {
        this.name = name;
        this.words = words;
    }
    /**
     * Returns the name of the spell.
     * @return spell name
     */
    public String getName(){
        return this.name;
    }
    /**
     * Returns the words of the spell.
     * @return the words to be said to cast the spell
     */
    public String getWords(){
        return this.words;
    }
}