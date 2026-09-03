# Days 1-7 Study Guide — Python Fundamentals

Theory, examples, questions, and full solutions for Week 1 of the curriculum (`docs/50-day-curriculum.md`). Day 8 onward returns to the interactive teaching loop and the full hint ladder, since that's where real DSA problems start — this guide covers only the from-zero Python fundamentals.

---

## Day 1 — Variables, print, data types, input, comments

### Theory

A **variable** is a name for a value — like a labeled box. `x = 5` creates a box labeled `x` holding `5`. The `=` means "store this value," not "equals" — that distinction matters once `==` (comparison) shows up on Day 2. Reassigning a variable (`x = 10`) overwrites the box's contents; the old value is simply gone.

`print(x)` displays what's in the box. `#` starts a **comment** — everything after it on that line is ignored by Python, purely a note for humans.

Every value has a **type**: `int` (whole numbers), `float` (decimals), `str` (text, always in quotes), `bool` (`True`/`False`). Types matter because the same operator behaves differently per type — `"5" + "3"` gives `"53"` (joining text) while `5 + 3` gives `8` (adding numbers). This is the most common beginner trip-up: quotes make something text, and `+` on text means "stick together," not "add."

`input()` reads what a user types, always as a `str` — even a typed number comes back as text, so `int(input())` converts it to a real number.

### Examples

```python
name = input("What's your name? ")
age = int(input("What's your age? "))
print("Hello, " + name)
print(age + 1)
```

### Questions

1. Print a greeting with your own message.
2. Store your name and age in variables, then print a sentence using both.
3. Swap two variables' values (`a`, `b` end up holding each other's original values).
4. Write a Celsius→Fahrenheit converter (`F = C * 9/5 + 32`).
5. Read a number with `input()`, convert it with `int()`, and print it doubled.

### Solutions

```python
# Q1
print("Hey, welcome to Day 1!")

# Q2
name = "Akshat"
age = 25
print("My name is " + name + " and I am " + str(age) + " years old.")
# age is an int, so it must be converted with str() before joining with +;
# you can't "add" a string and an int directly.

# Q3
a = 3
b = 7
a, b = b, a
print(a, b)  # 7 3
# Python evaluates the whole right side (b, a) into a temporary pair BEFORE
# assigning, so this works without a separate temp variable.

# Q4
celsius = 30
fahrenheit = celsius * 9 / 5 + 32
print(fahrenheit)  # 86.0

# Q5
n = int(input("Enter a number: "))
print(n * 2)
```

---

## Day 2 — Operators, conditionals, booleans

### Theory

Comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) produce a `bool`. Watch `==` (compare) vs `=` (assign) — confusing these is the single most common beginner syntax bug.

`if`/`elif`/`else` picks one branch to run. Python checks conditions top to bottom and runs the *first* one that's `True`, skipping the rest — order matters. `and`/`or`/`not` combine conditions. Indentation isn't just style in Python — it's how the language knows what's "inside" the `if`.

### Examples

```python
age = 20
if age < 13:
    print("child")
elif age < 20:
    print("teen")
else:
    print("adult")
```

### Questions

1. Even/odd checker.
2. Largest of 3 numbers.
3. Grade calculator using `if`/`elif` on a score.
4. Leap year checker.
5. FizzBuzz-style checks on 5 hardcoded numbers (no loop yet).

### Solutions

```python
# Q1
num = 7
if num % 2 == 0:
    print("even")
else:
    print("odd")

# Q2
a, b, c = 4, 9, 2
if a >= b and a >= c:
    largest = a
elif b >= a and b >= c:
    largest = b
else:
    largest = c
print(largest)  # 9

# Q3
score = 82
if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("F")

# Q4
year = 2024
if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
    print("leap year")
else:
    print("not a leap year")
# The actual rule: divisible by 4, EXCEPT century years (divisible by 100)
# unless also divisible by 400.

# Q5
for n in [3, 5, 15, 7, 9]:
    if n % 15 == 0:
        print("FizzBuzz")
    elif n % 3 == 0:
        print("Fizz")
    elif n % 5 == 0:
        print("Buzz")
    else:
        print(n)
# Technically uses a loop already -- fine, Day 3 formalizes loops properly.
```

---

## Day 3 — Loops

### Theory

`for` and `while` both repeat code. `for x in range(5):` runs 5 times with `x` taking `0,1,2,3,4` — `range(5)` excludes `5` itself, a very common off-by-one trap. `while condition:` repeats as long as the condition is `True`; forgetting to update something inside it causes an infinite loop.

`break` exits a loop immediately; `continue` skips to the next iteration without exiting. Nested loops multiply the work — a loop of `n` inside a loop of `n` runs `n × n` times, your first hands-on look at why nested loops are considered "slower."

### Examples

```python
total = 0
for i in range(1, 6):   # 1,2,3,4,5
    total = total + i
print(total)  # 15
```

### Questions

1. Print numbers 1-10 with `while`, then again with `for`+`range`.
2. Sum of 1 to n.
3. Multiplication table for a number.
4. Count vowels in a string with a loop.
5. Print a small triangle of stars using a nested loop.
6. Factorial via loop.
7. Count digits of a number.
8. Reverse a number using arithmetic (not string tricks).

### Solutions

```python
# Q1
i = 1
while i <= 10:
    print(i)
    i += 1

for i in range(1, 11):
    print(i)

# Q2
n = 10
total = 0
for i in range(1, n + 1):
    total += i
print(total)  # 55

# Q3
num = 6
for i in range(1, 11):
    print(num, "x", i, "=", num * i)

# Q4
s = "hello world"
count = 0
for ch in s:
    if ch in "aeiou":
        count += 1
print(count)  # 3

# Q5
rows = 5
for i in range(1, rows + 1):
    print("*" * i)

# Q6
n = 5
fact = 1
for i in range(1, n + 1):
    fact *= i
print(fact)  # 120

# Q7
n = 12345
count = 0
while n > 0:
    n = n // 10
    count += 1
print(count)  # 5

# Q8
n = 1234
reversed_n = 0
while n > 0:
    digit = n % 10
    reversed_n = reversed_n * 10 + digit
    n = n // 10
print(reversed_n)  # 4321
```

---

## Day 4 — Lists (arrays)

### Theory

A list holds an ordered sequence of values: `arr = [4, 7, 2, 9]`. Indexing starts at `0` — `arr[0]` is `4`. Negative indices count from the end (`arr[-1]` is the last element). Slicing `arr[1:3]` gives a *new* list of indices 1 and 2 (exclusive of 3).

Key methods: `append(x)` adds to the end, `pop()` removes from the end, `insert(i, x)` inserts at index `i`, `len(arr)` gives the length, `x in arr` checks membership.

**Gotcha:** `b = a` does *not* copy a list — `b` and `a` point to the *same* list, so changing one changes the other.

### Examples

```python
arr = [4, 7, 2, 9]
biggest = arr[0]
for x in arr:
    if x > biggest:
        biggest = x
print(biggest)  # 9
```

### Questions

1. Find the largest element (write it yourself, not `max()`).
2. Find the second largest.
3. Sum of all elements; count of even numbers.
4. Reverse an array in place using a loop.

### Solutions

```python
arr = [4, 7, 2, 9, 5]

# Q1
largest = arr[0]
for x in arr:
    if x > largest:
        largest = x
print(largest)  # 9

# Q2
largest = second = float('-inf')
for x in arr:
    if x > largest:
        second = largest
        largest = x
    elif x > second:
        second = x
print(second)  # 7
# Tracking both "largest" and "second" in one pass: whenever a new largest
# shows up, the OLD largest becomes the new second.

# Q3
total = 0
even_count = 0
for x in arr:
    total += x
    if x % 2 == 0:
        even_count += 1
print(total, even_count)  # 27 2

# Q4
left, right = 0, len(arr) - 1
while left < right:
    arr[left], arr[right] = arr[right], arr[left]
    left += 1
    right -= 1
print(arr)  # [5, 9, 2, 7, 4]
```

---

## Day 5 — Strings

### Theory

A string behaves a lot like a list of characters, except **immutable** — you can't do `s[0] = 'x'`; you build a new string instead. Indexing/slicing work like lists. `s[::-1]` reverses a string, but write the reverse yourself with a loop first so you understand *why* it works.

Useful methods: `.split()` breaks a string into a list of words, `.join()` reverses that, `.strip()` removes whitespace, `.upper()`/`.lower()` change case, `.replace(a, b)` swaps substrings.

### Examples

```python
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

### Questions

1. Reverse a string with a manual loop.
2. Palindrome check.
3. Count vowels/consonants.
4. Anagram check.

### Solutions

```python
# Q1
s = "hello"
reversed_s = ""
for ch in s:
    reversed_s = ch + reversed_s   # each new char goes to the FRONT
print(reversed_s)  # olleh

# Q2
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
print(is_palindrome("racecar"))  # True

# Q3
s = "hello world"
vowels = consonants = 0
for ch in s:
    if ch.isalpha():
        if ch in "aeiouAEIOU":
            vowels += 1
        else:
            consonants += 1
print(vowels, consonants)  # 3 7

# Q4
def is_anagram(a, b):
    return sorted(a) == sorted(b)
print(is_anagram("listen", "silent"))  # True
# sorted() turns each string into a list of chars in order -- two strings
# are anagrams exactly when those sorted lists match.
```

---

## Day 6 — Functions

### Theory

`def name(params):` defines a reusable block of code. `return` sends a value back to the caller; `print` just displays something and returns nothing — mixing these up (using `print` where you meant `return`) silently breaks automated testing, since the function then "returns" `None`.

A variable created inside a function only exists inside that function (**scope**) — it disappears once the function returns.

### Examples

```python
def max_of_two(a, b):
    if a > b:
        return a
    return b
```

### Questions

1. Function returning the max of two numbers.
2. Function checking if a number is prime.
3. Rewrite Day 4-5's largest-element, palindrome-check, and anagram-check as proper functions with clean signatures.

### Solutions

```python
# Q1
def max_of_two(a, b):
    if a > b:
        return a
    return b

# Q2
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
# Only need to check divisors up to sqrt(n) -- if n has a factor bigger
# than its square root, it must also have one smaller, which you'd have
# already found.

# Q3
def largest_element(arr):
    largest = arr[0]
    for x in arr:
        if x > largest:
            largest = x
    return largest

def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

def is_anagram(a, b):
    return sorted(a) == sorted(b)
```

---

## Day 7 — Dictionaries, sets, Week 1 checkpoint

### Theory

A dictionary stores key→value pairs: `phonebook = {"Alex": "555-1234"}`. Looking something up by key is fast — much faster than scanning a whole list for a match, which is the seed of everything "hashing" means starting Day 11. `.get(key)` looks up a key without crashing if it's missing (`phonebook["missing"]` raises `KeyError`; `.get("missing")` returns `None`).

A set is like a dict with only keys, no values — ideal for "have I seen this before" checks and de-duplication.

### Examples

```python
def has_duplicate(nums):
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False
```

### Questions

1. Word-frequency counter using a dict.
2. Duplicate check using a set.
3. Simple phonebook: add, look up, delete.
4. Two Sum, brute-force only (nested loop checking every pair).

### Solutions

```python
# Q1
def word_frequency(sentence):
    freq = {}
    for word in sentence.split():
        freq[word] = freq.get(word, 0) + 1
    return freq
print(word_frequency("the cat sat on the mat"))
# {'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}

# Q2
def has_duplicate(nums):
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False
print(has_duplicate([1, 2, 3, 2]))  # True

# Q3
phonebook = {}
phonebook["Alex"] = "555-1234"       # add
print(phonebook.get("Alex"))         # look up -> 555-1234
del phonebook["Alex"]                # delete

# Q4
def two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
print(two_sum_brute([2, 7, 11, 15], 9))  # [0, 1]
# O(n^2) -- Day 11's whole point is replacing this nested loop with a
# single-pass hashmap version.
```

### Week 1 checkpoint

Before Day 8, you should be able to explain, unaided, in your own words: what a variable is and how reassignment works; the difference between `int`/`float`/`str`/`bool`; how `if`/`elif`/`else` picks a branch; the difference between `for` and `while`, and what `range()` generates; how list/string indexing and slicing work; why `b = a` doesn't copy a list; the difference between `return` and `print`; and why a dict lookup beats scanning a list.

---

## What changes starting Day 8

Two things revert from "read at your own pace" back to the original design: the interactive teaching loop (concept → example → prediction → exercise → feedback, one step at a time) resumes, and the full hint ladder applies to every problem with no direct-solution shortcut (see `docs/learning-philosophy.md`'s amendment log for exactly what changed and why). Day 8 is arrays/prefix-sums, the start of Block 2 in `docs/50-day-curriculum.md`.
