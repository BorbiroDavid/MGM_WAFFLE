import math

def detect_pillars(scan):
    """A LiDAR-meresekbol oszlopjeloltek (x, y) koordinatait adja vissza."""
    groups = []
    group = []
    previous = None
    previous_range = None

    for i, r in enumerate(scan.ranges):
        if not math.isfinite(r) or r < scan.range_min or r > scan.range_max:
            if group:
                groups.append(group)
            group = []
            previous = None
            previous_range = None
            continue

        angle = scan.angle_min + i * scan.angle_increment
        point = (r * math.cos(angle), r * math.sin(angle))

        if previous is not None:
            gap = math.hypot(point[0] - previous[0], point[1] - previous[1])
            limit = max(0.12, 2.5 * min(r, previous_range) * abs(scan.angle_increment))
            if gap > limit:
                if group:
                    groups.append(group)
                group = []

        group.append(point)
        previous = point
        previous_range = r

    if group:
        groups.append(group)

    if len(groups) > 1 and abs(scan.angle_increment) * len(scan.ranges) >= 6.2:
        first = groups[0][0]
        last = groups[-1][-1]
        if math.hypot(first[0] - last[0], first[1] - last[1]) < 0.12:
            groups[0] = groups[-1] + groups[0]
            groups.pop()

    pillars = []
    for points in groups:
        if len(points) < 3:
            continue

        width = math.hypot(points[-1][0] - points[0][0],
                           points[-1][1] - points[0][1])
        if not 0.05 <= width <= 0.40:
            continue

        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        d = math.hypot(x, y)
        if d > 0:
            pillars.append((x + 0.07 * x / d, y + 0.07 * y / d))

    return pillars
