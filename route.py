import xml.etree.ElementTree as ET
from typing import Union, BinaryIO, List, Tuple

def read_gpx(file_source: Union[str, BinaryIO]) -> List[Tuple[float, float]]:
    """
    Extrai as coordenadas da tag <trkpt> do XML nativo de dispositivos GPS.
    """
    tree = ET.parse(file_source)
    root = tree.getroot()
    points = []

    for elem in root.iter():
        if 'trkpt' in elem.tag:
            lat = float(elem.attrib['lat'])
            lon = float(elem.attrib['lon'])
            points.append((lat, lon))

    return points

def draw_route_from_points(canvas, points: List[Tuple[float, float]],
                           color: Tuple[int, int, int, int] = (252, 82, 0, 255)) -> None:
    """
    Transpõe coordenadas geográficas (Lat/Lon) para a resolução em pixels do Canvas.
    Garante que a rota respeite o aspect-ratio geográfico enquanto ocupa
    proporcionalmente a bounding-box delimitada no layout do poster.
    """
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

    # Adapta o bounding-box mantendo a escala real do terreno percorrido
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

    line_width = int(canvas.width * 0.0045)
    canvas.draw.line(pixel_points, fill=color, width=line_width, joint="curve")

    # Demarca o início (Branco) e o fim (Laranja com borda branca) da rota
    start_p, end_p = pixel_points[0], pixel_points[-1]
    radius = int(canvas.width * 0.0055)

    canvas.draw.ellipse([start_p[0] - radius, start_p[1] - radius, start_p[0] + radius, start_p[1] + radius],
                        fill=(255, 255, 255, 255))
    canvas.draw.ellipse([end_p[0] - radius, end_p[1] - radius, end_p[0] + radius, end_p[1] + radius], fill=color,
                        outline=(255, 255, 255, 255), width=2)

def draw_route(canvas, gpx_source: Union[str, BinaryIO], color: Tuple[int, int, int, int] = (252, 82, 0, 255)) -> None:
    points = read_gpx(gpx_source)
    draw_route_from_points(canvas, points, color)