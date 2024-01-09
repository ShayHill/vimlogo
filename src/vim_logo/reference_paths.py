from paragraphs import par

_letter_m = par(
    """M 272.59623,185.12055 276.99076,191.38227 263.02201,236.16742 H 268.6392 L
    266.7642,241.78461 H 244.08451 L 257.33451,202.11274 H 237.46342 L
    226.15873,236.16742 H 231.77201 L 229.90092,241.78461 H 207.22123 L
    220.47123,202.11274 H 200.59623 L 189.29545,236.16742 H 194.98295 L
    193.03764,241.78461 H 170.35795 L 187.42045,190.80805 H 181.73295 L
    183.60404,185.12055 H 204.41264 L 210.10014,190.80805 H 215.71733 L
    221.40483,185.12055 H 238.39701 L 244.08451,190.80805 H 249.77201 L
    255.46342,185.12055 H 272.59623"""
)


def _get_pts_from_datastring(datastring: str) -> list[tuple[float, float]]:
    """Get a list of points from the datastring of an absolute, linear path."""
    words = datastring.split()
    command = "M"
    pts: list[tuple[float, float]] = []
    for word in words:
        if word in "MLHV":
            command = word
            continue
        if command in "ML":
            x, y = word.split(",")
            pts.append((float(x), float(y)))
        if command == "H":
            x = word
            pts.append((float(x), pts[-1][1]))
        if command == "V":
            y = word
            pts.append((pts[-1][0], float(y)))
    if pts[0] == pts[-1]:
        _ = pts.pop()
    return pts

ref_m = _get_pts_from_datastring(_letter_m)
# start from the upper-left corner (the -x, -y corner)
ref_m = ref_m[20:] + ref_m[:20]
