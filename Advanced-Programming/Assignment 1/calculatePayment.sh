#!/bin/bash

#flag to indicate if there was an error
has_error=0

#Checking whether 2 or more parameters were received
if [ "$#" -lt 2 ]; then
    echo "Number of parameters received : $#" >&2
    has_error=1
fi

#Extracting the last parameter (the money received from the customer) and grouping the files into an array
if [ "$#" -ge 2 ]; then
    money="${!#}"
    files=("${@:1:$#-1}")
fi

# Check whether the last parameter received is a positive number
if [ "$#" -ge 2 ] && ! [[ "$money" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "Not a valid number : $money" >&2
    has_error=1
fi

#Check whether the received files are correct
if [ "$#" -ge 2 ] && [[ "$money" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "File does not exist : $file" >&2
            has_error=1
        fi
    done
fi

#If errors are detected, exit with error code 1
if [ $has_error -eq 1 ]; then
    echo "Usage : calculatePayment.sh <valid_file_name> [More_Files] ... <money>"
    exit 1
fi

#Calculate the total amount to be paid
sum=0
for file in "${files[@]}"; do
    file_sum=$(
        { printf '0\n';\
          grep -Eo '[-+]?[0-9]+([.][0-9]+)?|[-+]?[.][0-9]+' -- "$file" \
          | sed -E 's/^[-+]//' | sed -E 's/^[.]/0./'; } \
        | paste -sd+ - | bc -l)
          sum=$(printf "%s + %s\n" "$sum" "$file_sum" | bc -l)
done

#Show the total amount to be paid
printf "Total purchase price : %.2f\n" "$sum" 

#Calculating the refund to the customer
amount=$(printf "%s - %s\n" "$money" "$sum" | bc -l)

#Calculate the absolute value of the difference
if (( $(echo "$amount < 0" | bc -l) )); then
    abs_amount=$(echo "-1 * $amount" | bc -l)
else
    abs_amount="$amount"
fi

#Shows the customer based on the amount whether he paid accurately and if not,
#how much he should be refunded or how much he should add
if (( $(echo "$abs_amount <= 0.005" | bc -l) )); then
    echo "Exact payment"
elif (( $(echo "$amount > 0" | bc -l) )); then
    echo "Your change is $(printf "%.2f" "$amount") shekel"
else 
    printf "You need to add %.2f shekel to pay the bill\n" "$abs_amount"
fi




