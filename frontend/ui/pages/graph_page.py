import math
import random
import flet as ft
from flet import canvas as cv

from frontend.services.api_client import api_client
from frontend.config import COLORS, SIZES


class GraphPage:
    """Canvas-based interactive graph page for the air network."""

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.page = main_window.page
        self.api = api_client

        # Data
        self.airports = []
        self.routes = []

        # Layout
        self.positions = {}  # airport_id -> (x,y)
        self.canvas_width = 1600
        self.canvas_height = 1000

        # UI
        self.canvas = None
        self.stack = None
        self.detail_panel = None
        self.status_text = None
        self.highlight_path = None

    def build(self):
        # Left: graph area with native horizontal + vertical scrolling
        self.stack = ft.Stack(expand=True, width=self.canvas_width, height=self.canvas_height)
        graph_surface = ft.Container(
            content=self.stack,
            width=self.canvas_width,
            height=self.canvas_height,
            bgcolor=ft.Colors.WHITE,
        )

        horizontal_scroll = ft.Row(
            controls=[graph_surface],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )

        scrollable_graph = ft.Column(
            controls=[horizontal_scroll],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )

        # status line + viewer
        self.status_text = ft.Text("Mapa: sin datos", size=12)
        graph_panel = ft.Container(
            content=ft.Column([
                self.status_text,
                scrollable_graph
            ], expand=True),
            expand=True,
            padding=10,
            bgcolor=COLORS["BACKGROUND"]
        )

        # Right: details + legend
        self.detail_panel = ft.Column([
            ft.Text("Información del aeropuerto", weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Selecciona un nodo para ver detalles.")
        ], width=320, spacing=8)

        layout = ft.Row([
            graph_panel,
            ft.VerticalDivider(width=1),
            ft.Container(self.detail_panel, padding=10)
        ], expand=True)

        return layout

    async def load_data(self):
        """Async: load graph data from backend and render."""
        try:
            print('[DEBUG][GraphPage] Calling API get_graph_data()')
            data = await self.api.get_graph_data()
            print(f"[DEBUG][GraphPage] Received graph data keys: {list(data.keys())}")
            self.airports = data.get("airports", [])
            self.routes = data.get("routes", [])
            print(f"[DEBUG][GraphPage] airports={len(self.airports)} routes={len(self.routes)}")

            # update status
            if self.status_text:
                self.status_text.value = f"Aeropuertos: {len(self.airports)} | Rutas: {len(self.routes)}"
            # compute initial layout only when the graph view has been built
            if self.stack is not None:
                self._compute_layout()
                self._render_graph()
        except Exception as e:
            print(f"[ERROR][GraphPage] load_data failed: {e}")
            self.main.show_error(str(e))

    def visualize_path(self, path: list[str]):
        """Highlight a path (list of airport ids) and re-render."""
        self.highlight_path = path
        self._render_graph()

    def _compute_layout(self):
        """Simple force-directed layout.

        Deterministic-ish: seed the random generator so layout is stable.
        """
        n = len(self.airports)
        if n == 0:
            return

        # initialize positions on a grid
        rnd = random.Random(42)
        margin = 80
        for a in self.airports:
            aid = a["id"]
            self.positions[aid] = (
                rnd.uniform(margin, self.canvas_width - margin),
                rnd.uniform(margin, self.canvas_height - margin)
            )

        # build adjacency for springs
        adj = {a["id"]: set() for a in self.airports}
        for r in self.routes:
            adj[r["origin_id"]].add(r["destination_id"])

        # parameters
        area = self.canvas_width * self.canvas_height
        k = math.sqrt(area / max(1, n))
        iterations = 70

        for _ in range(iterations):
            disp = {aid: [0.0, 0.0] for aid in adj}

            # repulsive forces
            ids = list(adj.keys())
            for i in range(n):
                for j in range(i + 1, n):
                    u = ids[i]
                    v = ids[j]
                    (x1, y1) = self.positions[u]
                    (x2, y2) = self.positions[v]
                    dx = x1 - x2
                    dy = y1 - y2
                    dist = math.hypot(dx, dy) + 0.01
                    force = (k * k) / dist
                    disp[u][0] += (dx / dist) * force
                    disp[u][1] += (dy / dist) * force
                    disp[v][0] -= (dx / dist) * force
                    disp[v][1] -= (dy / dist) * force

            # attractive (spring) forces along edges
            for u, neighbors in adj.items():
                for v in neighbors:
                    (x1, y1) = self.positions[u]
                    (x2, y2) = self.positions[v]
                    dx = x1 - x2
                    dy = y1 - y2
                    dist = math.hypot(dx, dy) + 0.01
                    # ideal distance depends on hub status
                    ideal = 120
                    f = (dist * dist) / k
                    disp[u][0] -= (dx / dist) * f
                    disp[u][1] -= (dy / dist) * f
                    disp[v][0] += (dx / dist) * f
                    disp[v][1] += (dy / dist) * f

            # update positions
            temp = max(self.canvas_width, self.canvas_height) / 10.0
            for aid in ids:
                dx, dy = disp[aid]
                (x, y) = self.positions[aid]
                x = x + (dx / (1 + abs(dx))) * 0.1
                y = y + (dy / (1 + abs(dy))) * 0.1
                # keep inside bounds
                margin = 40
                x = max(margin, min(self.canvas_width - margin, x))
                y = max(margin, min(self.canvas_height - margin, y))
                self.positions[aid] = (x, y)

    def _render_graph(self):
        """Render canvas shapes and overlay node controls."""
        if self.stack is None:
            return

        shapes = []

        # helper to get pos
        def pos(aid):
            return self.positions.get(aid, (self.canvas_width / 2, self.canvas_height / 2))

        # compute path sets
        path_edges = set()
        path_nodes = set()
        if self.highlight_path and len(self.highlight_path) >= 2:
            path_nodes = set(self.highlight_path)
            path_edges = set(zip(self.highlight_path[:-1], self.highlight_path[1:]))

        # Draw edges first
        airport_index = {a["id"]: a for a in self.airports}
        for r in self.routes:
            o = r["origin_id"]
            d = r["destination_id"]
            x1, y1 = pos(o)
            x2, y2 = pos(d)

            origin_hub = airport_index.get(o, {}).get("es_hub", False)
            destination_hub = airport_index.get(d, {}).get("es_hub", False)
            origin_radius = 21 if origin_hub else 14
            destination_radius = 21 if destination_hub else 14

            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist < 0.001:
                continue
            ux = dx / dist
            uy = dy / dist

            # shorten line so arrows sit at node border instead of node center
            line_start_x = x1 + ux * origin_radius
            line_start_y = y1 + uy * origin_radius
            line_end_x = x2 - ux * destination_radius
            line_end_y = y2 - uy * destination_radius

            in_path = (o, d) in path_edges
            is_blocked = bool(r.get("blocked", False)) or (not bool(r.get("is_available", True)))
            if is_blocked:
                color = ft.Colors.ORANGE_700
                width = 3.0
            else:
                color = ft.Colors.RED if in_path else ft.Colors.BLACK_26
                width = 3.5 if in_path else 1.2

            paint = ft.Paint(color=color, stroke_width=width, stroke_cap=ft.StrokeCap.ROUND)
            shapes.append(cv.Line(line_start_x, line_start_y, line_end_x, line_end_y, paint=paint))

            # arrowhead
            ang = math.atan2(line_end_y - line_start_y, line_end_x - line_start_x)
            ah = 12 if in_path else 10
            p1 = (line_end_x, line_end_y)
            p2 = (
                line_end_x - ah * math.cos(ang - 0.45),
                line_end_y - ah * math.sin(ang - 0.45),
            )
            p3 = (
                line_end_x - ah * math.cos(ang + 0.45),
                line_end_y - ah * math.sin(ang + 0.45),
            )
            shapes.append(cv.Points([p1, p2, p3], point_mode=cv.PointMode.POLYGON, paint=ft.Paint(color=color)))

            # edge label: only distance in kilometers
            label = f"{r.get('distance_km', 0)} km"
            if is_blocked:
                label = f"BLOQ · {label}"

            mx = line_start_x + (line_end_x - line_start_x) * 0.35
            my = line_start_y + (line_end_y - line_start_y) * 0.35

            # background rect
            padding = 6
            approx_w = max(40, len(label) * 6)
            shapes.append(cv.Rect(mx - approx_w / 2 - padding / 2, my - 12 - padding / 2, approx_w + padding, 18 + padding, paint=ft.Paint(color=ft.Colors.WHITE)))
            shapes.append(cv.Text(mx - approx_w / 2 + 4, my - 2, value=label, style=ft.TextStyle(size=10), text_align=ft.TextAlign.START))

        # reset stack children: canvas bottom + nodes
        children = []

        for a in self.airports:
            aid = a["id"]
            x, y = pos(aid)
            is_hub = a.get("es_hub", False)
            in_path_node = aid in path_nodes

            # node visual
            # use common Colors constants for better contrast
            color = ft.Colors.BLUE if not is_hub else ft.Colors.AMBER
            if in_path_node:
                if aid == (self.highlight_path[0] if self.highlight_path else None):
                    color = ft.Colors.ORANGE
                elif aid == (self.highlight_path[-1] if self.highlight_path else None):
                    color = ft.Colors.LIGHT_GREEN
                else:
                    color = ft.Colors.RED

            size = 28 if not is_hub else 42

            # draw a small marker on canvas to improve visibility of node center
            marker_paint = ft.Paint(color=ft.Colors.BLACK if is_hub else ft.Colors.BLUE, stroke_width=2)
            shapes.append(cv.Circle(x, y, radius=5 if not is_hub else 7, paint=marker_paint))

            node = ft.Container(
                width=size,
                height=size,
                bgcolor=color,
                border_radius=size // 2,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(aid, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                left=x - size / 2,
                top=y - size / 2,
                tooltip=f"{a.get('ciudad','')} - {a.get('pais','')}\nZona: {a.get('zona_horaria','')}",
            )

            # click handler
            def make_onclick(_aid):
                def _on_click(e):
                    try:
                        self.page.run_task(self._load_airport_details(_aid))
                    except Exception:
                        import asyncio
                        asyncio.create_task(self._load_airport_details(_aid))
                return _on_click

            node.on_click = make_onclick(aid)

            children.append(node)

        # Build canvas after all shapes are added
        self.canvas = cv.Canvas(shapes=shapes, width=self.canvas_width, height=self.canvas_height)
        children.insert(0, self.canvas)

        print(f"[DEBUG][GraphPage] Built {len(shapes)} canvas shapes")

        if self.status_text:
            blocked_count = sum(1 for r in self.routes if bool(r.get("blocked", False)) or (not bool(r.get("is_available", True))))
            self.status_text.value = (
                f"Aeropuertos: {len(self.airports)} | Rutas: {len(self.routes)} "
                f"| Bloqueadas: {blocked_count} | Shapes: {len(shapes)}"
            )

        # apply to stack
        self.stack.controls = children
        self.page.update()

    async def _load_airport_details(self, airport_id: str):
        try:
            data = await self.api.get_airport_details(airport_id)
            # Build detail panel
            items = [
                ft.Text(f"{data.get('nombre','')} ({data.get('id',airport_id)})", weight=ft.FontWeight.BOLD),
                ft.Text(f"Ciudad: {data.get('ciudad','-')}") ,
                ft.Text(f"País: {data.get('pais','-')}") ,
                ft.Text(f"Zona horaria: {data.get('zona_horaria','-')}") ,
                ft.Divider()
            ]

            # airlines not provided in dataset; try to infer from connected_airports if present
            connected = data.get('connected_airports', [])
            aircraft_types = set()
            for c in connected:
                for at in c.get('aircraft_types', []) or []:
                    aircraft_types.add(at)

            if aircraft_types:
                items.append(ft.Text(f"Tipos de aeronave disponibles: {', '.join(sorted(aircraft_types))}"))
            else:
                items.append(ft.Text("Aerolíneas: (no disponible en los datos)"))

            self.detail_panel.controls = items
            self.page.update()

        except Exception as e:
            self.main.show_error(str(e))
