## 2024-05-23 - Accessibility Pattern: Unbound Labels
**Learning:** Login form labels were visually associated but programmatically disconnected (missing `for`/`id`).
**Action:** Always check `for`/`id` binding in Flask templates, don't rely on nesting or proximity.
