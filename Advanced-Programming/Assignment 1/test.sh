#!/bin/bash

# ==============================================================================
# Automatic test script for calculatePayment.sh
#
# *** v9 - ADDED EDGE CASES ***
#
#
# ==============================================================================

# --- Settings ---
SCRIPT_TO_TEST="./calculatePayment.sh"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' 
total_tests=0
passed_tests=0

# --- Initial Check ---
if [ ! -x "$SCRIPT_TO_TEST" ]; then
    echo -e "${RED}Error: Script $SCRIPT_TO_TEST not found or is not executable (run chmod +x).${NC}"
    exit 1
fi

# --- Helper Functions ---
setup_tests() {
    echo -e "${YELLOW}--- Setting up test environment... ---${NC}"
    
    cat << 'EOF' > grocery.txt
Avocados 2.5 /can
Ginger: $3.99
Tuna (only tuna, salt, olive oil or water): $1.49/can
Popcorn Kernels: $1.99/lb
Olive Oil : Extra Light Tasting: 0.26/oz (bottle)
Nuts, Almonds/Cashews/Pecans: 10.99 /lb
Balsamic: $3.99
Pasta Sauce (no added sugar!): 3/oz jar
no more items.
EOF

printf "one chicken wing 2.20\nnewspaper* 17" > He_wants_to_return_the_bags.txt


    cat << 'EOF' > no_numbers.txt
hey :)
EOF
	printf "ss .9 \n 23. \n 0.1000 \n tt.5" > wird_point.txt
    echo "10.001" > rounding_down.txt
    echo "10.125" > rounding_up.txt
    echo "10.00" > "-file_with_dash.txt"
    echo "20.00" > "file with spaces.txt"
    touch empty_file.txt
    mkdir -p test_dir
    
    # --- NEW TESTS ADDED ---
    echo "10.00" > no_read.txt
    chmod 000 no_read.txt # Remove read permissions
    echo ".50" > dot_file.txt # Number starting with a dot
}

cleanup_tests() {
    echo -e "${YELLOW}--- Cleaning up test environment... ---${NC}"
    
    # Add permissions back so 'rm' doesn't fail
    chmod 644 no_read.txt 2>/dev/null 

    rm -f -- grocery.txt \
             He_wants_to_return_the_bags.txt \
             no_numbers.txt \
             rounding_down.txt \
             rounding_up.txt \
             "-file_with_dash.txt" \
             "file with spaces.txt" \
             empty_file.txt \
             /tmp/actual_stdout.txt \
             /tmp/expected_stdout.txt \
             /tmp/actual_stderr.txt \
             /tmp/expected_stderr.txt \
             no_read.txt \
             dot_file.txt
    
    rmdir test_dir
}

# --- CHANGE: The 'trap' command has been REMOVED ---
# trap cleanup_tests EXIT

# --- Main Test Function (v6) ---
run_test() {
    local test_name="$1"
    local expected_stdout="$2"
    local expected_stderr="$3"
    shift 3 
    local args=("$@") 
    ((total_tests++))

    actual_stdout=$( $SCRIPT_TO_TEST "${args[@]}" 2> /tmp/stderr.txt )
    actual_stderr=$( cat /tmp/stderr.txt )
    rm /tmp/stderr.txt

    if [ "$actual_stdout" == "$expected_stdout" ] && [ "$actual_stderr" == "$expected_stderr" ]; then
        echo -e "${GREEN}PASSED:${NC} $test_name"
        ((passed_tests++))
    else
        echo -e "${RED}FAILED:${NC} $test_name"
        
        # --- START: Updated Failure Output (v6) ---
        
        echo -e "${YELLOW}--- Command Run ---${NC}"
        printf "%s " "$SCRIPT_TO_TEST" "${args[@]}"
        echo # for the newline
        echo "---------------------"

        echo -n "$actual_stdout" > /tmp/actual_stdout.txt
        echo -n "$expected_stdout" > /tmp/expected_stdout.txt
        echo -n "$actual_stderr" > /tmp/actual_stderr.txt
        echo -n "$expected_stderr" > /tmp/expected_stderr.txt

        if [ "$actual_stdout" != "$expected_stdout" ]; then
            echo -e "${YELLOW}--- STDOUT (Regular Text View) ---${NC}"
            echo -e "${YELLOW}Expected (wrapped in quotes):${NC}\n\"$expected_stdout\""
            echo "---"
            echo -e "${RED}Actual (wrapped in quotes):${NC}\n\"$actual_stdout\""
            echo "------------------------------------"
            
            echo -e "${YELLOW}--- STDOUT (Character Dump View) ---${NC}"
            echo "Comparing with 'od -c' (character dump):"
            echo -e "${YELLOW}--- Diff Report ( < Actual | > Expected ) ---${NC}"
            diff -y -W $(tput cols) <(od -c /tmp/actual_stdout.txt) <(od -c /tmp/expected_stdout.txt)
            echo "-----------------------------------"
            echo -e "${YELLOW}Hint: Look for '\\r' (Carriage Return). If you see it, run: dos2unix calculatePayment.sh${NC}"

        fi
        if [ "$actual_stderr" != "$expected_stderr" ]; then
            echo -e "${YELLOW}--- STDERR (Regular Text View) ---${NC}"
            echo -e "${YELLOW}Expected (wrapped in quotes):${NC}\n\"$expected_stderr\""
            echo "---"
            echo -e "${RED}Actual (wrapped in quotes):${NC}\n\"$actual_stderr\""
            echo "------------------------------------"

            echo -e "${YELLOW}--- STDERR (Character Dump View) ---${NC}"
            echo "Comparing with 'od -c' (character dump):"
            echo -e "${YELLOW}--- Diff Report ( < Actual | > Expected ) ---${NC}"
            diff -y -W $(tput cols) <(od -c /tmp/actual_stderr.txt) <(od -c /tmp/expected_stderr.txt)
            echo "-----------------------------------"
            echo -e "${YELLOW}Hint: Look for '\\r' (Carriage Return). If you see it, run: dos2unix calculatePayment.sh${NC}"
        fi
        # --- END: Updated Failure Output ---
    fi
}


# ==============================================================================
# --- Run Tests ---
# ==============================================================================

setup_tests

echo -e "\n${YELLOW}--- 1. Testing Error Scenarios ---${NC}"

run_test "Error : No arguments" \
         "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>" \
         "Number of parameters received : 0"
         
run_test "Error : Last argument not a valid number" \
         "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>" \
         "Not a valid number : hey" \
         "grocery.txt" "hey"

run_test "Error : Invalid number (letter in middle)" \
         "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>" \
         "Not a valid number : 1c00.5" \
         "noFile.txt" "1c00.5"
		 
run_test "Error : Invalid number (2 points)" \
         "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>" \
         "Not a valid number : 1.00.5" \
         "noFile.txt" "1.00.5"

expected_stderr=$(printf "File does not exist : grocery\nFile does not exist : noFile.txt")
run_test "Error : Two non-existent files" \
         "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>" \
         "$expected_stderr" \
         "grocery" "noFile.txt" "100"


		 
		 
		 
		 
		 

echo -e "\n${YELLOW}--- 2. Testing Success Scenarios ---${NC}"

expected_stdout_1=$(printf "Total purchase price : 19.20\nYour change is 80.80 shekel")
run_test "Success: Bag return - Calculate change" \
         "$expected_stdout_1" \
         "" \
         "He_wants_to_return_the_bags.txt" "100"

expected_stdout_2=$(printf "Total purchase price : 19.20\nYou need to add 16.00 shekel to pay the bill")
run_test "Success: Bag return - Need to add" \
         "$expected_stdout_2" \
         "" \
         "He_wants_to_return_the_bags.txt" "3.2"

expected_stdout_3=$(printf "Total purchase price : 19.20\nExact payment")
run_test "Success: Bag return - Exact payment" \
         "$expected_stdout_3" \
         "" \
         "He_wants_to_return_the_bags.txt" "19.2"
		 
expected_stdout_3_5=$(printf "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>\n")
expected_stderr_3_5=$(printf "Not a valid number : .19\n")

run_test "Fail: Bag return - illegal money input" \
         "$expected_stdout_3_5" \
         "$expected_stderr_3_5" \
         "He_wants_to_return_the_bags.txt" ".19"




expected_stdout_4=$(printf "Total purchase price : 47.41\nYou need to add 41.66 shekel to pay the bill")
run_test "Success: Two files - Need to add" \
         "$expected_stdout_4" \
         "" \
         "grocery.txt" "He_wants_to_return_the_bags.txt" "5.75"

expected_stdout_5=$(printf "Total purchase price : 0.00\nYour change is 100.00 shekel")
run_test "Success: File with no numbers" \
         "$expected_stdout_5" \
         "" \
         "no_numbers.txt" "100"

echo -e "\n${YELLOW}--- 3. Testing Edge Cases ---${NC}"

expected_stdout_6=$(printf "Total purchase price : 0.00\nYour change is 50.00 shekel")
run_test "Edge Case: Empty file" \
         "$expected_stdout_6" \
         "" \
         "empty_file.txt" "50"

run_test "Edge Case: Argument is a directory" \
         "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>" \
         "File does not exist : test_dir" \
         "test_dir" "100"

expected_stdout_dash=$(printf "Total purchase price : 10.00\nYour change is 90.00 shekel")
run_test "Edge Case: Filename starts with dash (requires -- in grep)" \
         "$expected_stdout_dash" \
         "" \
         "-file_with_dash.txt" "100"

expected_stdout_spaces=$(printf "Total purchase price : 20.00\nYour change is 80.00 shekel")
run_test "Edge Case: Filename contains spaces" \
         "$expected_stdout_spaces" \
         "" \
         "file with spaces.txt" "100"

expected_stdout_rounding_need=$(printf "Total purchase price : 10.00\nExact payment")
run_test "Edge Case: Rounding (diff 0.001 -> Exact payment)" \
         "$expected_stdout_rounding_need" \
         "" \
         "rounding_down.txt" "10.00"



         
expected_stdout_rounding_0=$(printf "Total purchase price : 10.12\nExact payment")
run_test "Edge Case: Rounding (diff 0.005 -> Change 0.01)" \
         "$expected_stdout_rounding_0" \
         "" \
         "rounding_up.txt" "10.13"
		 
		 

		 
expected_stdout_rounding_printf=$(printf "Total purchase price : 24.50\nExact payment")
run_test "Edge Case: with .# , #. , c.#" \
         "$expected_stdout_rounding_printf" \
         "" \
         "wird_point.txt" "24.5"








# ==============================================================================
# --- Summary ---
# ==============================================================================
echo -e "\n${YELLOW}--- Test Summary ---${NC}"
echo "Total Tests: $total_tests"
echo -e "${GREEN}Passed: $passed_tests${NC}"




# --- CHANGE: Cleanup is now conditional ---
if [ $total_tests -ne $passed_tests ]; then
    echo -e "${RED}Failed: $((total_tests - passed_tests))${NC}"
    echo -e "${YELLOW}Test environment was NOT cleaned up for debugging.${NC}"
    exit 1 
else
    echo -e "${GREEN}All tests passed successfully!${NC}"
    cleanup_tests # Only clean up if all tests passed
    exit 0 
fi