import ctypes
import json
import os
import sys
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

THEMES = {
    "dark": {
        "background": "#0D1117",
        "surface": "#161B22",
        "surface_alt": "#21262D",
        "border": "#30363D",
        "text": "#E6EDF3",
        "muted": "#8B949E",
        "accent": "#2F81F7",
        "accent_text": "#FFFFFF",
        "error": "#FF7B72",
    },
    "light": {
        "background": "#FFFFFF",
        "surface": "#F6F8FA",
        "surface_alt": "#F3F4F6",
        "border": "#D1D9E0",
        "text": "#1F2328",
        "muted": "#59636E",
        "accent": "#0969DA",
        "accent_text": "#FFFFFF",
        "error": "#CF222E",
    },
}


@dataclass(frozen=True)
class ClockLocation:
    name: str
    country: str
    timezone: str
    longitude: float
    latitude: float
    region: str


LOCATIONS = tuple(
    ClockLocation(*location)
    for location in (
        ("Anchorage", "United States", "America/Anchorage", -149.9, 61.2, "Americas"),
        ("Vancouver", "Canada", "America/Vancouver", -123.1, 49.3, "Americas"),
        ("Los Angeles", "United States", "America/Los_Angeles", -118.2, 34.1, "Americas"),
        ("Denver", "United States", "America/Denver", -104.9, 39.7, "Americas"),
        ("Mexico City", "Mexico", "America/Mexico_City", -99.1, 19.4, "Americas"),
        ("Chicago", "United States", "America/Chicago", -87.6, 41.9, "Americas"),
        ("New York", "United States", "America/New_York", -73.98, 40.75, "Americas"),
        ("Toronto", "Canada", "America/Toronto", -79.4, 43.7, "Americas"),
        ("Halifax", "Canada", "America/Halifax", -63.6, 44.6, "Americas"),
        ("St. John's", "Canada", "America/St_Johns", -52.7, 47.6, "Americas"),
        ("Guatemala City", "Guatemala", "America/Guatemala", -90.5, 14.6, "Americas"),
        ("Panama City", "Panama", "America/Panama", -79.5, 9.0, "Americas"),
        ("Bogotá", "Colombia", "America/Bogota", -74.1, 4.7, "Americas"),
        ("Lima", "Peru", "America/Lima", -77.0, -12.0, "Americas"),
        ("Caracas", "Venezuela", "America/Caracas", -66.9, 10.5, "Americas"),
        ("La Paz", "Bolivia", "America/La_Paz", -68.1, -16.5, "Americas"),
        ("Santiago", "Chile", "America/Santiago", -70.7, -33.4, "Americas"),
        ("Buenos Aires", "Argentina", "America/Argentina/Buenos_Aires", -58.4, -34.6, "Americas"),
        ("São Paulo", "Brazil", "America/Sao_Paulo", -46.6, -23.6, "Americas"),
        ("Reykjavík", "Iceland", "Atlantic/Reykjavik", -21.9, 64.1, "Europe"),
        ("London", "United Kingdom", "Europe/London", -0.1, 51.5, "Europe"),
        ("Dublin", "Ireland", "Europe/Dublin", -6.3, 53.3, "Europe"),
        ("Lisbon", "Portugal", "Europe/Lisbon", -9.1, 38.7, "Europe"),
        ("Madrid", "Spain", "Europe/Madrid", -3.7, 40.4, "Europe"),
        ("Paris", "France", "Europe/Paris", 2.4, 48.9, "Europe"),
        ("Brussels", "Belgium", "Europe/Brussels", 4.4, 50.9, "Europe"),
        ("Amsterdam", "Netherlands", "Europe/Amsterdam", 4.9, 52.4, "Europe"),
        ("Berlin", "Germany", "Europe/Berlin", 13.4, 52.5, "Europe"),
        ("Copenhagen", "Denmark", "Europe/Copenhagen", 12.6, 55.7, "Europe"),
        ("Oslo", "Norway", "Europe/Oslo", 10.8, 59.9, "Europe"),
        ("Stockholm", "Sweden", "Europe/Stockholm", 18.1, 59.3, "Europe"),
        ("Helsinki", "Finland", "Europe/Helsinki", 25.0, 60.2, "Europe"),
        ("Warsaw", "Poland", "Europe/Warsaw", 21.0, 52.2, "Europe"),
        ("Prague", "Czechia", "Europe/Prague", 14.4, 50.1, "Europe"),
        ("Vienna", "Austria", "Europe/Vienna", 16.4, 48.2, "Europe"),
        ("Zurich", "Switzerland", "Europe/Zurich", 8.54, 47.38, "Europe"),
        ("Rome", "Italy", "Europe/Rome", 12.5, 41.9, "Europe"),
        ("Athens", "Greece", "Europe/Athens", 23.7, 38.0, "Europe"),
        ("Bucharest", "Romania", "Europe/Bucharest", 26.1, 44.4, "Europe"),
        ("Kyiv", "Ukraine", "Europe/Kyiv", 30.5, 50.5, "Europe"),
        ("Istanbul", "Türkiye", "Europe/Istanbul", 28.8, 41.3, "Europe"),
        ("Moscow", "Russia", "Europe/Moscow", 37.6, 55.8, "Europe"),
        ("Jerusalem", "Israel", "Asia/Jerusalem", 35.2, 31.8, "Asia"),
        ("Riyadh", "Saudi Arabia", "Asia/Riyadh", 46.7, 24.7, "Asia"),
        ("Dubai", "United Arab Emirates", "Asia/Dubai", 55.3, 25.2, "Asia"),
        ("Tehran", "Iran", "Asia/Tehran", 51.4, 35.7, "Asia"),
        ("Karachi", "Pakistan", "Asia/Karachi", 67.0, 24.9, "Asia"),
        ("Mumbai", "India", "Asia/Kolkata", 72.9, 19.1, "Asia"),
        ("New Delhi", "India", "Asia/Kolkata", 77.2, 28.6, "Asia"),
        ("Kathmandu", "Nepal", "Asia/Kathmandu", 85.3, 27.7, "Asia"),
        ("Dhaka", "Bangladesh", "Asia/Dhaka", 90.4, 23.8, "Asia"),
        ("Bangkok", "Thailand", "Asia/Bangkok", 100.5, 13.8, "Asia"),
        ("Jakarta", "Indonesia", "Asia/Jakarta", 106.8, -6.2, "Asia"),
        ("Kuala Lumpur", "Malaysia", "Asia/Kuala_Lumpur", 101.7, 3.1, "Asia"),
        ("Singapore", "Singapore", "Asia/Singapore", 103.8, 1.3, "Asia"),
        ("Manila", "Philippines", "Asia/Manila", 120.98, 14.6, "Asia"),
        ("Hong Kong", "China", "Asia/Hong_Kong", 114.2, 22.3, "Asia"),
        ("Beijing", "China", "Asia/Shanghai", 116.4, 39.9, "Asia"),
        ("Seoul", "South Korea", "Asia/Seoul", 127.0, 37.6, "Asia"),
        ("Tokyo", "Japan", "Asia/Tokyo", 139.7, 35.7, "Asia"),
    )
)
LOCATION_BY_TIMEZONE = {location.timezone: location for location in LOCATIONS}
LOCATION_BY_NAME = {location.name: location for location in LOCATIONS}
COUNTRY_LOCATION_NAMES = {
    "AE": "Dubai", "AR": "Buenos Aires", "AT": "Vienna", "BD": "Dhaka", "BE": "Brussels",
    "BO": "La Paz", "BR": "São Paulo", "CA": "Toronto", "CH": "Zurich",
    "CL": "Santiago", "CN": "Beijing", "CO": "Bogotá", "CZ": "Prague",
    "DE": "Berlin", "DK": "Copenhagen", "ES": "Madrid", "FI": "Helsinki",
    "FR": "Paris", "GB": "London", "GR": "Athens", "GT": "Guatemala City",
    "IE": "Dublin", "ID": "Jakarta", "IL": "Jerusalem", "IN": "New Delhi",
    "IR": "Tehran", "IS": "Reykjavík", "IT": "Rome", "JP": "Tokyo",
    "KR": "Seoul", "MX": "Mexico City", "MY": "Kuala Lumpur", "NL": "Amsterdam",
    "NO": "Oslo", "NP": "Kathmandu", "PA": "Panama City", "PE": "Lima",
    "PH": "Manila", "PK": "Karachi", "PL": "Warsaw", "PT": "Lisbon",
    "RO": "Bucharest", "RU": "Moscow", "SA": "Riyadh", "SE": "Stockholm",
    "SG": "Singapore", "TH": "Bangkok", "TR": "Istanbul",
    "UA": "Kyiv", "US": "New York", "VE": "Caracas",
}
LOCATION_SEARCH_OPTIONS = tuple(
    sorted(
        {location.country for location in LOCATIONS}
        | {location.name for location in LOCATIONS},
        key=str.casefold,
    )
)


def find_location_search_matches(query: str) -> tuple[str, ...]:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return LOCATION_SEARCH_OPTIONS
    return tuple(
        option
        for option in LOCATION_SEARCH_OPTIONS
        if normalized_query in option.casefold()
    )


def representative_location_for_country(country: str) -> ClockLocation | None:
    normalized_country = country.strip().casefold()
    if not normalized_country:
        return None
    matching_locations = tuple(
        location
        for location in LOCATIONS
        if location.country.casefold() == normalized_country
    )
    if not matching_locations:
        return None
    for location_name in COUNTRY_LOCATION_NAMES.values():
        location = LOCATION_BY_NAME.get(location_name)
        if location in matching_locations:
            return location
    return matching_locations[0]


def resolve_location_search(query: str) -> ClockLocation | None:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return None
    location = next(
        (
            location
            for location in LOCATIONS
            if location.name.casefold() == normalized_query
        ),
        None,
    )
    if location is not None:
        return location
    return representative_location_for_country(query)


def format_utc_offset(value: datetime) -> str:
    offset = value.strftime("%z")
    if len(offset) != 5:
        return "UTC"
    return f"UTC{offset[:3]}:{offset[3:]}"


MAP_LOCATIONS = tuple(
    LOCATION_BY_NAME[name]
    for name in (
        "Anchorage", "Vancouver", "Los Angeles", "Mexico City", "Chicago",
        "New York", "São Paulo", "Buenos Aires",
        "Reykjavík", "London", "Madrid", "Berlin", "Rome", "Moscow",
        "Jerusalem", "Dubai", "New Delhi", "Bangkok", "Singapore",
        "Beijing", "Tokyo",
    )
)
MAP_LATITUDE_MIN = -65
MAP_LATITUDE_MAX = 75
MAP_ZOOM = 1.05
MAP_PADDING = 18
MAP_COLORS = {
    "background": "#0B1220",
    "land": "#18273B",
    "coast": "#263B55",
    "grid": "#172438",
    "Americas": "#68A7FF",
    "Europe": "#55D6A4",
    "Asia": "#F2BA64",
}


def project_map_coordinates(
    longitude: float,
    latitude: float,
    width: int,
    height: int,
) -> tuple[float, float]:
    scale = min(
        (width - 2 * MAP_PADDING) / 360,
        (height - 2 * MAP_PADDING) / (MAP_LATITUDE_MAX - MAP_LATITUDE_MIN),
    )
    center_latitude = (MAP_LATITUDE_MIN + MAP_LATITUDE_MAX) / 2
    x = width / 2 + longitude * scale * MAP_ZOOM
    y = height / 2 + (center_latitude - latitude) * scale * MAP_ZOOM
    return x, y


def location_for_country(country_code: str | None) -> ClockLocation | None:
    if not country_code:
        return None
    location_name = COUNTRY_LOCATION_NAMES.get(country_code.upper())
    return LOCATION_BY_NAME.get(location_name) if location_name else None


def detect_local_location() -> ClockLocation | None:
    country_code = None
    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_country = kernel32.GetUserDefaultGeoName
        get_country.argtypes = [ctypes.POINTER(ctypes.c_wchar), ctypes.c_int]
        get_country.restype = ctypes.c_int
        country_buffer = ctypes.create_unicode_buffer(16)
        if get_country(country_buffer, len(country_buffer)):
            country_code = country_buffer.value
    return location_for_country(country_code)


def set_app_identity() -> None:
    if sys.platform != "win32":
        return
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    set_id = shell32.SetCurrentProcessExplicitAppUserModelID
    set_id.argtypes = [ctypes.c_wchar_p]
    set_id.restype = ctypes.c_long
    result = set_id("CLF.DigitalClock")
    if result < 0:
        raise OSError(
            f"Could not set Windows app identity "
            f"(HRESULT 0x{result & 0xFFFFFFFF:08X})"
        )


def get_resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS")) / "sysclock"
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)


def load_land_polygons(
    geojson_path: Path,
) -> tuple[tuple[tuple[float, float], ...], ...]:
    data = json.loads(geojson_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        raise ValueError(f"Invalid world map GeoJSON: {geojson_path}")

    polygons = []
    for feature in data["features"]:
        geometry = feature.get("geometry", {}) if isinstance(feature, dict) else {}
        coordinates = geometry.get("coordinates", []) if isinstance(geometry, dict) else []
        if geometry.get("type") == "Polygon":
            polygon_rings = coordinates
        elif geometry.get("type") == "MultiPolygon":
            polygon_rings = [ring for polygon in coordinates for ring in polygon]
        else:
            continue
        if polygon_rings:
            outline = tuple(
                (float(point[0]), float(point[1]))
                for point in polygon_rings[0]
            )
            if outline:
                polygons.append(outline)
    if not polygons:
        raise ValueError(f"World map GeoJSON contains no land polygons: {geojson_path}")
    return tuple(polygons)


def load_saved_settings(settings_path: Path) -> tuple[dict[str, str], str | None]:
    defaults = {"theme": "dark", "time_format": "24h", "location": "local"}
    if not settings_path.exists():
        return defaults, None
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return defaults, f"Could not read saved settings: {error}"
    if not isinstance(settings, dict):
        return defaults, "Saved settings are invalid. Using default settings."

    warnings = []
    if "location" not in settings and isinstance(settings.get("timezone"), str):
        timezone = settings["timezone"]
        matching_location = LOCATION_BY_TIMEZONE.get(timezone)
        settings["location"] = matching_location.name if matching_location else "local"

    for key, allowed in (
        ("theme", THEMES),
        ("time_format", {"12h", "24h"}),
        ("location", {"local", *LOCATION_BY_NAME}),
    ):
        value = settings.get(key, defaults[key])
        if isinstance(value, str) and value in allowed:
            defaults[key] = value
        else:
            warnings.append(f"Invalid {key.replace('_', ' ')}; using its default.")
    return defaults, " ".join(warnings) or None


def set_windows_window_icon(window: tk.Tk, icon_path: Path) -> list[int]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    load_image = user32.LoadImageW
    load_image.argtypes = [
        ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint,
        ctypes.c_int, ctypes.c_int, ctypes.c_uint,
    ]
    load_image.restype = ctypes.c_void_p
    get_system_metrics = user32.GetSystemMetrics
    get_system_metrics.argtypes = [ctypes.c_int]
    get_system_metrics.restype = ctypes.c_int
    get_ancestor = user32.GetAncestor
    get_ancestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    get_ancestor.restype = ctypes.c_void_p
    send_message = user32.SendMessageW
    send_message.argtypes = [
        ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t,
    ]
    send_message.restype = ctypes.c_ssize_t
    destroy_icon = user32.DestroyIcon
    destroy_icon.argtypes = [ctypes.c_void_p]

    handles = []
    for metric in (11, 49):
        size = get_system_metrics(metric)
        handle = load_image(None, str(icon_path), 1, size, size, 0x0010)
        if not handle:
            for loaded in handles:
                destroy_icon(loaded)
            raise ctypes.WinError(ctypes.get_last_error())
        handles.append(handle)

    hwnd = get_ancestor(window.winfo_id(), 2)
    if not hwnd:
        for handle in handles:
            destroy_icon(handle)
        raise ctypes.WinError(ctypes.get_last_error())
    send_message(hwnd, 0x0080, 1, handles[0])
    send_message(hwnd, 0x0080, 0, handles[1])
    return handles


class DigitalClock:
    def __init__(
        self,
        window: tk.Tk,
        theme_settings_path: Path | None = None,
    ) -> None:
        self.window = window
        self.theme_settings_path = (
            theme_settings_path or self.default_theme_settings_path()
        )
        preferences, self.settings_warning = load_saved_settings(self.theme_settings_path)
        self.current_theme = preferences["theme"]
        self.time_format = preferences["time_format"]
        self.selected_location = LOCATION_BY_NAME.get(preferences["location"])
        self.local_location = detect_local_location()
        self.land_polygons = load_land_polygons(
            get_resource_path("assets", "world_land.geojson")
        )
        self.active_page = "clock"
        self.themed_frames: list[tuple[tk.Frame, str]] = []
        self.themed_labels: list[tuple[tk.Label, str, str]] = []
        self.themed_buttons: list[tuple[tk.Button, str]] = []
        self.map_markers: dict[int, ClockLocation] = {}
        self.hovered_location: ClockLocation | None = None
        self.highlighted_location: ClockLocation | None = None
        self.highlight_step = 0
        self.highlight_after_id: str | None = None
        self.search_status_error = False

        window.title("Digital Clock")
        window.geometry("1000x720")
        window.minsize(800, 620)
        window.configure(bg=THEMES[self.current_theme]["background"])
        window.protocol("WM_DELETE_WINDOW", self.close)

        self.load_app_icon()
        self.build_layout()
        self.apply_theme()
        self.update_clock()

    @staticmethod
    def default_theme_settings_path() -> Path:
        app_data = Path(os.environ.get("APPDATA", Path.home()))
        return app_data / "DigitalClock" / "settings.json"

    def load_app_icon(self) -> None:
        self.app_icon_image = tk.PhotoImage(
            file=str(get_resource_path("assets", "digital_clock_icon.png"))
        )
        self.header_icon_image = tk.PhotoImage(
            file=str(get_resource_path("assets", "digital_clock_header_icon.png"))
        )
        self.window.iconphoto(True, self.app_icon_image)
        self.icon_handles: list[int] = []
        if sys.platform == "win32":
            icon_path = get_resource_path("assets", "digital_clock_icon.ico")
            self.window.iconbitmap(default=str(icon_path))
            self.window.update_idletasks()
            self.icon_handles = set_windows_window_icon(self.window, icon_path)

    def create_frame(
        self,
        parent: tk.Widget,
        color_role: str = "background",
        **options: object,
    ) -> tk.Frame:
        frame = tk.Frame(parent, bd=0, **options)
        self.themed_frames.append((frame, color_role))
        return frame

    def create_label(
        self,
        parent: tk.Widget,
        text: str,
        *,
        foreground: str = "text",
        background: str = "background",
        **options: object,
    ) -> tk.Label:
        label = tk.Label(parent, text=text, bd=0, **options)
        self.themed_labels.append((label, foreground, background))
        return label

    def create_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        *,
        role: str = "surface_alt",
        **options: object,
    ) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            bd=0,
            cursor="hand2",
            **options,
        )
        self.themed_buttons.append((button, role))
        return button

    def build_layout(self) -> None:
        self.content = self.create_frame(self.window, padx=26, pady=18)
        self.content.pack(fill="both", expand=True)

        self.toolbar = self.create_frame(self.content)
        self.toolbar.pack(fill="x")
        self.toolbar.grid_columnconfigure(1, weight=1)
        self.header_icon = tk.Label(
            self.toolbar,
            image=self.header_icon_image,
            bd=0,
        )
        self.header_icon.grid(row=0, column=0, padx=(0, 9))
        self.themed_labels.append((self.header_icon, "text", "background"))
        self.app_title = self.create_label(
            self.toolbar,
            "Digital Clock",
            font=("Segoe UI", 11, "bold"),
        )
        self.app_title.grid(row=0, column=1, sticky="w")
        self.local_time_button = self.create_button(
            self.toolbar,
            "Local",
            lambda: self.set_timezone("local"),
            role="local",
            font=("Segoe UI", 9),
            padx=12,
            pady=7,
        )
        self.local_time_button.grid(row=0, column=2, sticky="e", padx=(0, 8))
        self.settings_button = self.create_button(
            self.toolbar,
            "Settings",
            lambda: self.show_page("settings"),
            font=("Segoe UI", 9),
            padx=12,
            pady=7,
        )
        self.settings_button.grid(row=0, column=3, sticky="e")

        self.clock_page = self.create_frame(self.content)
        self.clock_page.pack(fill="both", expand=True, pady=(18, 0))
        self.clock_page.grid_columnconfigure(0, weight=1)
        self.clock_page.grid_rowconfigure(6, weight=1)
        self.clock_label = self.create_label(
            self.clock_page,
            "",
            font=("Segoe UI Light", 52),
            anchor="center",
        )
        self.clock_label.grid(row=0, column=0, sticky="ew")
        self.date_label = self.create_label(
            self.clock_page,
            "",
            foreground="muted",
            font=("Segoe UI", 12),
            anchor="center",
        )
        self.date_label.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        self.clock_timezone = self.create_label(
            self.clock_page,
            "",
            foreground="muted",
            font=("Segoe UI", 9),
            anchor="center",
        )
        self.clock_timezone.grid(row=2, column=0, sticky="ew", pady=(0, 14))

        self.map_heading = self.create_label(
            self.clock_page,
            "WORLD CLOCK",
            foreground="muted",
            font=("Segoe UI", 9, "bold"),
        )
        self.map_heading.grid(row=3, column=0, sticky="w", pady=(0, 8))
        self.map_search_panel = self.create_frame(self.clock_page)
        self.map_search_panel.grid(row=4, column=0, sticky="ew", pady=(0, 5))
        self.map_search_panel.grid_columnconfigure(1, weight=1)
        self.map_search_label = self.create_label(
            self.map_search_panel,
            "Search country or city",
            foreground="muted",
            font=("Segoe UI", 9),
        )
        self.map_search_label.grid(row=0, column=0, sticky="w")
        self.location_style = ttk.Style(self.window)
        self.location_style.theme_use("clam")
        self.location_search_variable = tk.StringVar(self.window)
        self.location_search = ttk.Combobox(
            self.map_search_panel,
            textvariable=self.location_search_variable,
            values=LOCATION_SEARCH_OPTIONS,
            state="normal",
            style="WorldClock.TCombobox",
        )
        self.location_search.grid(row=0, column=1, sticky="ew", padx=(12, 8))
        self.location_search.bind("<KeyRelease>", self.on_location_search_key_release)
        self.location_search.bind("<Return>", self.submit_location_search)
        self.location_search.bind(
            "<<ComboboxSelected>>",
            self.on_location_search_selected,
        )
        self.search_button = self.create_button(
            self.map_search_panel,
            "Go",
            self.submit_location_search,
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=6,
        )
        self.search_button.grid(row=0, column=2, sticky="e")
        self.map_search_status = self.create_label(
            self.clock_page,
            "",
            foreground="muted",
            font=("Segoe UI", 8),
            anchor="w",
        )
        self.map_search_status.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        self.map_canvas = tk.Canvas(
            self.clock_page,
            height=340,
            bd=0,
            highlightthickness=1,
        )
        self.map_canvas.grid(row=6, column=0, sticky="nsew")
        self.map_canvas.bind("<Configure>", self.draw_map)
        self.map_canvas.bind("<Motion>", self.on_map_motion)
        self.map_canvas.bind("<Leave>", self.hide_map_tooltip)
        self.map_canvas.bind("<Button-1>", self.on_map_click)

        self.map_legend = tk.Frame(
            self.clock_page,
            bg=MAP_COLORS["background"],
            bd=0,
        )
        self.map_legend.grid(row=7, column=0, sticky="ew", pady=(8, 0))
        self.map_legend.grid_columnconfigure(1, weight=1)
        for column, region in enumerate(("Americas", "Europe", "Asia")):
            marker = tk.Label(
                self.map_legend,
                text="●",
                fg=MAP_COLORS[region],
                bg=MAP_COLORS["background"],
                bd=0,
                font=("Segoe UI", 15),
            )
            marker.grid(row=0, column=column * 2, padx=(0, 5))
            label = tk.Label(
                self.map_legend,
                text=region,
                fg="#E6EDF3",
                bg=MAP_COLORS["background"],
                bd=0,
                font=("Segoe UI", 11),
            )
            label.grid(row=0, column=column * 2 + 1, sticky="w", padx=(0, 20))
        self.map_help = tk.Label(
            self.map_legend,
            text="Hover for details · Click a dot to show that time",
            fg="#8B949E",
            bg=MAP_COLORS["background"],
            bd=0,
            font=("Segoe UI", 10),
        )
        self.map_help.grid(row=0, column=6, sticky="e")
        self.create_map_tooltip()
        self.draw_map()

        self.settings_page = self.create_frame(self.content)
        self.settings_page.grid_columnconfigure(0, weight=1)
        self.settings_back_button = self.create_button(
            self.settings_page,
            "←  Back to clock",
            lambda: self.show_page("clock"),
            font=("Segoe UI", 9),
            padx=10,
            pady=7,
        )
        self.settings_back_button.pack(anchor="w")
        self.settings_heading = self.create_label(
            self.settings_page,
            "Settings",
            font=("Segoe UI", 22, "bold"),
        )
        self.settings_heading.pack(anchor="w", pady=(22, 4))
        self.settings_description = self.create_label(
            self.settings_page,
            "Personalize your world clock.",
            foreground="muted",
            font=("Segoe UI", 10),
        )
        self.settings_description.pack(anchor="w", pady=(0, 16))

        self.appearance_panel = self.create_frame(
            self.settings_page,
            "surface",
            padx=16,
            pady=14,
            highlightthickness=1,
        )
        self.appearance_panel.pack(fill="x")
        self.appearance_panel.grid_columnconfigure(0, weight=1)
        self.appearance_title = self.create_label(
            self.appearance_panel,
            "Appearance",
            background="surface",
            font=("Segoe UI", 11, "bold"),
        )
        self.appearance_title.grid(row=0, column=0, sticky="w")
        self.appearance_description = self.create_label(
            self.appearance_panel,
            "Your selection is saved on this PC.",
            foreground="muted",
            background="surface",
            font=("Segoe UI", 9),
        )
        self.appearance_description.grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.theme_buttons: dict[str, tk.Button] = {}
        for column, (theme, label) in enumerate((("dark", "Dark"), ("light", "Light"))):
            button = self.create_button(
                self.appearance_panel,
                label,
                lambda selected=theme: self.set_theme(selected),
                role=theme,
                font=("Segoe UI", 9, "bold"),
                padx=16,
                pady=7,
            )
            button.grid(row=0, column=column + 1, rowspan=2, padx=(8, 0))
            self.theme_buttons[theme] = button

        self.time_format_panel = self.create_frame(
            self.settings_page,
            "surface",
            padx=16,
            pady=14,
            highlightthickness=1,
        )
        self.time_format_panel.pack(fill="x", pady=(12, 0))
        self.time_format_panel.grid_columnconfigure(0, weight=1)
        self.time_format_title = self.create_label(
            self.time_format_panel,
            "Time format",
            background="surface",
            font=("Segoe UI", 11, "bold"),
        )
        self.time_format_title.grid(row=0, column=0, sticky="w")
        self.time_format_description = self.create_label(
            self.time_format_panel,
            "Choose 12-hour or 24-hour time.",
            foreground="muted",
            background="surface",
            font=("Segoe UI", 9),
        )
        self.time_format_description.grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.time_format_buttons: dict[str, tk.Button] = {}
        for column, (clock_format, label) in enumerate(
            (("12h", "12-hour"), ("24h", "24-hour"))
        ):
            button = self.create_button(
                self.time_format_panel,
                label,
                lambda selected=clock_format: self.set_time_format(selected),
                role=clock_format,
                font=("Segoe UI", 9, "bold"),
                padx=14,
                pady=7,
            )
            button.grid(row=0, column=column + 1, rowspan=2, padx=(8, 0))
            self.time_format_buttons[clock_format] = button

        self.location_panel = self.create_frame(
            self.settings_page,
            "surface",
            padx=16,
            pady=14,
            highlightthickness=1,
        )
        self.location_panel.pack(fill="x", pady=(12, 0))
        self.location_panel.grid_columnconfigure(0, weight=1)
        self.location_title = self.create_label(
            self.location_panel,
            "Clock location",
            background="surface",
            font=("Segoe UI", 11, "bold"),
        )
        self.location_title.grid(row=0, column=0, sticky="w")
        self.location_description = self.create_label(
            self.location_panel,
            "Choose from all supported world clock cities.",
            foreground="muted",
            background="surface",
            font=("Segoe UI", 9),
        )
        self.location_description.grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.location_variable = tk.StringVar(
            self.window,
            self.selected_location.name if self.selected_location else "Local time",
        )
        self.location_selector = ttk.Combobox(
            self.location_panel,
            textvariable=self.location_variable,
            values=("Local time", *(location.name for location in LOCATIONS)),
            state="readonly",
            style="WorldClock.TCombobox",
            width=26,
        )
        self.location_selector.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e",
            padx=(12, 0),
        )
        self.location_selector.bind("<<ComboboxSelected>>", self.on_location_selected)

        self.settings_status_label = self.create_label(
            self.settings_page,
            "Theme preference is saved on this PC.",
            foreground="muted",
            font=("Segoe UI", 9),
        )
        self.settings_status_label.pack(anchor="w", pady=(12, 0))
        if self.settings_warning:
            self.settings_status_label.configure(
                text=self.settings_warning,
                fg=THEMES[self.current_theme]["error"],
            )

    def map_coordinates(self, longitude: float, latitude: float) -> tuple[float, float]:
        return project_map_coordinates(
            longitude,
            latitude,
            max(self.map_canvas.winfo_width(), 1),
            max(self.map_canvas.winfo_height(), 1),
        )

    def draw_map(self, _event: tk.Event | None = None) -> None:
        if not hasattr(self, "map_canvas"):
            return
        canvas = self.map_canvas
        canvas.delete("all")
        self.map_markers.clear()
        canvas.configure(
            bg=MAP_COLORS["background"],
            highlightbackground=THEMES[self.current_theme]["border"],
        )

        for latitude in (-30, 0, 30, 60):
            _, y = self.map_coordinates(0, latitude)
            canvas.create_line(
                0, y, canvas.winfo_width(), y,
                fill=MAP_COLORS["grid"],
                width=1,
            )
        for longitude in (-120, -60, 0, 60, 120):
            x, _ = self.map_coordinates(longitude, 0)
            canvas.create_line(
                x, 0, x, canvas.winfo_height(),
                fill=MAP_COLORS["grid"],
                width=1,
            )

        for outline in self.land_polygons:
            points = [
                coordinate
                for longitude, latitude in outline
                for coordinate in self.map_coordinates(longitude, latitude)
            ]
            canvas.create_polygon(
                *points,
                fill=MAP_COLORS["land"],
                outline=MAP_COLORS["coast"],
                width=1,
            )

        for location in self.visible_map_locations():
            x, y = self.map_coordinates(location.longitude, location.latitude)
            selected = location == self.selected_location
            radius = 5 if selected or location == self.local_location else 4
            marker = canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=MAP_COLORS[location.region],
                outline="",
                width=0,
            )
            self.map_markers[marker] = location
            if location == self.highlighted_location:
                phase = self.highlight_step % 6
                radius = 7 + (phase if phase <= 3 else 6 - phase) * 2
                canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    outline=THEMES[self.current_theme]["accent"],
                    width=2,
                    tags=("search-highlight",),
                )

    def on_location_search_key_release(self, event: tk.Event) -> None:
        if event.keysym in ("Return", "Up", "Down", "Escape", "Tab"):
            return
        query = self.location_search_variable.get()
        matches = find_location_search_matches(query)
        self.location_search.configure(values=matches)
        if query.strip() and not matches:
            self.set_search_status("No supported country or city matches.", error=True)
        else:
            self.set_search_status("")

    def on_location_search_selected(self, _event: tk.Event | None = None) -> None:
        self.submit_location_search()

    def submit_location_search(
        self,
        _event: tk.Event | None = None,
    ) -> str | None:
        query = self.location_search_variable.get().strip()
        matches = find_location_search_matches(query)
        location = resolve_location_search(query)
        if location is None and len(matches) == 1:
            location = resolve_location_search(matches[0])
        if location is None:
            message = (
                "Choose a country or city from the suggestions."
                if matches
                else "No supported country or city matches."
            )
            self.set_search_status(message, error=not matches)
            return "break"

        self.set_location(location)
        self.highlight_location(location)
        offset = format_utc_offset(self.location_datetime(location.timezone))
        if query.casefold() == location.country.casefold():
            description = f"{location.country} → {location.name}"
        else:
            description = f"{location.name}, {location.country}"
        self.set_search_status(
            f"{description} · {location.timezone} · {offset}"
        )
        return "break" if _event is not None else None

    def set_search_status(self, message: str, *, error: bool = False) -> None:
        self.search_status_error = error
        self.map_search_status.configure(
            text=message,
            fg=THEMES[self.current_theme]["error" if error else "muted"],
        )

    def highlight_location(self, location: ClockLocation) -> None:
        if self.highlight_after_id is not None:
            self.window.after_cancel(self.highlight_after_id)
        self.highlighted_location = location
        self.highlight_step = 0
        self.draw_map()
        self.highlight_after_id = self.window.after(
            120,
            self.animate_location_highlight,
        )

    def animate_location_highlight(self) -> None:
        self.highlight_after_id = None
        if self.highlighted_location is None:
            return
        self.highlight_step += 1
        if self.highlight_step >= 12:
            self.clear_location_highlight()
            return
        self.draw_map()
        self.highlight_after_id = self.window.after(
            120,
            self.animate_location_highlight,
        )

    def clear_location_highlight(self) -> None:
        if self.highlight_after_id is not None:
            self.window.after_cancel(self.highlight_after_id)
        self.highlight_after_id = None
        self.highlighted_location = None
        self.draw_map()

    def create_map_tooltip(self) -> None:
        self.map_tooltip = tk.Toplevel(self.window)
        self.map_tooltip.withdraw()
        self.map_tooltip.overrideredirect(True)
        self.map_tooltip.configure(bg=MAP_COLORS["coast"])
        self.map_tooltip_label = tk.Label(
            self.map_tooltip,
            justify="left",
            bg=MAP_COLORS["background"],
            fg=THEMES[self.current_theme]["text"],
            font=("Segoe UI", 8),
            padx=7,
            pady=5,
            bd=0,
        )
        self.map_tooltip_label.pack(padx=1, pady=1)
        self.tooltip_position = (0, 0)

    def location_at(self, x: int, y: int) -> ClockLocation | None:
        closest_location = None
        closest_distance = 16
        for location in self.visible_map_locations():
            marker_x, marker_y = self.map_coordinates(
                location.longitude,
                location.latitude,
            )
            distance = ((marker_x - x) ** 2 + (marker_y - y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_location = location
                closest_distance = distance
        return closest_location

    def visible_map_locations(self) -> tuple[ClockLocation, ...]:
        locations = list(MAP_LOCATIONS)
        for location in (self.local_location, self.selected_location):
            if location is not None and location not in locations:
                locations.append(location)
        return tuple(locations)

    @staticmethod
    def format_time(value: datetime, time_format: str) -> str:
        if time_format == "12h":
            return value.strftime("%I:%M:%S %p").lstrip("0")
        return value.strftime("%H:%M:%S")

    def location_datetime(self, timezone_name: str | None = None) -> datetime:
        zone = timezone_name or (
            self.selected_location.timezone if self.selected_location else "local"
        )
        if zone == "local":
            return datetime.now().astimezone()
        return datetime.now(ZoneInfo(zone))

    def on_map_motion(self, event: tk.Event) -> None:
        location = self.location_at(event.x, event.y)
        if location is None:
            self.hide_map_tooltip()
            return
        self.hovered_location = location
        self.tooltip_position = (event.x_root + 14, event.y_root + 14)
        self.update_map_tooltip()

    def update_map_tooltip(self) -> None:
        if self.hovered_location is None:
            return
        location = self.hovered_location
        local_time = self.location_datetime(location.timezone)
        offset = local_time.strftime("%z")
        if offset:
            offset = f"UTC{offset[:3]}:{offset[3:]}"
        is_local = location == self.local_location
        if is_local:
            local_time = datetime.now().astimezone()
            local_zone = local_time.tzname() or location.timezone
            location_description = f"Your country · {location.country}"
            timezone_description = local_zone
        else:
            location_description = f"{location.name}, {location.country}"
            timezone_description = f"{location.timezone} · {offset}"
        self.map_tooltip_label.configure(
            text=(
                f"{location_description}\n"
                f"{timezone_description}\n"
                f"{self.format_time(local_time, self.time_format)}"
            ),
            fg=THEMES[self.current_theme]["text"],
        )
        self.map_tooltip.update_idletasks()
        x, y = self.tooltip_position
        x = min(x, self.window.winfo_screenwidth() - self.map_tooltip.winfo_width() - 8)
        y = min(y, self.window.winfo_screenheight() - self.map_tooltip.winfo_height() - 8)
        self.map_tooltip.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.map_tooltip.deiconify()
        self.map_tooltip.lift()

    def hide_map_tooltip(self, _event: tk.Event | None = None) -> None:
        self.hovered_location = None
        if hasattr(self, "map_tooltip"):
            self.map_tooltip.withdraw()

    def on_map_click(self, event: tk.Event) -> None:
        location = self.location_at(event.x, event.y)
        if location is not None:
            self.set_location(None if location == self.local_location else location)

    def save_preferences(self) -> None:
        preferences = {
            "theme": self.current_theme,
            "time_format": self.time_format,
            "location": (
                self.selected_location.name if self.selected_location else "local"
            ),
        }
        try:
            self.theme_settings_path.parent.mkdir(parents=True, exist_ok=True)
            self.theme_settings_path.write_text(
                json.dumps(preferences, indent=2),
                encoding="utf-8",
            )
        except OSError as error:
            self.settings_status_label.configure(
                text=f"Settings changed, but could not be saved: {error}",
                fg=THEMES[self.current_theme]["error"],
            )
        else:
            self.settings_status_label.configure(
                text="Settings are saved on this PC.",
                fg=THEMES[self.current_theme]["muted"],
            )

    def apply_theme(self) -> None:
        colors = THEMES[self.current_theme]
        self.window.configure(bg=colors["background"])
        for frame, role in self.themed_frames:
            frame.configure(
                bg=colors[role],
                highlightbackground=colors["border"],
            )
        for label, foreground, background in self.themed_labels:
            label.configure(fg=colors[foreground], bg=colors[background])
        for button, role in self.themed_buttons:
            selected = (
                role == self.current_theme
                or role == self.time_format
                or (role == "local" and self.selected_location is None)
            )
            background = colors["accent"] if selected else colors["surface_alt"]
            button.configure(
                bg=background,
                fg=colors["accent_text"] if selected else colors["text"],
                activebackground=colors["accent"] if selected else colors["surface"],
                activeforeground=colors["accent_text"] if selected else colors["text"],
            )
        self.appearance_panel.configure(highlightbackground=colors["border"])
        self.time_format_panel.configure(highlightbackground=colors["border"])
        self.location_panel.configure(highlightbackground=colors["border"])
        self.location_style.configure(
            "WorldClock.TCombobox",
            fieldbackground=colors["surface_alt"],
            background=colors["surface_alt"],
            foreground=colors["text"],
            arrowcolor=colors["text"],
            bordercolor=colors["border"],
            lightcolor=colors["border"],
            darkcolor=colors["border"],
            padding=6,
        )
        self.map_search_status.configure(
            fg=colors["error" if self.search_status_error else "muted"]
        )
        self.location_style.map(
            "WorldClock.TCombobox",
            fieldbackground=[("readonly", colors["surface_alt"])],
            foreground=[("readonly", colors["text"])],
        )
        self.map_canvas.configure(highlightbackground=colors["border"])
        self.map_tooltip_label.configure(fg=colors["text"])
        self.draw_map()
        if sys.platform == "win32":
            dark_mode = ctypes.c_int(self.current_theme == "dark")
            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode),
            )

    def set_theme(self, theme: str) -> None:
        if theme not in THEMES:
            raise ValueError(f"Unsupported theme: {theme}")
        self.current_theme = theme
        self.apply_theme()
        self.save_preferences()

    def set_time_format(self, time_format: str) -> None:
        if time_format not in ("12h", "24h"):
            raise ValueError(f"Unsupported time format: {time_format}")
        self.time_format = time_format
        self.apply_theme()
        self.update_clock()
        self.save_preferences()

    def set_timezone(self, timezone_name: str) -> None:
        if timezone_name == "local":
            self.set_location(None)
            return
        location = LOCATION_BY_TIMEZONE.get(timezone_name)
        if location is None:
            raise ValueError(f"Unsupported timezone: {timezone_name}")
        self.set_location(location)

    def set_location(self, location: ClockLocation | None) -> None:
        if location is not None and location not in LOCATIONS:
            raise ValueError(f"Unsupported clock location: {location.name}")
        self.selected_location = location
        if hasattr(self, "location_variable"):
            self.location_variable.set(location.name if location else "Local time")
        self.apply_theme()
        self.update_clock()
        self.save_preferences()

    def on_location_selected(self, _event: tk.Event | None = None) -> None:
        selected_name = self.location_variable.get()
        if selected_name == "Local time":
            self.set_location(None)
            return
        location = LOCATION_BY_NAME.get(selected_name)
        if location is None:
            raise ValueError(f"Unsupported clock location: {selected_name}")
        self.set_location(location)

    def show_page(self, page: str) -> None:
        if page not in ("clock", "settings"):
            raise ValueError(f"Unknown page: {page}")
        self.clock_page.pack_forget()
        self.settings_page.pack_forget()
        if page == "clock":
            self.clock_page.pack(fill="both", expand=True, pady=(18, 0))
        else:
            self.settings_page.pack(fill="both", expand=True, pady=(18, 0))
        self.active_page = page
        self.apply_theme()

    def update_clock(self) -> None:
        now = self.location_datetime()
        self.clock_label.configure(text=self.format_time(now, self.time_format))
        self.date_label.configure(text=now.strftime("%A, %B %d, %Y"))
        if self.selected_location is None:
            location_name = (
                f"LOCAL TIME · {now.tzname() or 'LOCAL'} · {format_utc_offset(now)}"
            )
        else:
            location_name = (
                f"{self.selected_location.name}, {self.selected_location.country} · "
                f"{self.selected_location.timezone} · {format_utc_offset(now)}"
            )
        self.clock_timezone.configure(text=location_name)
        self.local_time_button.configure(
            text="Local",
            relief="sunken" if self.selected_location is None else "flat",
        )
        if self.hovered_location is not None:
            self.update_map_tooltip()
        milliseconds_to_next_second = (
            1_000_000 - now.microsecond + 999
        ) // 1_000
        self.window.after(max(1, milliseconds_to_next_second), self.update_clock)

    def close(self) -> None:
        if self.highlight_after_id is not None:
            self.window.after_cancel(self.highlight_after_id)
        if sys.platform == "win32":
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.DestroyIcon.argtypes = [ctypes.c_void_p]
            for handle in self.icon_handles:
                user32.DestroyIcon(handle)
        self.window.destroy()


def main() -> None:
    set_app_identity()
    root = tk.Tk()
    DigitalClock(root)
    root.mainloop()
