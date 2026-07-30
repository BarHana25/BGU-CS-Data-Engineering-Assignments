public class Tester{
    public static void main(String[] args) {
        testDoubleHashTable();
        testAVLTree();
        testHashAVLSpellTable();
    }
    private static void printTestResult(boolean condition, int testNum) {
        System.out.println("Test " + testNum + ": " + (condition ? "true" : "false"));
    }
    // DoubleHashTable
    private static void testDoubleHashTable() {
        System.out.println("\n--- Testing DoubleHashTable ---");
        DoubleHashTable table = new DoubleHashTable(5);
        SpellSimple s1 = new SpellSimple("fire", "burn");
        SpellSimple s2 = new SpellSimple("ice", "freeze");
        SpellSimple s3 = new SpellSimple("frost", "chill");
        SpellSimple s4 = new SpellSimple("stone", "solidify");
        // Test 1: Insert one spell
        boolean t1 = table.put(s1) && table.getSize() == 1;
        printTestResult(t1, 1);
        // Test 2: Get spell by name
        boolean t2 = table.getCastWords("fire").equals("burn") && table.getLastSteps() == 0;
        printTestResult(t2, 2);
        // Test 3: Insert another spell (collision not guaranteed)
        boolean t3 = table.put(s2) && table.getSize() == 2;
        printTestResult(t3, 3);
        // Test 4: Get spell that doesn't exist
        boolean t4 = table.getCastWords("nope") == null;
        printTestResult(t4, 4);
        // Test 5: Insert duplicate name
        boolean t5 = table.put(new SpellSimple("fire", "different")) && table.getSize() == 3;
        printTestResult(t5, 5);
    }
    // AVLTree
    private static void testAVLTree() {
        System.out.println("\n--- Testing AVLTree ---");
        Spell sp1 = new Spell("A", "fire", 10, "a1");
        Spell sp2 = new Spell("B", "fire", 20, "a2");
        Spell sp3 = new Spell("C", "fire", 30, "a3");
        AVLTree tree = new AVLTree(sp2);
        // Test 6: insert one node
        boolean t6 = tree.getSize() == 1 && tree.getTreeHeight() == 0;
        printTestResult(t6, 6);
        // Test 7: insert to test balancing
        tree.insert(sp3);
        tree.insert(sp1);
        boolean t7 = tree.getSize() == 3 && tree.getTreeHeight() <= 3;
        printTestResult(t7, 7);
        // Test 8: search existing spell
        Spell found = tree.search("B", 20);
        boolean t8 = found != null && found.getName().equals("B");
        printTestResult(t8, 8);
        // Test 9: getTopK more than size
        boolean t9 = tree.getTopK(5).size() == 3;
        printTestResult(t9, 9);
        // Test 10: getTopK
        boolean t10 = tree.getTopK(3).get(0).getPowerLevel() == 30;
        printTestResult(t10, 10);
    }
    // HashAVLSpellTable
    private static void testHashAVLSpellTable() {
        System.out.println("\n--- Testing HashAVLSpellTable ---");
        HashAVLSpellTable table = new HashAVLSpellTable(5);
        Spell s1 = new Spell("A", "fire", 10, "say1");
        Spell s2 = new Spell("B", "fire", 20, "say2");
        Spell s3 = new Spell("C", "ice", 15, "say3");
        // Test 11: add to new category
        table.addSpell(s1);
        boolean t11 = table.getNumberSpells("fire") == 1;
        printTestResult(t11, 11);
        // Test 12: add more spells to same category
        table.addSpell(s2);
        boolean t12 = table.getNumberSpells("fire") == 2;
        printTestResult(t12, 12);
        // Test 13: search spell
        Spell found = table.searchSpell("fire", "B", 20);
        boolean t13 = found != null && found.getName().equals("B");
        printTestResult(t13, 13);
        // Test 14: getTopK on category that doesn’t exist
        boolean t14 = table.getTopK("wind", 3) == null;
        printTestResult(t14, 14);
        // Test 15: check separation between categories
        table.addSpell(s3);
        boolean t15 = table.getNumberSpells("ice") == 1 && table.getNumberSpells() == 3;
        printTestResult(t15, 15);
    }
}
