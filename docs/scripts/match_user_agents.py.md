# match_user_agents.py
```python
#!/usr/bin/env python3
"""Find matching user_agent strings."""


def main():
    """Execute."""
    file_bad = 'IPs_bad.csv'
    file_all = 'IPs_all.csv'
    list_bad = []
    list_all = []

    # Read the full data log
    with open(file_all) as fp:
        line = fp.readline()

        while line:
            list_all.append(line.split('\t'))
            line = fp.readline()

    # Read the bad IP data and match on user_agent but only
    # keep the results if less than 4 matches are found.
    with open(file_bad) as fp:
        line = fp.readline()

        while line:
            tmp = []
            line_bad = line.split('\t')

            for line_all in list_all:
                if line_all[4] == line_bad[4]:
                    tmp.append(line_all[0])

            # Only add if less than 4 matches
            if len(tmp) < 4:
                list_bad.extend(tmp)

            # Add the original IP as well
            list_bad.append(line_bad[0])
            line = fp.readline()

    # Remove duplicates
    list_bad = list(dict.fromkeys(list_bad))

    # Tadaaaaa!
    print(f'Bad IPs: {",".join(list_bad)}')


if __name__ == "__main__":
    main()
```