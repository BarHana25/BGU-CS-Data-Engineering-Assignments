public class DoubleHashTable {
    /**
     * Represents a hash table with double hashing.
     * Each cell in the table can contain an object of type SpellSimple.
     * The table supports adding a spell (put) and searching for a spell by name (getCastWords),
     * while maintaining the number of steps taken in the last operation.
     */
    private SpellSimple[] table;
    private int capacity;
    private int size;
    private int steps=0;

    /**
     * Constructor for a hash table of a given size
     * @param capacity
     */
    public DoubleHashTable(int capacity) {
        this.capacity = capacity;
        this.size = 0;
        this.steps = 0;
        this.table = new SpellSimple[capacity];
    }
    /**
     * Attempts to insert a new spell into the table based on the hash value.
     * If there is a conflict, double hashing is used to find an empty cell.
     * @param spell The spell to insert
     * @return true if successful, false if the cell is occupied and no space was found
     */
    public boolean put(SpellSimple spell) {
        int h1 = hash1(spell.getName());
        int h2 = hash2(spell.getName());
        // tries to find an empty space in the table (up to the size of the table attempts)
        for (int i = 0; i < this.capacity; i++) {
            this.steps = i;
            int index = (h1+i*h2) % this.capacity;
            if (table[index] == null) {
                table[index] = spell;
                size++;
                return true;
            }
        }
        return false;// if didn't succeed to find a spot
    }
    /**
     * Searches for a spell by spell name.
     * @param name The spell name to search for
     * @return The spell words if found, null otherwise
     */
    public String getCastWords(String name) {
        int h1 = hash1(name);
        int h2 = hash2(name);
        //Trying to find the spell by hash position
        for (int i = 0; i < this.capacity; i++) {
            this.steps = i; // updates steps
            int index = (h1+ i*h2) % this.capacity;
            if (table[index] == null) {
                return null; // stops if not fund
            }
            if (table[index].getName().equals(name)) {
                return table[index].getWords();// if fund return the words of the spell
            }
        }
        steps = this.capacity;
        return null; // not found in full search
    }

    /**
     * Returns the number of spells in the table
     * @return the number of spells in the table
     */
    public int getSize() {
        return this.size;
    }
    /**
     * Returns the number of steps taken in the last operation (put or getCastWords).
     * @return last number of steps
     */
    public int getLastSteps() {
        return this.steps; }
    /**
     * First hash function based on ASCII sum multiplied by 31.
     * @param name The spell string
     * @return First hash value
     */
    private int hash1(String name) {
        int h1 = 0;
        for (int i = 0; i < name.length(); i++) {
            char c = name.charAt(i);
            h1 = h1 + c * 31;
        }
        return h1 % this.capacity;
    }
    /**
     * Second hash function based on ASCII sum multiplied by 13.
     * @param name The spell string
     * @return Second hash value
     */
    private int hash2(String name) {
        int h2 = 0;
        for (int i = 0; i < name.length(); i++) {
            char c = name.charAt(i);
            h2 = h2 + c * 13;
        }
        return 1 + h2 % (this.capacity - 2);
    }
}