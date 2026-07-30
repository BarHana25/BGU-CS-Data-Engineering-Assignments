import java.util.LinkedList;
import java.util.List;
/**
 * Implements a hash table where each bucket is a linked list of AVL trees.
 * Each AVL tree in the list represents a specific spell category.
 * Used to store and search spells based on their category and power level.
 */
public class HashAVLSpellTable {
    private LinkedList<AVLTree> buckets[];
    private int tableSize;
    private int numSpells;
    /**
     * Constructor for the hash table.
     * Initializes each bucket with an empty linked list.
     * @param size the number of buckets in the table
     */
    public HashAVLSpellTable(int size) {
        this.tableSize = size;
        this.numSpells = 0;
        this.buckets = new LinkedList[this.tableSize];
        for (int i = 0; i < this.tableSize; i++) {
            this.buckets[i] = new LinkedList<>();
        }
    }
    /**
     * Hash function for categories.
     * Sums the ASCII values of characters in the category and modulu by table size.
     * @param category the spell category
     * @return index in the buckets array
     */
    private int hash(String category) {
        int h = 0;
        for (char c : category.toCharArray()) {
            h = h + c;
        }
        return h % this.tableSize;
    }
    /**
     * Adds a spell to the appropriate AVL tree in the hash table.
     * If the tree does not exist for the category, a new tree is created.
     * No duplicate spell (same name and power) is inserted.
     * @param s the spell to add
     */
    public void addSpell(Spell s) {
        int h = hash(s.getCategory());
        LinkedList<AVLTree> bucket = this.buckets[h];
        // Look for an existing AVL tree with the same category
        for (AVLTree b : bucket) {
            if (b.getCategory().equals(s.getCategory())) {
                // Only insert if the spell doesn't already exist
                if (b.search(s.getName(), s.getPowerLevel()) == null) {
                    b.insert(s);
                    this.numSpells++;
                }
                return;
            }
        }
        // If no tree for this category yet then create new tree and add it
        AVLTree newB = new AVLTree(s);
        bucket.add(newB);
        this.numSpells++;
    }
    /**
     * Searches for a specific spell in a given category by name and power level.
     * @param category the spell category
     * @param spellName the spell name
     * @param powerLevel the spell power level
     * @return the matching Spell if found, otherwise null
     */
    public Spell searchSpell(String category, String spellName, int powerLevel) {
        int h = hash(category);
        LinkedList<AVLTree> bucket = this.buckets[h];
        for (AVLTree b : bucket) {
            if (b.getCategory().equals(category)) {
                return b.search(spellName, powerLevel);
            }
        }
        return null;
    }
    /**
     * Returns the total number of spells in the hash table.
     * @return total spell count
     */
    public int getNumberSpells(){
        return this.numSpells;
    }
    /**
     * Returns the number of spells for a specific category.
     * @param category the spell category
     * @return number of spells in that category
     */
    public int getNumberSpells(String category){
        int h = hash(category);
        LinkedList<AVLTree> bucket = this.buckets[h];
        for (AVLTree b : bucket) {
            if (b.getCategory().equals(category)) {
                return b.getSize();
            }
        }
        return 0;
    }
    /**
     * Returns a list of the top-k most powerful spells from a given category.
     * If there are fewer than k spells, returns all of them.
     * @param category the spell category
     * @param k number of top spells to return
     * @return list of top-k spells, or null if category does not exist
     */
    public List<Spell> getTopK(String category, int k) {
        int h = hash(category);
        LinkedList<AVLTree> bucket = this.buckets[h];
        for (AVLTree b : bucket) {
            if (b.getCategory().equals(category)) {
                return b.getTopK(k);
            }
        }
        return null;
    }
}
