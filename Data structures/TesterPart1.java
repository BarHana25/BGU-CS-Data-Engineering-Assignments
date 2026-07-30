import java.util.concurrent.atomic.AtomicInteger;

public class TesterPart1 {
    public static void main(String[] args) {
        DoubleHashTable table = new DoubleHashTable(5);

        AtomicInteger tests  = new AtomicInteger(0);
        AtomicInteger passed = new AtomicInteger(0);

        java.util.function.BiConsumer<String,Boolean> check = (msg, ok) -> {
            tests.getAndIncrement();
            if (ok) passed.getAndIncrement();
            System.out.println((ok ? "✓ " : "✗ ") + msg);
        };

        //―――――― Test data setup ――――――
        SpellSimple s1   = new SpellSimple("abc", "words1");
        SpellSimple sDup = new SpellSimple("abc", "wordsDup");
        SpellSimple s2   = new SpellSimple("ahb", "words2");
        SpellSimple s3   = new SpellSimple("hey", "words3");

        //―――――― Test1: first insert → i=0 ――――――
        boolean r1 = table.put(s1);
        check.accept(
                "Test1 insert('abc'): true, size=1, steps=0",
                r1 && table.getSize()==1 && table.getLastSteps()==0
        );

        //―――――― Test2: duplicate-name allowed → i=1 ――――――
        boolean r2 = table.put(sDup);
        check.accept(
                "Test2 insert duplicate-name('abc'): true, size=2, steps=1",
                r2 && table.getSize()==2 && table.getLastSteps()==1
        );

        //―――――― Test3: collision insert ('ahb') → i=1 ――――――
        boolean r3 = table.put(s2);
        check.accept(
                "Test3 insert('ahb'): true, size=3, steps=1",
                r3 && table.getSize()==3 && table.getLastSteps()==1
        );

        //―――――― Test4: no-collision insert ('hey') → i=0 ――――――
        boolean r4 = table.put(s3);
        check.accept(
                "Test4 insert('hey'): true, size=4, steps=0",
                r4 && table.getSize()==4 && table.getLastSteps()==0
        );

        //―――――― Test5: getCastWords at h1 ('abc') → i=0 ――――――
        String w1 = table.getCastWords("abc");
        check.accept(
                "Test5 getCastWords('abc'): 'words1', steps=0",
                "words1".equals(w1) && table.getLastSteps()==0
        );

        //―――――― Test6: getCastWords collision ('ahb') → i=1 ――――――
        String w2 = table.getCastWords("ahb");
        check.accept(
                "Test6 getCastWords('ahb'): 'words2', steps=1",
                "words2".equals(w2) && table.getLastSteps()==1
        );

        //―――――― Test7: miss ('xxx') → i=3 ――――――
        String w3 = table.getCastWords("xxx");
        check.accept(
                "Test7 getCastWords('xxx'): null, steps=3",
                w3 == null && table.getLastSteps()==3
        );

        //―――――― Summary ――――――
        System.out.println();
        System.out.printf("Passed %d / %d tests%n",
                passed.get(), tests.get());
    }
}