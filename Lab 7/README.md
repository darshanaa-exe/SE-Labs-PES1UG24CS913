# L6_L7_58 — Restaurant Bill

Lab 7: Fuzzing for Input Validation Bugs

**Repository:** https://github.com/darshanaa-exe/L6_L7_58_restaurant_bill.git

## About

`restaurant_bill_parser.py` is a small Python module that reads restaurant bill details typed in by a user:
- cleans a dish name by removing chef's-special markers (`*`, `#`, `~`) and title-casing it (`clean_dish_name`)
- parses a comma-separated list of item prices into a list of ints (`parse_item_prices`)
- splits a `TOTAL/PEOPLE` bill into the amount each person pays (`split_amount`)

The original module assumed every input was well formed. This lab uses property-based fuzzing with `Hypothesis` to find the inputs that crash it, then hardens the module until all three functions handle any input without crashing.

## Repository structure

```
LAB7/
├── restaurant_bill_parser.py               # fixed module (hardened against bad input)
├── test_restaurant_bill_parser.py          # Hypothesis fuzz tests, one per function
├── PES1UG24CS913_Darshana_S_LAB7.pdf       # screenshots SS1 to SS4
└── README.md
```

## Setup

```bash
pip install hypothesis pytest
```

## How to run

Run these from inside the `LAB7` folder.

**Run the module**
```bash
python restaurant_bill_parser.py
```

**Run the fuzz tests**
```bash
python -m pytest test_restaurant_bill_parser.py -v
```

Each test feeds `st.text() | st.none()` to one function and fails if the function raises any exception.

## Results

| Stage | What was run | Result | Screenshot |
|---|---|---|---|
| Buggy module | `python restaurant_bill_parser.py` | Crashes with `ValueError` on `abc` and `ZeroDivisionError` on `1200/0` | SS1 |
| Tests on buggy module | `pytest test_restaurant_bill_parser.py` | 3 failed | SS2 |
| Fixed module | `python restaurant_bill_parser.py` | Bad inputs handled without crashing | SS3 |
| Tests on fixed module | `pytest test_restaurant_bill_parser.py -v` | 3 passed | SS4 |

All four screenshots are in `PES1UG24CS913_Darshana_S_LAB7.pdf`.

## Bugs found

Hypothesis shrank each failure to a minimal input:

| Function | Failing input | Exception | Error message |
|---|---|---|---|
| `clean_dish_name` | `None` | `AttributeError` | `'NoneType' object has no attribute 'strip'` |
| `parse_item_prices` | `''` | `ValueError` | `invalid literal for int() with base 10: ''` |
| `parse_item_prices` | `None` | `AttributeError` | `'NoneType' object has no attribute 'split'` |
| `split_amount` | `'/'` | `ValueError` | `invalid literal for int() with base 10: ''` |
| `split_amount` | `''` | `ValueError` | `not enough values to unpack (expected 2, got 1)` |
| `split_amount` | `None` | `AttributeError` | `'NoneType' object has no attribute 'split'` |

Typed input such as `abc` (`ValueError`) and `1200/0` (`ZeroDivisionError`) also crashed the original module.

## How the bugs were fixed

| Function | Fix |
|---|---|
| `clean_dish_name` | Returns `""` if the input is not a string |
| `parse_item_prices` | Returns `[]` for non-strings; skips empty, non-numeric and negative entries |
| `split_amount` | Returns `None` for non-strings, input not in `TOTAL/PEOPLE` form, non-integer values, a negative total, or fewer than one person (including zero) |

`main()` also prints a clear "Invalid input" message when `split_amount` returns `None`.
