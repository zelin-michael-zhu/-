def convert_to_4(value: float | None, scale: float | None) -> float | None:
    if value is None or scale is None:
        return None
    if scale == 4.0:
        return round(value, 2)
    if scale == 5.0:
        return round(value / 5 * 4, 2)
    if scale == 100:
        if value >= 90:
            return 4.0
        if value >= 85:
            return 3.7
        if value >= 80:
            return 3.3
        if value >= 75:
            return 3.0
        if value >= 70:
            return 2.7
        if value >= 65:
            return 2.3
        if value >= 60:
            return 2.0
        return 0
    return round(min(4, value / scale * 4), 2)
