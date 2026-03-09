"""
╔══════════════════════════════════════════════════════════════════╗
║           PythonEXEBuilder - Desktop Build Tool                  ║
║                  Developed By SANTHOSH A                         ║
╚══════════════════════════════════════════════════════════════════╝

Converts a Python (.py) file into a standalone Windows executable (.exe)
with full support for UI frameworks, assets, internet access, drag-and-drop,
local storage, and custom themes.
"""

import os
import sys
import ast
import time
import shutil
import hashlib
import logging
import platform
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
#  Constants & Paths
# ─────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.resolve()
INPUT_DIR   = BASE_DIR / "input"
OUTPUT_DIR  = BASE_DIR / "output"
ASSETS_DIR  = BASE_DIR / "assets"
LOGS_DIR    = BASE_DIR / "logs"
WORK_DIR    = BASE_DIR / ".build_tmp"

DEVELOPER   = "SANTHOSH A"
VERSION     = "1.0.0"

ASSET_EXTS  = {
    "image":  {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp", ".tiff"},
    "config": {".ini", ".cfg", ".toml", ".yaml", ".yml", ".env"},
    "web":    {".html", ".htm", ".css", ".js", ".ts"},
    "data":   {".json", ".csv", ".xml", ".db", ".sqlite", ".sqlite3"},
    "font":   {".ttf", ".otf", ".woff", ".woff2"},
    "misc":   {".txt", ".md", ".pdf"},
}

# ─────────────────────────────────────────────
#  Logging Setup
# ─────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOGS_DIR / f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("EXEBuilder")


# ══════════════════════════════════════════════
#  ANSI colour helpers (Windows-safe via colorama)
# ══════════════════════════════════════════════
try:
    from colorama import init as _cinit, Fore, Style
    _cinit(autoreset=True)
    def _c(color, text): return f"{color}{text}{Style.RESET_ALL}"
except ImportError:
    def _c(_, text): return text

def banner():
    lines = [
        "╔══════════════════════════════════════════════════════════════════╗",
        "║           PythonEXEBuilder  v{}                             ║".format(VERSION),
        "║                  Developed By SANTHOSH A                        ║",
        "║          Python → Windows .exe  Packaging Tool                  ║",
        "╚══════════════════════════════════════════════════════════════════╝",
    ]
    print(_c(Fore.CYAN if 'Fore' in dir() else "", "\n".join(lines)))
    print()

def step(n, total, msg):
    bar = "█" * n + "░" * (total - n)
    print(_c(Fore.GREEN if 'Fore' in dir() else "", f"  [{bar}] Step {n}/{total}  {msg}"))

def info(msg):  log.info(_c(Fore.WHITE  if 'Fore' in dir() else "", msg))
def ok(msg):    log.info(_c(Fore.GREEN  if 'Fore' in dir() else "", f"✔  {msg}"))
def warn(msg):  log.warning(_c(Fore.YELLOW if 'Fore' in dir() else "", f"⚠  {msg}"))
def err(msg):   log.error(_c(Fore.RED   if 'Fore' in dir() else "", f"✘  {msg}"))
def head(msg):  print(_c(Fore.CYAN    if 'Fore' in dir() else "", f"\n{'─'*60}\n  {msg}\n{'─'*60}"))


# ══════════════════════════════════════════════
#  1. Environment Checks
# ══════════════════════════════════════════════
class EnvironmentChecker:
    """Verify Python version, OS, and required tools."""

    def run(self):
        head("Environment Check")
        self._check_python()
        self._check_os()
        pkg = self._check_pyinstaller()
        return pkg

    def _check_python(self):
        v = sys.version_info
        if v < (3, 7):
            err(f"Python 3.7+ required. Found: {v.major}.{v.minor}")
            sys.exit(1)
        ok(f"Python {v.major}.{v.minor}.{v.micro}")

    def _check_os(self):
        os_name = platform.system()
        ok(f"Operating System: {os_name} {platform.release()}")
        if os_name != "Windows":
            warn("Not running on Windows. The .exe will be created but may only run on Windows.")

    def _check_pyinstaller(self):
        """Install PyInstaller if missing, return package name."""
        try:
            import PyInstaller
            ok(f"PyInstaller {PyInstaller.__version__} found")
            return "pyinstaller"
        except ImportError:
            warn("PyInstaller not found – attempting auto-install …")
            ret = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"],
                capture_output=True, text=True
            )
            if ret.returncode != 0:
                err("Failed to install PyInstaller.\n" + ret.stderr)
                sys.exit(1)
            ok("PyInstaller installed successfully")
            return "pyinstaller"


# ══════════════════════════════════════════════
#  2. Input Validator
# ══════════════════════════════════════════════
class InputValidator:
    """Find & validate the Python source file."""

    def find_script(self) -> Path:
        head("Locating Python Source File")
        INPUT_DIR.mkdir(parents=True, exist_ok=True)

        py_files = sorted(INPUT_DIR.glob("*.py"))
        if not py_files:
            err(f"No .py file found in '{INPUT_DIR}'")
            err("Please place your Python script inside the 'input/' folder and run again.")
            sys.exit(1)

        if len(py_files) > 1:
            warn(f"Multiple .py files found. Using: {py_files[0].name}")
            info("  Files detected: " + ", ".join(f.name for f in py_files))

        script = py_files[0]
        ok(f"Source file: {script.name}  ({script.stat().st_size:,} bytes)")
        return script

    def validate_syntax(self, script: Path):
        head("Syntax Validation")
        source = script.read_text(encoding="utf-8", errors="replace")
        try:
            ast.parse(source)
            ok("Syntax check passed")
        except SyntaxError as e:
            err(f"Syntax error in {script.name} at line {e.lineno}: {e.msg}")
            sys.exit(1)

    def check_file_hash(self, script: Path) -> str:
        h = hashlib.md5(script.read_bytes()).hexdigest()
        info(f"Source MD5: {h}")
        return h


# ══════════════════════════════════════════════
#  3. Dependency Analyser
# ══════════════════════════════════════════════
class DependencyAnalyser:
    """
    Parse imports from the Python source and detect:
      - UI frameworks → special PyInstaller hooks
      - Hidden imports that PyInstaller often misses
    """

    # Known hidden imports per detected module
    HIDDEN_IMPORT_MAP = {
        "customtkinter":  ["customtkinter"],
        "tkinter":        ["tkinter", "tkinter.ttk", "tkinter.messagebox", "tkinter.filedialog"],
        "PyQt5":          ["PyQt5", "PyQt5.sip"],
        "PyQt6":          ["PyQt6"],
        "PySide6":        ["PySide6"],
        "wx":             ["wx"],
        "kivy":           ["kivy"],
        "flask":          ["flask", "jinja2", "werkzeug"],
        "django":         ["django"],
        "requests":       ["requests", "urllib3", "certifi", "charset_normalizer", "idna"],
        "PIL":            ["PIL"],
        "Pillow":         ["PIL"],
        "numpy":          ["numpy"],
        "pandas":         ["pandas"],
        "matplotlib":     ["matplotlib"],
        "cv2":            ["cv2"],
        "selenium":       ["selenium"],
        "playwright":     ["playwright"],
        "sqlalchemy":     ["sqlalchemy"],
        "cryptography":   ["cryptography"],
        "pydantic":       ["pydantic"],
        "fastapi":        ["fastapi", "uvicorn"],
    }

    FRAMEWORK_HOOKS = {
        "PyQt5":  "--windowed",
        "PyQt6":  "--windowed",
        "PySide6":"--windowed",
        "wx":     "--windowed",
        "kivy":   "--windowed",
    }

    def analyse(self, script: Path):
        head("Dependency Analysis")
        source = script.read_text(encoding="utf-8", errors="replace")
        tree   = ast.parse(source)

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        ok(f"Detected {len(imports)} imported modules")

        hidden = []
        for mod, hiddens in self.HIDDEN_IMPORT_MAP.items():
            if mod in imports:
                info(f"  ↳ {mod} → adding hidden imports: {hiddens}")
                hidden.extend(hiddens)

        windowed = False
        for mod, flag in self.FRAMEWORK_HOOKS.items():
            if mod in imports:
                windowed = True
                info(f"  ↳ GUI framework detected: {mod} → {flag}")

        # Tkinter / customtkinter are windowed by default only if no console usage found
        if "tkinter" in imports or "customtkinter" in imports:
            if "print(" not in source:
                windowed = True

        self._install_missing(imports)
        return list(set(hidden)), windowed, imports

    def _install_missing(self, imports: set):
        """Best-effort pip install for detected third-party packages."""
        stdlib = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
        third_party = [m for m in imports if m not in stdlib and not m.startswith("_")]

        for pkg in third_party:
            if importlib.util.find_spec(pkg) is None:
                warn(f"  '{pkg}' not installed – attempting pip install …")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                    capture_output=True
                )


# ══════════════════════════════════════════════
#  4. Asset Collector
# ══════════════════════════════════════════════
class AssetCollector:
    """Collect and map all assets to be bundled."""

    def collect(self, script: Path) -> list[tuple[str, str]]:
        head("Asset Collection")
        datas = []

        # 1. assets/ folder
        if ASSETS_DIR.exists():
            for f in ASSETS_DIR.rglob("*"):
                if f.is_file() and self._is_asset(f):
                    rel = f.relative_to(BASE_DIR)
                    dest_dir = str(rel.parent)
                    datas.append((str(f), dest_dir))
                    info(f"  + {rel}")

        # 2. Files next to script in input/
        for f in INPUT_DIR.iterdir():
            if f.is_file() and f.suffix != ".py" and self._is_asset(f):
                datas.append((str(f), "."))
                info(f"  + input/{f.name}")

        ok(f"Total assets bundled: {len(datas)}")
        return datas

    def _is_asset(self, f: Path) -> bool:
        ext = f.suffix.lower()
        return any(ext in exts for exts in ASSET_EXTS.values())


# ══════════════════════════════════════════════
#  5. Icon Manager
# ══════════════════════════════════════════════
class IconManager:
    """Find or generate a default icon for the exe."""

    def get_icon(self) -> Path | None:
        # Search assets/icons first
        for loc in [ASSETS_DIR / "icons", ASSETS_DIR, INPUT_DIR]:
            if loc.exists():
                for ext in (".ico", ".png"):
                    matches = list(loc.glob(f"*{ext}"))
                    if matches:
                        ok(f"Icon: {matches[0]}")
                        return matches[0]

        # Try generating a simple default icon using Pillow
        try:
            from PIL import Image, ImageDraw, ImageFont
            ico_path = WORK_DIR / "default_icon.ico"
            img = Image.new("RGBA", (256, 256), (30, 30, 40, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse([20, 20, 236, 236], fill=(0, 150, 255, 255))
            draw.text((85, 90), "EXE", fill="white")
            img.save(str(ico_path), format="ICO")
            ok(f"Default icon generated: {ico_path}")
            return ico_path
        except Exception:
            warn("Could not generate icon – exe will use default Python icon")
            return None


# ══════════════════════════════════════════════
#  6. Spec File Generator
# ══════════════════════════════════════════════
class SpecGenerator:
    """Build a PyInstaller .spec file with all options."""

    def generate(
        self,
        script: Path,
        hidden_imports: list,
        datas: list,
        icon: Path | None,
        windowed: bool,
        app_name: str,
    ) -> Path:
        head("Generating PyInstaller Spec File")

        WORK_DIR.mkdir(parents=True, exist_ok=True)

        # Format datas list
        datas_repr = ",\n        ".join(
            f'("{src.replace(chr(92), "/")}",  "{dst}")'
            for src, dst in datas
        )

        hidden_repr = ",\n        ".join(f'"{h}"' for h in hidden_imports)

        console_flag = "False" if windowed else "True"
        icon_line    = f'icon=r"{icon}",' if icon else ""

        spec_content = f'''\
# -*- mode: python ; coding: utf-8 -*-
# Generated by PythonEXEBuilder  –  Developed By {DEVELOPER}

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    [r"{script}"],
    pathex=[r"{script.parent}", r"{BASE_DIR}"],
    binaries=[],
    datas=[
        {datas_repr}
    ],
    hiddenimports=[
        {hidden_repr}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="{app_name}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_flag},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
    version_info=None,
)
'''
        spec_path = WORK_DIR / f"{app_name}.spec"
        spec_path.write_text(spec_content, encoding="utf-8")
        ok(f"Spec file: {spec_path}")
        return spec_path


# ══════════════════════════════════════════════
#  7. Builder (PyInstaller runner)
# ══════════════════════════════════════════════
class Builder:
    """Run PyInstaller and monitor output."""

    def build(self, spec_path: Path, app_name: str) -> Path:
        head("Building Executable")
        dist_dir = WORK_DIR / "dist"
        build_dir = WORK_DIR / "build"

        cmd = [
            sys.executable, "-m", "PyInstaller",
            str(spec_path),
            "--distpath", str(dist_dir),
            "--workpath", str(build_dir),
            "--noconfirm",
            "--clean",
            "--log-level", "WARN",
        ]

        info(f"Command: {' '.join(cmd)}")
        print()
        print("  Building", end="", flush=True)

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace"
        )

        with open(log_file, "a", encoding="utf-8") as lf:
            dot_timer = time.time()
            for line in proc.stdout:
                lf.write(line)
                # Print a dot every 2 seconds
                if time.time() - dot_timer > 2:
                    print(".", end="", flush=True)
                    dot_timer = time.time()

        proc.wait()
        print()

        if proc.returncode != 0:
            err("PyInstaller failed. Check the build log for details:")
            err(f"  {log_file}")
            sys.exit(1)

        exe_path = dist_dir / f"{app_name}.exe"
        if not exe_path.exists():
            # Some builds output to a subfolder
            candidates = list(dist_dir.rglob("*.exe"))
            if candidates:
                exe_path = candidates[0]
            else:
                err("Build completed but .exe not found in dist/")
                sys.exit(1)

        ok(f"Executable built: {exe_path}  ({exe_path.stat().st_size / 1_048_576:.1f} MB)")
        return exe_path


# ══════════════════════════════════════════════
#  8. Output Manager
# ══════════════════════════════════════════════
class OutputManager:
    """Move final exe to output/ folder and clean temp files."""

    def finalise(self, exe_path: Path, app_name: str) -> Path:
        head("Finalising Output")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        dest = OUTPUT_DIR / exe_path.name
        shutil.copy2(exe_path, dest)
        ok(f"Executable saved to: {dest}")

        # Clean temp build folder
        try:
            shutil.rmtree(WORK_DIR, ignore_errors=True)
            ok("Temporary build files cleaned")
        except Exception as e:
            warn(f"Could not fully clean temp dir: {e}")

        return dest

    def print_summary(self, dest: Path, script: Path, elapsed: float):
        head("Build Summary")
        size_mb = dest.stat().st_size / 1_048_576
        lines = [
            f"  Source script : {script.name}",
            f"  Output file   : {dest}",
            f"  File size     : {size_mb:.2f} MB",
            f"  Build time    : {elapsed:.1f} seconds",
            f"  Developed By  : {DEVELOPER}",
            f"  Log file      : {log_file}",
        ]
        box = "╔" + "═"*62 + "╗"
        print(_c(Fore.CYAN if 'Fore' in dir() else "", box))
        for l in lines:
            pad = " " * (62 - len(l) - 1)
            print(_c(Fore.CYAN if 'Fore' in dir() else "", f"║ {l}{pad}║"))
        print(_c(Fore.CYAN if 'Fore' in dir() else "", "╚" + "═"*62 + "╝"))
        print()
        ok("✅  Build complete!  Double-click the .exe to run your application.")


# ══════════════════════════════════════════════
#  9. Main Orchestrator
# ══════════════════════════════════════════════
def main():
    banner()
    t0 = time.time()
    total_steps = 7

    # Step 1 – Environment
    step(1, total_steps, "Environment Check")
    EnvironmentChecker().run()

    # Step 2 – Find & validate source
    step(2, total_steps, "Locating & Validating Source")
    validator = InputValidator()
    script = validator.find_script()
    validator.validate_syntax(script)
    validator.check_file_hash(script)

    app_name = script.stem  # e.g. "app" from "app.py"

    # Step 3 – Analyse dependencies
    step(3, total_steps, "Analysing Dependencies")
    hidden_imports, windowed, all_imports = DependencyAnalyser().analyse(script)

    # Step 4 – Collect assets
    step(4, total_steps, "Collecting Assets")
    datas = AssetCollector().collect(script)

    # Step 5 – Icon
    step(5, total_steps, "Preparing Icon")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    icon = IconManager().get_icon()

    # Step 6 – Generate spec & build
    step(6, total_steps, "Generating Spec & Building")
    spec = SpecGenerator().generate(script, hidden_imports, datas, icon, windowed, app_name)
    exe  = Builder().build(spec, app_name)

    # Step 7 – Finalise
    step(7, total_steps, "Finalising Output")
    dest = OutputManager().finalise(exe, app_name)
    OutputManager().print_summary(dest, script, time.time() - t0)


if __name__ == "__main__":
    main()
