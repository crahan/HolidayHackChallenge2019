# Frosty Keypad
```python
#!/usr/bin/env python3
"""Tangle Coalbox Frosty Keypad challenge."""
import itertools


def is_prime(number):
    """Verify if a number is a prime."""
    return 2 in [number, 2**number % number]


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
```
