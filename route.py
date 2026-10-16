import xml.etree.ElementTree as ET
from PIL import ImageDraw

def read_gpx(file_path: str) -> list[tuple[float, float]]:
    tree = ET.parse(file_path)
    root = tree.getroot()
    points = []
    for elem in root.iter():
        if 'trkpt' in elem.tag:
            lat = float(elem.attrib['lat'])
            lon = float(elem.attrib['lon'])
            points.append((lat, lon))
    return points

def draw_route(canvas, gpx_path: str, color: tuple = (252, 82, 0, 255)):
    points = read_gpx(gpx_path)
    if not points:
        return

    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    lat_diff = max_lat - min_lat
    lon_diff = max_lon - min_lon

    box_x = canvas.get_x(0.62)
    box_y = canvas.get_y(0.12)
    box_width = canvas.get_x(0.32)
    box_height = canvas.get_y(0.32)

    if lon_diff > 0 and lat_diff > 0:
        route_ratio = lon_diff / lat_diff
        box_ratio = box_width / box_height
        if route_ratio > box_ratio:
            box_height = box_width / route_ratio
        else:
            box_width = box_height * route_ratio

    pixel_points = []
    for lat, lon in points:
        x = box_x + ((lon - min_lon) / lon_diff) * box_width
        y = box_y + ((max_lat - lat) / lat_diff) * box_height
        pixel_points.append((x, y))

    draw = canvas.draw
    line_width = int(canvas.width * 0.0045)
    draw.line(pixel_points, fill=color, width=line_width, joint="curve")

    start_p, end_p = pixel_points[0], pixel_points[-1]
    r = int(canvas.width * 0.0055)

    draw.ellipse([start_p[0] - r, start_p[1] - r, start_p[0] + r, start_p[1] + r], fill=(255, 255, 255, 255))
    draw.ellipse([end_p[0] - r, end_p[1] - r, end_p[0] + r, end_p[1] + r], fill=color, outline=(255, 255, 255, 255),
                 width=2)