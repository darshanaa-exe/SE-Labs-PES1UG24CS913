# L6_L7_58 — Restaurant Bill

Lab 6: Code and Branch Coverage Analysis

**Repository:** https://github.com/darshanaa-exe/L6_L7_58_restaurant_bill.git

## About

`restaurant_bill.py` is a small Python module that:
- totals a restaurant bill by seating section, happy hour and party size (`bill_total`)
- splits the bill between diners with a tip (`split_bill`)
- decides how a walk-in party is seated (`table_wait`)

This lab measures how much of that module the tests execute, using `coverage` and `pytest`, and improves the tests until line and branch coverage are both above 90%.

## Repository structure

```
LAB6/
├── restaurant_bill.py                      # module under test (unchanged)
├── test_restaurant_bill.py                 # starter tests (2 tests)
├── CodeCoverageTest_restaurant_bill.py     # test cases for code (line) coverage
├── BranchCoverageTest_restaurant_bill.py   # test cases for branch coverage
├── README.md
└── screenshots/
    ├── Code-Before.png
    ├── Code-After.png
    ├── Branch-Before.png
    └── Branch-After.png
```

## Setup

```bash
pip install pytest coverage
```

## How to run

Run these from inside the `LAB6` folder.

**Code (line) coverage**
```bash
python -m coverage erase
python -m coverage run -m pytest CodeCoverageTest_restaurant_bill.py
python -m coverage report -m
```

**Branch coverage**
```bash
python -m coverage erase
python -m coverage run --branch -m pytest BranchCoverageTest_restaurant_bill.py
python -m coverage report -m
```

To see the starting point, run the same commands with `test_restaurant_bill.py`.

## Results

Coverage of `restaurant_bill.py`:

| Stage | Test file | Tests | Coverage | Screenshot |
|---|---|---|---|---|
| Code coverage, before | `test_restaurant_bill.py` | 2 | 52% | `screenshots/Code-Before.png` |
| Code coverage, after | `CodeCoverageTest_restaurant_bill.py` | 15 | 100% | `screenshots/Code-After.png` |
| Branch coverage, before | `test_restaurant_bill.py` | 2 | 44% | `screenshots/Branch-Before.png` |
| Branch coverage, after | `BranchCoverageTest_restaurant_bill.py` | 30 | 100% (22/22 branches) | `screenshots/Branch-After.png` |

## What the tests cover

| Function | Cases tested |
|---|---|
| `bill_total` | Unknown section, negative food total, zero guests, happy hour on/off, happy hour ignored for takeaway, 7 vs 8 guests (large-group surcharge) |
| `split_bill` | Zero people, negative tip, exact split, rounding up, zero tip, single person |
| `table_wait` | Party of 12 vs 13, reservation, no free tables, party of 6 vs 7 with one free table, large party with two free tables |

The branch test file contains all of the code coverage tests plus extra boundary and condition cases, so that every `if`/`elif` is taken both ways.
