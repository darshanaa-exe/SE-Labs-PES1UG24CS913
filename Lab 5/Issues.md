# Issues found in support_ticket_tracker.py
NAME: Darshana S\
SRN: PES1UG24CS913\
SECTION: 5 J     
   

Line numbers refer to the **original** file. Issue numbers match the commit messages ("Fix Issue N: ...").
Severity: Bandit rating, or Pylint category (W = warning, R = refactor, C = convention).

| # | Issue | Type | Line(s) | Description | Fix Approach |
| - | ----- | ---- | ------- | ----------- | ------------ |
| 1 | `eval()` used (Bandit B307, Medium; Pylint W0123) | Security | 92 | `eval` executes any string as code. If the string ever came from user input or an environment variable, an attacker could run arbitrary code. | Removed `eval`; the demo line now calls `print("unsafe demo")` directly. |
| 2 | Bare `except:` with `pass` (Bandit B110, Low; Pylint W0702; Flake8 E722) | Bug / Security | 24-25 | `assign_ticket` silently swallows every error, including `KeyboardInterrupt`, so real bugs are hidden. | Replaced with an explicit `if ticket_id not in TICKETS: return False` check. |
| 3 | Mutable default argument `audit_log=[]` (Pylint W0102, R0913, R0917) | Bug | 10 | The same list is created once and shared by every call, so audit entries leak between calls. It also made `create_ticket` take 6 arguments (limit 5). | Removed the parameter and used one module-level `AUDIT_LOG` list. |
| 4 | Unknown ticket id crashes the program (found by running it; no tool flags it) | Bug | 29-31, 66-67, 70-74 | `update_status`, `closeTicket` and `is_open` raise `KeyError` on an unknown id. Typing `999` at the prompt crashed the program. | Check `ticket_id in TICKETS` first. `update_status` returns `None`, `close_ticket` returns `False`, `is_open` returns `False`, and `main` prints "No ticket with id ...". |
| 5 | Unused imports `sys`, `random` (Flake8 F401; Pylint W0611) | Style | 4-5 | Imported but never used. | Removed both imports. |
| 6 | Unused variable `count` and trailing whitespace (Flake8 F841, W291; Pylint W0612, C0303) | Style | 84 | `count` is assigned but never used, and the line had a stray trailing space. | Deleted the line. |
| 7 | Files opened without `with` or an encoding (Pylint R1732, W1514) | Bug | 45-48, 51-55 | If `write` or `json.loads` fails, `close()` never runs and the file handle leaks. The encoding depended on the OS. | Used `with open(..., encoding="utf-8")` in `save_tickets` and `load_tickets`. |
| 8 | `global TICKETS` statement (Pylint W0603) | Design | 52 | Rebinding a module-level variable from inside a function makes the code harder to reason about. | `load_tickets` now reads the file first, then calls `TICKETS.clear()` and `TICKETS.update(data)`. |
| 9 | `closeTicket` is not snake_case (Pylint C0103) | Style | 66 | Breaks PEP 8 naming. | Renamed to `close_ticket` and updated its one caller in `main`. |
| 10 | Unused argument `notify` (Pylint W0613) | Style | 20 | The parameter is never used and no caller passes it. | Removed the parameter. |
| 11 | `!= None` comparison (Flake8 E711; Pylint C0121, R1714) | Style | 37 | `None` should be compared by identity, not equality. | Changed to `is not None`. |
| 12 | Verbose boolean logic (Pylint R1703, R1705) | Style | 70-74 | `if ...: return True else: return False` is redundant. | `is_open` now returns `status in ("open", "in_progress")` directly. |
| 13 | `len()` used as a truth test (Pylint C1802) | Style | 60 | `if not len(TICKETS)` is not Pythonic. | Changed to `if not TICKETS`. |
| 14 | Outdated string formatting (Pylint C0209, W1203) | Style | 16, 85 | `%` formatting is outdated, and an f-string inside `logging` is built even when the log level is off. | Used an f-string for the audit entry and lazy `%d` formatting in `logging.info`. |
| 15 | Missing docstrings (Pylint C0114, C0116) | Style | 1 and every `def` | The module and all functions had no documentation. | Added a one-line docstring to the module and to each function. |
| 16 | Looping over a dict and indexing it (Pylint C0206) | Style | 62-63 | `for ticket_id in TICKETS:` followed by `TICKETS[ticket_id]` twice. Surfaced in Pylint only after the earlier fixes. | Changed to `for ticket_id, ticket in TICKETS.items():`. |
| 17 | Lines longer than 79 characters (Flake8 E501; Pylint C0301) | Style | 10, 14, 63, 71, 79, 80 | Hard to read and review. Lines 63 and 71 were already shortened by Issues 16 and 12. | Wrapped the remaining long lines and expanded the ticket dict one key per line. |

## Results

| Tool | Before | After |
| ---- | ------ | ----- |
| Pylint | 5.00/10 | 10.00/10 |
| Bandit | 1 Medium, 1 Low | 0 issues |
| Flake8 | 12 findings | 0 findings |
