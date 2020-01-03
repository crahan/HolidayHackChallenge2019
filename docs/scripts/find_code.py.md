# find_code.py
**Purpose**: generate valid [keypad codes](../hints/h6.md)

```python
#!/usr/bin/env python3
"""Tangle Coalbox - Frosty Keypad challenge."""
import itertools


def is_prime(number):
    """Verify if a number is a prime."""
    return 2 in [number, 2**number % number]


def main():
    """Execute."""
    digit_sets = [
        ['1', '1', '3', '7'],
        ['1', '3', '3', '7'],
        ['1', '3', '7', '7']
    ]

    primes = []

    for digits in digit_sets:
        for subset in itertools.permutations(digits):
            val = int(''.join(subset))
            if is_prime(val) and val not in primes:
                primes.append(val)
                print(f'{val} is a prime number')


if __name__ == "__main__":
    main()
```
