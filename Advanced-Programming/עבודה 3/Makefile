PokemonsBattleCenter: PokemonsBattleCenter.o Pokemon.o BattleByCategory.o MaxHeap.o LinkedList.o
	gcc PokemonsBattleCenter.o Pokemon.o BattleByCategory.o MaxHeap.o LinkedList.o -o PokemonsBattleCenter

PokemonsBattleCenter.o: PokemonsBattleCenter.c Defs.h MaxHeap.h BattleByCategory.h
	gcc -c PokemonsBattleCenter.c

MaxHeap.o: MaxHeap.c MaxHeap.h Defs.h
	gcc -c MaxHeap.c

Pokemon.o: Pokemon.c Pokemon.h
	gcc -c Pokemon.c

BattleByCategory.o: BattleByCategory.c BattleByCategory.h Defs.h MaxHeap.h Pokemon.h
	gcc -c BattleByCategory.c

LinkedList.o: LinkedList.c LinkedList.h
	gcc -c LinkedList.c

clean:
	rm -f *.o PokemonsBattleCenter
