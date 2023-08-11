# Data Models for PyMUD

## Notes
1. We're relying on inheritance in most cases, so deletion needs to be handling using `session.delete()`
2. Updates on parent columns need to be directed at the parent table
