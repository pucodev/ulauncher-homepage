def plural_text(zero: str, one: str, many: str, count: int) -> str:
    if count == 0:
        return zero

    if count == 1:
        return one

    return many
