#!/usr/bin/env python3
"""Simple MVP CLI for tracking trips and expenses."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


DB_PATH = Path("trips.json")


def load_db(path: Path = DB_PATH) -> dict[str, Any]:
    if not path.exists():
        return {"trips": []}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {path} is not valid JSON.", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict) or "trips" not in data or not isinstance(data["trips"], list):
        print(f"Error: {path} has unexpected format.", file=sys.stderr)
        sys.exit(1)
    return data


def save_db(data: dict[str, Any], path: Path = DB_PATH) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)


def parse_iso_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must be in YYYY-MM-DD format.") from exc


def find_trip(data: dict[str, Any], trip_id: str) -> dict[str, Any]:
    for trip in data["trips"]:
        if trip["id"] == trip_id:
            return trip
    print(f"Error: trip '{trip_id}' not found.", file=sys.stderr)
    sys.exit(1)


def cmd_create(args: argparse.Namespace) -> None:
    start = parse_iso_date(args.start)
    end = parse_iso_date(args.end)
    if end < start:
        print("Error: end date must be on or after start date.", file=sys.stderr)
        sys.exit(1)
    if args.budget < 0:
        print("Error: budget must be 0 or greater.", file=sys.stderr)
        sys.exit(1)

    data = load_db()
    trip_id = f"trip_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    trip = {
        "id": trip_id,
        "name": args.name.strip(),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "budget": round(args.budget, 2),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "expenses": [],
    }
    data["trips"].append(trip)
    save_db(data)
    print(f"Created trip: {trip_id}")


def cmd_list(_: argparse.Namespace) -> None:
    data = load_db()
    trips = data["trips"]
    if not trips:
        print("No trips found. Create one with `create`.")
        return
    print("Trips:")
    for trip in trips:
        spent = sum(item["amount"] for item in trip.get("expenses", []))
        remaining = trip["budget"] - spent
        print(
            f"- {trip['id']} | {trip['name']} | {trip['start_date']} to {trip['end_date']} | "
            f"budget ${trip['budget']:.2f} | remaining ${remaining:.2f}"
        )


def cmd_add_expense(args: argparse.Namespace) -> None:
    if args.amount <= 0:
        print("Error: amount must be greater than 0.", file=sys.stderr)
        sys.exit(1)
    expense_date = parse_iso_date(args.date) if args.date else date.today()

    data = load_db()
    trip = find_trip(data, args.trip_id)
    expense = {
        "amount": round(args.amount, 2),
        "category": args.category.strip(),
        "note": args.note.strip(),
        "date": expense_date.isoformat(),
    }
    trip["expenses"].append(expense)
    save_db(data)
    print(f"Added ${expense['amount']:.2f} to {args.trip_id} ({expense['category']}).")


def cmd_summary(args: argparse.Namespace) -> None:
    data = load_db()
    trip = find_trip(data, args.trip_id)
    expenses = trip.get("expenses", [])
    spent = sum(item["amount"] for item in expenses)
    remaining = trip["budget"] - spent

    print(f"Trip: {trip['name']} ({trip['id']})")
    print(f"Dates: {trip['start_date']} to {trip['end_date']}")
    print(f"Budget: ${trip['budget']:.2f}")
    print(f"Spent: ${spent:.2f}")
    print(f"Remaining: ${remaining:.2f}")
    print()
    print("Expenses:")
    if not expenses:
        print("- none")
        return
    for item in expenses:
        print(f"- {item['date']} | ${item['amount']:.2f} | {item['category']} | {item['note']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Personal trip MVP tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a new trip")
    create.add_argument("--name", required=True, help="Trip name (e.g. Tokyo Spring)")
    create.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    create.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    create.add_argument("--budget", required=True, type=float, help="Trip budget")
    create.set_defaults(func=cmd_create)

    list_cmd = subparsers.add_parser("list", help="List trips")
    list_cmd.set_defaults(func=cmd_list)

    add_expense = subparsers.add_parser("add-expense", help="Add trip expense")
    add_expense.add_argument("--trip-id", required=True, help="Trip id")
    add_expense.add_argument("--amount", required=True, type=float, help="Expense amount")
    add_expense.add_argument("--category", required=True, help="Expense category")
    add_expense.add_argument("--note", default="", help="Optional expense note")
    add_expense.add_argument("--date", help="Expense date YYYY-MM-DD (default: today)")
    add_expense.set_defaults(func=cmd_add_expense)

    summary = subparsers.add_parser("summary", help="Show trip budget summary")
    summary.add_argument("--trip-id", required=True, help="Trip id")
    summary.set_defaults(func=cmd_summary)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
