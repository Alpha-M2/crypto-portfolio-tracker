import csv


def export_portfolio(snapshot: list[dict], filepath: str):
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=snapshot[0].keys())
        writer.writeheader()
        writer.writerows(snapshot)
