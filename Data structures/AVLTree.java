import java.util.ArrayList;
import java.util.List;

public class AVLTree {
    /**
     * Implements an AVL Tree where each node stores a Spell object.
     * The tree represents a specific spell category.
     * Nodes are ordered by the spell's powerLevel.
     * The tree maintains balance after every insertion to ensure efficient operations.
     */
    private Node root; // Root of the AVL tree
    private int size; // Number of spells in the tree
    private String category; // The category of the tree
	
	// private Node class for the AVL Tree nodes
    /**
     * Inner private class representing a node in the AVL tree.
     * Each node holds a Spell, left and right children, and a height.
     */
    private class Node { 
        private Spell spell;  // The spell stored in the node
        private Node left; // Left child
        private Node right; // Right child
        private int height; // Height of the node
        // Constructs a new node with a given spell
        private Node(Spell spell) {
            this.spell = spell;
            this.left = null;
            this.right = null;
            this.height = 0;
        }
    }
    // Constructor, getters, setters
    /**
     * Constructs a new AVLTree with the first spell.
     * Initializes the category based on the spell's category.
     * @param spell the first spell to insert into the tree
     */
    public AVLTree(Spell spell) {
        this.root = new Node(spell);
        this.size = 1;
        this.category = spell.getCategory();
    }
    /**
     * Returns the height of the AVL tree.
     * @return the height of the tree
     */
    public int getTreeHeight(){
        return getHeight(root);
    }

    /**
     * helper to get the tree height
     * @param node
     * @return specific nod height
     */
    private int getHeight(Node node) {
        if (node == null) {
            return -1;
        } else {
            return node.height;
        }
    }
    /**
     * Returns the number of spells currently stored in the tree.
     * @return the size of the tree
     */
    public int getSize(){
        return this.size;
    }
    /**
     * Returns the category this tree represents.
     * @return the spell category
     */
    public String getCategory() {
        return this.category; }
    /**
     * Searches the tree for a spell with the given name and power level.
     * @param spellName the name of the spell to search
     * @param powerLevel the power level of the spell
     * @return the matching Spell if found, null otherwise
     */
    public Spell search(String spellName, int powerLevel) {
        return searchRec(root, spellName, powerLevel);
    }
    // Recursive helper for search
    private Spell searchRec(Node node, String spellName, int powerLevel) {
        if (node == null) {
            return null;
        }
        int currPower = node.spell.getPowerLevel();
        if (currPower > powerLevel) {
            return searchRec(node.left, spellName, powerLevel);
        } else if (currPower < powerLevel) {
            return searchRec(node.right, spellName, powerLevel);
        } else { if (node.spell.getName().equals(spellName)) {
                    return node.spell;
               } else {
                    return null;
               }
        }
    }
    // Right rotation to restore AVL balance
    private Node rotateRight(Node node) {
        Node leftC = node.left;
        Node temp = leftC.right;
        leftC.right = node;
        node.left = temp;
        // Update heights
        node.height = Math.max(getHeight(node.left), getHeight(node.right)) + 1;
        leftC.height = Math.max(getHeight(leftC.left), getHeight(leftC.right)) + 1;

        System.out.println("Rotation result: " + leftC.spell.getName() + ", height: " + leftC.height);


        return leftC;
    }
    // Left rotation to restore AVL balance
    private Node rotateLeft(Node node) {
        Node rightC = node.right;
        Node temp = rightC.left;
        rightC.left = node;
        node.right = temp;
        // Update heights
        node.height = Math.max(getHeight(node.left), getHeight(node.right)) + 1;
        rightC.height = Math.max(getHeight(rightC.left), getHeight(rightC.right)) + 1;

        System.out.println("Rotation result: " + rightC.spell.getName() + ", height: " + rightC.height);

        return rightC;
    }
    /**
     * Inserts a new spell into the AVL tree.
     * Maintains balance according to AVL rules.
     * @param spell the spell to insert
     */
    public void insert(Spell spell) {
        this.root = insertRec(root, spell);
        size++;
    }
    // Recursive insert with balancing
    private Node insertRec(Node node , Spell spell) {
        if (node == null) {
            return new Node(spell);
        }
        int newPower = spell.getPowerLevel();
        int currPower = node.spell.getPowerLevel();
        if (newPower < currPower) {
            node.left = insertRec(node.left, spell);
        }else if (newPower > currPower) {
            node.right = insertRec(node.right, spell);
        } else {
            return node;// Duplicate powerLevel, do not insert
        }
        // Update height
        node.height = Math.max(getHeight(node.left),getHeight(node.right)) + 1;
        // Calculate balance factor
        int balance = getHeight(node.left) - getHeight(node.right);
        // Perform rotations if unbalanced
        if (balance >1 && newPower <node.left.spell.getPowerLevel()) {
            return rotateRight(node); // Left Left Case
        }
        if (balance <-1 && newPower > node.right.spell.getPowerLevel()) {
            return rotateLeft(node); // Right Right Case
        }
        if (balance > 1 && newPower > node.left.spell.getPowerLevel()) {
            node.left = rotateLeft(node.left);
            return rotateRight(node); // Left Right Case
        }
        if (balance <-1 && newPower < node.right.spell.getPowerLevel()) {
            node.right = rotateRight(node.right);
            return rotateLeft(node); // Right Left Case
        }
        return node;
    }
    /**
     * Returns a list of the top k most powerful spells in the tree.
     * Ordered from highest to lowest powerLevel.
     * @param k the number of top spells to return
     * @return list of top k spells
     */
    public List<Spell> getTopK(int k) {
        List<Spell> kSpells = new ArrayList<>();
        if (k>=this.size) {
            k = this.size;
        }
        getTopKRec(root, k, kSpells);
        return kSpells;
    }
    // Reverse inorder to get top k largest spells
    private void getTopKRec(Node node, int k, List<Spell> kSpells) {
        if (node == null || kSpells.size()>=k) {
            return;
        }
        getTopKRec(node.right, k, kSpells); // Visit right subtree first (larger)
        if (kSpells.size()<k) {
            kSpells.add(node.spell);
        }
        getTopKRec(node.left, k, kSpells); // Then visit left
    }
}


