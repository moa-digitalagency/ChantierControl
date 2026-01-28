## 2024-05-23 - Rate Limiting on Login
**Vulnerability:** Lack of rate limiting on the login endpoint allowed brute-forcing of the 4-digit PIN authentication.
**Learning:** Weak authentication factors (like 4-digit PINs) must be paired with strict rate limiting to be secure. Even "secure" hashing (scrypt) isn't enough when the input space is small (10,000 possibilities).
**Prevention:** Always implement rate limiting on authentication endpoints, especially when using low-entropy secrets.
