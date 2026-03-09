# PythonEXEBuilder

> **Developed By SANTHOSH A**  
> Convert any Python script into a standalone Windows `.exe` – no Python required on the end-user machine.

---

## 📁 Project Structure

```
PythonEXEBuilder/
│
├── input/               ← Drop your Python file here
│   └── app.py           ← Sample demo application
│
├── assets/              ← Optional bundled assets
│   ├── images/          ← .png / .jpg / .bmp / .gif / .svg / .webp
│   ├── icons/           ← .ico / .png (first .ico found is used for exe)
│   └── html/            ← .html / .css / .js files
│
├── output/              ← Final .exe appears here after build
│
├── logs/                ← Timestamped build logs
│
├── builder.py           ← Core build engine
├── build.bat            ← One-click build automation (Windows)
└── README.md            ← You are here
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Details |
|-------------|---------|
| Python | 3.7 or higher ([python.org](https://python.org)) |
| pip | Included with Python |
| Windows | Recommended for building `.exe` files |

> PyInstaller is **auto-installed** by the build tool if not present.

### Steps

1. **Place your Python file** inside the `input/` folder  
   _(rename it to anything, e.g. `myapp.py`)_

2. **Add assets** (optional) to the `assets/` folder  
   _(images, icons, HTML/CSS/JS, JSON, config files — all auto-detected)_

3. **Double-click `build.bat`** — that's it!

4. **Collect your `.exe`** from the `output/` folder

---

## ⚙️ How It Works

```
build.bat
   │
   └─▶ builder.py
         │
         ├─ [1] Environment Check    – Python version, PyInstaller availability
         ├─ [2] Input Validation     – Finds .py file, syntax check, MD5 hash
         ├─ [3] Dependency Analysis  – Parses imports, adds hidden imports
         ├─ [4] Asset Collection     – Bundles images, configs, HTML/CSS/JS
         ├─ [5] Icon Detection       – Finds .ico or auto-generates one
         ├─ [6] Spec Generation      – Creates PyInstaller .spec file
         │       └─▶ PyInstaller compile
         └─ [7] Output               – Copies .exe to output/, cleans temp
```

---

## ✅ Supported Features

| Feature | Support |
|---------|---------|
| Internet / API calls (`requests`, `httpx`) | ✔ Full |
| File read / write | ✔ Full |
| Images & media | ✔ Auto-bundled |
| Tkinter UI | ✔ Full |
| CustomTkinter | ✔ Full |
| PyQt5 / PyQt6 / PySide6 | ✔ Full |
| wxPython | ✔ Full |
| Flask local web UI | ✔ Full |
| Drag & drop (`tkinterdnd2`) | ✔ Full |
| Dark / light / custom themes | ✔ Preserved |
| Local JSON / SQLite storage | ✔ Full |
| HTML / CSS / JS assets | ✔ Auto-bundled |
| Custom `.ico` icon | ✔ Auto-detected |
| UPX compression | ✔ Enabled |

---

## 📦 Asset Auto-Detection

Place any of the following in `assets/` and they will be bundled automatically:

| Category | Extensions |
|----------|-----------|
| Images | `.png .jpg .jpeg .gif .bmp .ico .svg .webp .tiff` |
| Config | `.ini .cfg .toml .yaml .yml .env` |
| Web | `.html .htm .css .js .ts` |
| Data | `.json .csv .xml .db .sqlite .sqlite3` |
| Fonts | `.ttf .otf .woff .woff2` |
| Misc | `.txt .md .pdf` |

---

## 🔧 Advanced Usage

### Running the builder directly

```bash
python builder.py
```

### Build logs

Every build generates a timestamped log in `logs/`:

```
logs/
└── build_20240315_143022.log
```

### Custom icon

Place any `.ico` file inside `assets/icons/` and it will be used automatically.

---

## ❌ Error Reference

| Error | Solution |
|-------|---------|
| `No .py file found in input/` | Add your Python script to the `input/` folder |
| `Syntax error at line N` | Fix the error in your script and rebuild |
| `PyInstaller failed` | Check `logs/` for detailed output |
| `Python is not installed` | Install Python from [python.org](https://python.org) and add to PATH |
| Module not found at runtime | Add it to `hiddenimports` in `builder.py` |

---

## 📝 Sample Demo App

The included `input/app.py` demonstrates:

- **Dark-mode Tkinter UI** with custom colors
- **Local storage** via JSON (auto-saved notes)
- **File browser & drag-and-drop** support
- **Internet API fetch** using `requests`
- **Multi-tab notebook** layout

Build it immediately with `build.bat` to see a working example.

---

## 📋 Notes

- The `.exe` file is **self-contained** — no Python needed on the target machine
- UPX compression is enabled by default to reduce file size
- The `output/` folder opens automatically after a successful build
- Replace `input/app.py` with any other `.py` file and rebuild anytime

---

## 👤 Developer

**Developed By SANTHOSH A**  
PythonEXEBuilder v1.0.0
