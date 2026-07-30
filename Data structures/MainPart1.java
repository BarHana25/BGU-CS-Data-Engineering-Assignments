public class MainPart1 {
    public static void main(String[] args) {
        DoubleHashTable table = new DoubleHashTable(7);

        // Add some spells to the table
        table.put(new SpellSimple("Abracadabra", "Avada Kedavra"));
        table.put(new SpellSimple("Expecto Patronum", "I’m gonna stand here like a unicorn"));
        table.put(new SpellSimple("Wingardium Leviosa", "Get up, stand up"));
        table.put(new SpellSimple("Shazam", "24K Magic in the air"));

        // Get the spells by name
        System.out.println(table.getCastWords("Shazam")); // prints "24K Magic in the air"
        System.out.println(table.getCastWords("Abracadabra")); // prints "Avada Kedavra"

        // Get the size of the table
        int size = table.getSize();
        System.out.println("Table size: " + size); // prints "Table size: 4"
    }
}