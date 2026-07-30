public class Tester3 {

    public static void main(String[] args) {
        System.out.println("Running AVLTree height test...");

        Spell s1 = new Spell("a", "fire", 10, "burn");
        Spell s2 = new Spell("b", "fire", 5, "heat");
        Spell s3 = new Spell("c", "fire", 15, "flame");

        AVLTree tree = new AVLTree(s1);
        System.out.println("Test 1 - Tree with 1 node:");
        System.out.println("Expected height: 0 | Actual: " + tree.getTreeHeight());

        tree.insert(s2); // הכנסה שמאלית
        System.out.println("Test 2 - Tree with 2 nodes:");
        System.out.println("Expected height: 1 | Actual: " + tree.getTreeHeight());

        tree.insert(s3); // הכנסה ימנית → אמור להפעיל איזון
        System.out.println("Test 3 - Tree with 3 nodes:");
        System.out.println("Expected height: 1 or 2 depending on rotation | Actual: " + tree.getTreeHeight());

        Spell s4 = new Spell("d", "fire", 20, "boom");
        tree.insert(s4);
        System.out.println("Test 4 - Tree with 4 nodes:");
        System.out.println("Expected height: 2 | Actual: " + tree.getTreeHeight());

        Spell s5 = new Spell("e", "fire", 25, "flash");
        tree.insert(s5);
        System.out.println("Test 5 - Tree with 5 nodes:");
        System.out.println("Expected height: 3 | Actual: " + tree.getTreeHeight());
    }
}


