# personal_triptools

Easy MVP command-line tool to track trips, budgets, and expenses.

## Quick Start

Run commands with Python 3:

```bash
python3 triptools.py --help
```

Create your first trip:

```bash
python3 triptools.py create --name "Tokyo Spring" --start 2026-04-10 --end 2026-04-17 --budget 1200
```

List trips:

```bash
python3 triptools.py list
```

Add an expense:

```bash
python3 triptools.py add-expense --trip-id trip_YYYYMMDDHHMMSS --amount 24.5 --category food --note ramen
```

Show trip summary:

```bash
python3 triptools.py summary --trip-id trip_YYYYMMDDHHMMSS
```

## Data

- Local data is saved in `trips.json`.
- `trips.json` is ignored by git so your personal records stay local.
