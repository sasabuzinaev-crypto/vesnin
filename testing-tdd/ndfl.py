def calculate_tax(income):
    tiers = [
        (50_000_000, 7_020_000, 0.22),
        (20_000_000, 1_020_000, 0.20),
        (5_000_000, 702_000, 0.18),
        (2_400_000, 312_000, 0.15),
        (0, 0, 0.13)
    ]

    for start, addition, rate in tiers:
        if income > start:
            return addition + (income - start) * rate