from functools import reduce

##--------------------------------------------------------------------------------------

## Question1
fibonacci = lambda n: reduce(lambda x, y: x + [x[-1] + x[-2]], range(2, n), [0, 1])[:n]
# Example usage:
n = 10
print("Question 1:")
print(fibonacci(n))
print()


##--------------------------------------------------------------------------------------

##Question2
concat_strings = lambda strings: reduce(lambda x, y: x + ' ' + y, strings)
result = concat_strings(["Hello", "Sharon", ",", "How", "Are", "You?"])
# Example usage:
print("Question 2:")
print(result)  # Output: "Hello Sharon , How Are You?"
print()

##--------------------------------------------------------------------------------------

##Question3
cumulative_sums_of_squares = lambda lst: list(map(
    lambda sublist: reduce(
        lambda acc, x: acc + (lambda is_even: (lambda sq: sq(x))(lambda y: y * y) if is_even(x) else 0)(lambda y: y % 2 == 0),
        sublist,0),lst))
result = cumulative_sums_of_squares([[1, 2, 3, 4, 10], [4, 5, 6], [7, 8, 9]])
# Example usage
print("Question 3:")
print(result)  # Output: [120, 52, 64]
print()

##--------------------------------------------------------------------------------------

##Question4
def cumulative_operation(op):
    return lambda seq: reduce(op, seq)

# Example usage to implement factorial
factorial = lambda n: cumulative_operation(lambda x, y: x * y)(range(1, n + 1))

# Example usage to implement exponentiation
exponentiation = lambda base, exp: cumulative_operation(lambda x, y: x * y)([base] * exp)

print("Question 4:")
# Testing factorial
print(factorial(5))  # Output: 120 (5! = 5 * 4 * 3 * 2 * 1)

# Testing exponentiation
print(exponentiation(2, 3))  # Output: 8 (2^3 = 2 * 2 * 2)
print()

##--------------------------------------------------------------------------------------

##Question5
result = reduce(lambda acc, x: acc + x,
                map(lambda even: even ** 2, filter(lambda num: num % 2 == 0, [2, 3, 4, 5, 6, 7, 8])))
# Example usage:
print("Question 5:")
print(result)  # Output: 120
print()

##--------------------------------------------------------------------------------------

##Question6
input_list = [
    ["madam", "test", "level", "word"],   # Contains 2 palindromes: "madam", "level"
    ["radar", "python", "civic"],         # Contains 2 palindromes: "radar", "civic"
    ["hello", "world"],                   # Contains 0 palindromes
    ["deified", "noon", "stats"]          # Contains 3 palindromes: "deified", "noon", "stats"
]
palindrome_counts = list(map(lambda sublist: len(list(filter(lambda x: x == x[::-1], sublist))), input_list))
# Example usage
print("Question 6:")
print(palindrome_counts)  # Output: [2, 2, 0, 3]
print()

##--------------------------------------------------------------------------------------

##Question7
print("Question 7:")
print("Lazy Evaluation: Values are generated and processed only as needed, potentially saving time and resources by avoiding unnecessary computations.In the program's second part, values are generated and squared one at a time, only when they are about to be used.")
## Lazy Evaluation: Values are generated and processed only as needed, potentially saving time and resources
## by avoiding unnecessary computations.In the program's second part, values are generated and squared one at a time, only when they are about to be used.
print()

##--------------------------------------------------------------------------------------

##Question8
primes_desc = lambda lst: sorted([x for x in lst if x > 1 and all(x % i != 0 for i in range(2, int(x ** 0.5) + 1))], reverse=True)
numbers = [29, 15, 3, 22, 19, 23, 5, 10, 13, 8]
# Find prime numbers and sort them in descending order
prime_numbers_sorted = primes_desc(numbers)
# Example usage
print("Question 8:")
print(prime_numbers_sorted)  # Output: [29, 23, 19, 13, 5, 3]
print()
