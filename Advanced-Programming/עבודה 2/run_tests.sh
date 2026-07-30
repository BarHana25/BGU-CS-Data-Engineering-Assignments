#!/bin/bash
# Automated test script for Pokedex edge cases

echo "======================================"
echo "POKEDEX EDGE CASE TESTING"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Compile
echo "Compiling..."
cc -Wall -Wextra Pokedex.c Pokemon.c -o Pokedex
if [ $? -ne 0 ]; then
    echo -e "${RED}Compilation failed!${NC}"
    exit 1
fi
echo -e "${GREEN}Compilation successful${NC}"
echo ""

# Test 1: Invalid input
echo "Test 1: Invalid menu input (i)"
echo -e "i\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Please choose a valid number"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 2: Invalid input (0)
echo "Test 2: Invalid menu input (0)"
echo -e "0\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Please choose a valid number"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 3: Non-existent type (option 3)
echo "Test 3: Non-existent type in option 3"
echo -e "3\nNotExist\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Type name doesn't exist"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 4: Non-existent type to add (option 3)
echo "Test 4: Non-existent type to add in option 3"
echo -e "3\nFire\nNotExist\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Type name doesn't exist"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 5: Type already exists (option 3)
echo "Test 5: Type already exists in option 3"
echo -e "3\nFire\nWater\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "This type already exist in the list"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 6: Successfully add type (option 3)
echo "Test 6: Successfully add type in option 3"
echo -e "3\nFire\nIce\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Ice"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 7: Non-existent pokemon (option 7)
echo "Test 7: Non-existent pokemon in option 7"
echo -e "7\nNotExist\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "The Pokemon doesn't exist"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 8: Valid pokemon (option 7)
echo "Test 8: Valid pokemon in option 7"
echo -e "7\nPikachu\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Pikachu :"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 9: Non-existent type (option 8)
echo "Test 9: Non-existent type in option 8"
echo -e "8\nNotExist\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Type name doesn't exist"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 10: Valid type with pokemons (option 8)
echo "Test 10: Valid type with pokemons in option 8"
echo -e "8\nFire\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "There are 2 Pokemons with this type"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 11: Print all pokemons (option 1)
echo "Test 11: Print all pokemons"
echo -e "1\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Pikachu :"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 12: Print all types (option 2)
echo "Test 12: Print all types"
echo -e "2\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Type Fire"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 13: Exit message
echo "Test 13: Exit message"
echo -e "9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "All the memory cleaned and the program is safely closed"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 14: Remove non-existent type (option 5)
echo "Test 14: Remove non-existent type in option 5"
echo -e "5\nFire\nNotExist\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Type name doesn't exist in the list"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 15: Remove valid type (option 5)
echo "Test 15: Remove valid type in option 5"
echo -e "5\nFire\nWater\n9" | ./Pokedex 6 14 config_txt/ExampleRun_Data.txt | grep -q "Type Fire"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

echo "======================================"
echo "TESTING COMPLETE"
echo "======================================"
echo ""
echo "For memory leak testing, run:"
echo "valgrind --leak-check=full --show-leak-kinds=all ./Pokedex 6 14 config_txt/ExampleRun_Data.txt"
echo ""

