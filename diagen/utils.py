def dtup2(direction: int, v1: float, v2: float) -> tuple[float, float]:
    if direction == 0:
        return v1, v2
    else:
        return v2, v1
