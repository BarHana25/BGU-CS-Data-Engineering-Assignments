import java.util.*;

public class TesterPart2 {
    public static void main(String[] args) {
        // Create HashAVLSpellTable with small bucket count to force collisions
        HashAVLSpellTable hashTable = new HashAVLSpellTable(3);

        // Spells to insert
        Spell fire1 = new Spell("SpellA", "Fire", 5, "castA");
        Spell sun1  = new Spell("SpellB", "Sun", 6, "castB");
        Spell air1  = new Spell("SpellC", "Air", 3, "castC");
        Spell earth1= new Spell("SpellD", "Earth", 4, "castD");
        Spell fire2 = new Spell("SpellE", "Fire", 7, "castE"); // same category Fire, higher power
        Spell water1= new Spell("SpellF", "Water", 2, "castF");
        Spell fire3 = new Spell("SpellG", "Fire", 7, "castG"); // Fire duplicate power
        Spell earth2= new Spell("SpellH", "Earth", 4, "castH"); // Earth duplicate power

        // Insert spells into the hash table
        hashTable.addSpell(fire1);
        hashTable.addSpell(sun1);
        hashTable.addSpell(air1);
        hashTable.addSpell(earth1);
        hashTable.addSpell(fire2);
        hashTable.addSpell(water1);
        hashTable.addSpell(fire3);
        hashTable.addSpell(earth2);

        // Test: total number of spells
        System.out.println("Total spells expected 8, got " + hashTable.getNumberSpells());

        // Test: number of spells per category
        System.out.println("Number of 'Fire' spells expected 3, got " + hashTable.getNumberSpells("Fire"));
        System.out.println("Number of 'Air' spells expected 1, got " + hashTable.getNumberSpells("Air"));
        System.out.println("Number of 'Wind' spells (non-existent) expected 0 or handled, got "
                + hashTable.getNumberSpells("Wind"));

        // Test: searchSpell (hits and misses)
        Spell searchResult1 = hashTable.searchSpell("Fire", "SpellE", 7);
        System.out.println("Search existing SpellE in Fire: expected non-null, got " + searchResult1);
        Spell searchResult2 = hashTable.searchSpell("Fire", "SpellF", 7);
        System.out.println("Search non-existent SpellF in Fire: expected null, got " + searchResult2);
        Spell searchResult3 = hashTable.searchSpell("Sun", "SpellB", 6);
        System.out.println("Search existing SpellB in Sun: expected non-null, got " + searchResult3);
        Spell searchResult4 = hashTable.searchSpell("Earth", "SpellD", 3);
        System.out.println("Search wrong power SpellD (should be 4): expected null, got " + searchResult4);
        Spell searchResult5 = hashTable.searchSpell("Wind", "SpellX", 1);
        System.out.println("Search in non-existent category Wind: expected null, got " + searchResult5);

        // Test: Spell.toString()
        Spell spTest = new Spell("Name", "MyCat", 9, "hello");
        System.out.println("Spell toString expected \"Name (MyCat) - Power Level: 9, to cast say: hello\", got \"" + spTest + "\"");

        // Test: getTopK with various K values for category "Fire"
        List<Spell> top0Fire = hashTable.getTopK("Fire", 0);
        System.out.println("Top 0 Fire spells: expected [], got " + top0Fire);
        List<Spell> top2Fire = hashTable.getTopK("Fire", 2);
        System.out.println("Top 2 Fire spells: expected [SpellE, SpellG] (power 7), got " + top2Fire);
        List<Spell> top5Fire = hashTable.getTopK("Fire", 5);
        System.out.println("Top 5 Fire spells: expected all 3 Fire spells sorted, got " + top5Fire);

        // Test: getTopK for a non-existent category
        List<Spell> topAny = hashTable.getTopK("NonCat", 3);
        System.out.println("TopK on non-existent category: expected null, got " + topAny);

        // Test: getTopK for category "Earth"
        List<Spell> top1Earth = hashTable.getTopK("Earth", 1);
        System.out.println("Top 1 Earth spells expected [highest power Earth], got " + top1Earth);
        List<Spell> top2Earth = hashTable.getTopK("Earth", 2);
        System.out.println("Top 2 Earth spells expected 2 spells, got " + top2Earth);
        List<Spell> top10Earth = hashTable.getTopK("Earth", 10);
        System.out.println("Top 10 Earth spells (k > size) expected both spells, got " + top10Earth);

        // Directly test AVLTree balancing
        // 1) LL rotation (3,2,1)
        AVLTree treeLL = new AVLTree(new Spell("X", "Cat", 3, "w"));
        treeLL.insert(new Spell("X", "Cat", 2, "w"));
        treeLL.insert(new Spell("X", "Cat", 1, "w"));
        System.out.println("AVL LL rotation height expected 2, got " + treeLL.getTreeHeight() +
                "; size expected 3, got " + treeLL.getSize());

        // 2) RR rotation (1,2,3)
        AVLTree treeRR = new AVLTree(new Spell("X", "Cat", 1, "w"));
        treeRR.insert(new Spell("X", "Cat", 2, "w"));
        treeRR.insert(new Spell("X", "Cat", 3, "w"));
        System.out.println("AVL RR rotation height expected 2, got " + treeRR.getTreeHeight() +
                "; size expected 3, got " + treeRR.getSize());

        // 3) LR rotation (3,1,2)
        AVLTree treeLR = new AVLTree(new Spell("X", "Cat", 3, "w"));
        treeLR.insert(new Spell("X", "Cat", 1, "w"));
        treeLR.insert(new Spell("X", "Cat", 2, "w"));
        System.out.println("AVL LR rotation height expected 2, got " + treeLR.getTreeHeight() +
                "; size expected 3, got " + treeLR.getSize());

        // 4) RL rotation (1,3,2)
        AVLTree treeRL = new AVLTree(new Spell("X", "Cat", 1, "w"));
        treeRL.insert(new Spell("X", "Cat", 3, "w"));
        treeRL.insert(new Spell("X", "Cat", 2, "w"));
        System.out.println("AVL RL rotation height expected 2, got " + treeRL.getTreeHeight() +
                "; size expected 3, got " + treeRL.getSize());

        // Test: inserting duplicate power in AVLTree
        int sizeBefore = treeLL.getSize();
        treeLL.insert(new Spell("Y", "Cat", 2, "dup"));  // duplicate power level 2
        int sizeAfter = treeLL.getSize();
        System.out.println("AVL insert duplicate power: size expected unchanged, got before="
                + sizeBefore + ", after=" + sizeAfter +
                "; height now " + treeLL.getTreeHeight());
    }
}