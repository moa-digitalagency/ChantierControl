## 2024-05-23 - N+1 and Redundant Calculation Optimization
**Learning:** In Flask/SQLAlchemy, it's common to see logic that loads all related records into memory to sum them up in Python (O(N)), which is inefficient compared to SQL aggregations (O(1)). Also, helper functions (like `verifier_alertes`) often recalculate data that the caller might already have (`calculer_kpi_chantier`).
**Action:** Always prefer `db.session.query(func.sum(...))` for aggregations. Design helper functions to accept optional pre-calculated data to avoid redundant work.
