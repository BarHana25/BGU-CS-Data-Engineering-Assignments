Decks_game: Card.o Deck.o CardSet.o Character.o Creature.o Troll.o Dragon.o Ghost.o main.o
	g++ Card.o Deck.o CardSet.o Character.o Creature.o Troll.o Dragon.o Ghost.o main.o -o Decks_game

Card.o: Card.cpp Card.h
	g++ -c Card.cpp

Deck.o: Deck.cpp Deck.h Card.h
	g++ -c Deck.cpp

CardSet.o: CardSet.cpp CardSet.h Card.h
	g++ -c CardSet.cpp

Character.o: Character.cpp Character.h
	g++ -c Character.cpp

Creature.o: Creature.cpp Creature.h
	g++ -c Creature.cpp

Troll.o: Troll.cpp Troll.h
	g++ -c Troll.cpp

Dragon.o: Dragon.cpp Dragon.h
	g++ -c Dragon.cpp

Ghost.o: Ghost.cpp Ghost.h
	g++ -c Ghost.cpp

main.o: main.cpp
	g++ -c main.cpp

clean:
	rm -f *.o Decks_game
