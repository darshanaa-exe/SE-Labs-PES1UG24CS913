# Lab 5: Static Code Analysis - Support Ticket Tracker

**Name:** Darshana S.
**SRN:** PES1UG24CS913
**Section:** 5 J
**Repository:** https://github.com/darshanaa-exe/L5_58_support-ticket-tracker.git
**File analysed:** `support_ticket_tracker.py`
**Tools used:** Pylint, Bandit, Flake8 (Python 3.12.3, virtual environment `venv`)

## 1. Objective

Use static analysis tools to find and fix quality, style and security problems in `support_ticket_tracker.py`, a small support ticket tracker (creates tickets, assigns and updates them, closes them, and saves/loads them from a JSON file).

## 2. Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install pylint bandit flake8
python support_ticket_tracker.py
```

Reports were generated with:

```bash
pylint support_ticket_tracker.py > pylint_report.txt
bandit -r support_ticket_tracker.py > bandit_report.txt
flake8 support_ticket_tracker.py > flake8_report.txt
```

## 3. Results Summary

| Tool   | Before          | After                |
| ------ | --------------- | -------------------- |
| Pylint | 5.00/10         | 10.00/10             |
| Bandit | 1 Medium, 1 Low | No issues identified |
| Flake8 | 12 findings     | No output (clean)    |

Before and after reports are in the `before/` and `after/` folders.

## 4. Issues Found and How They Were Fixed

Line numbers refer to the original file. The full table of 17 issues is in `Issues.md`.

**Bandit (security)**

| # | Issue | Severity | Line | Fix |
| - | ----- | -------- | ---- | --- |
| 1 | B307 `eval()` can run any string as code | Medium | 92 | Removed `eval`, call `print("unsafe demo")` directly |
| 2 | B110 bare `except` with `pass` hides every error | Low | 24-25 | Explicit `if ticket_id not in TICKETS: return False` |

**Pylint (quality)**

| # | Issue | Line | Fix |
| - | ----- | ---- | --- |
| 3 | W0102 mutable default `audit_log=[]` | 10 | Removed it, used one module-level `AUDIT_LOG` |
| 4 | Unknown ticket id crashes with `KeyError` (no tool flagged it) | 29-31, 66-67, 70-74 | Check `ticket_id in TICKETS` first |
| 5 | R1732 / W1514 files opened without `with` or encoding | 45-55 | `with open(..., encoding="utf-8")` |
| 6 | W0603 `global TICKETS` | 52 | `TICKETS.clear()` then `TICKETS.update(data)` |
| 7 | C0103 `closeTicket` not snake_case | 66 | Renamed to `close_ticket`, updated caller |
| 8 | W0613 unused argument `notify` | 20 | Removed it |
| 9 | C0114 / C0116 missing docstrings | every `def` | Added docstrings |
| 10 | Simplifiable `if/else`, `len()` truth test, `!= None` | 37, 60, 70-74 | `is not None`, `if not TICKETS`, `return status in (...)` |

**Flake8 (style)**

| # | Issue | Line | Fix |
| - | ----- | ---- | --- |
| 11 | F401 unused imports `sys`, `random` | 4-5 | Removed |
| 12 | F841 / W291 unused variable `count`, trailing space | 84 | Deleted the line |
| 13 | E501 lines longer than 79 characters | 10, 14, 63, 71, 79, 80 | Wrapped the lines |

## 5. What I Learned

- **Bandit caught the real security risk.** `eval` is dangerous if its input ever becomes user-controlled.
- **Some fixes were bug fixes, not style fixes.** The bare `except` hid real errors, and the mutable default leaked audit entries between calls.
- **Tools don't catch everything.** Running the program showed that an unknown ticket id crashed it, and no tool flagged that.
- **Fixes interact.** Fixing one issue changed or removed others, and a new Pylint warning only appeared after earlier fixes.
- **Re-run all three tools at the end** to confirm nothing new was introduced.

## 6. Deliverables Checklist

- [x] Fixed `support_ticket_tracker.py`
- [x] `Issues.md` completed
- [x] Before and after reports for Pylint, Bandit and Flake8
