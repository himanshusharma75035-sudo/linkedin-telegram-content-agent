# Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a focused branch.
3. Keep runtime code dependency-free unless a dependency removes substantial
   security or reliability risk.
4. Add or update tests.
5. Run:

```powershell
python -m unittest discover -s tests -v
python -m py_compile src\*.py
```

6. Confirm `git status` contains no `.env`, token, queue, or log files.
7. Open a pull request describing the behavior change and verification.

Do not include real API responses, user profiles, tokens, or private posts in
tests or screenshots.
