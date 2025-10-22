# Robot GUI Interface

This project is a Python-based GUI application using PySide2 that showcases advanced button customization and animations. The button styles, including colors, animations, and icons, are configured through a `button_themes.json` file.

## Setup and Installation

### 1. Create a Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv env
```

### 2. Activate the Environment

**On Windows:**
```powershell
.\env\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source env/bin/activate
```

### 3. Install Dependencies

This project uses `uv` for fast package management. First, install `uv`:

```bash
pip install uv
```

Then, install the required Python packages:

```bash
uv pip install PySide2 iconify
```

### 4. Download Icon Packs

The application uses the `iconify` library to display icons. You need to download the icon packs for the icons to be visible.

To fetch a specific icon pack, such as **Feather**, run the following command:

```bash
iconify-fetch-feather
```

To fetch all available icon packs (including Font Awesome, Material Design, etc.), you can run:

```bash
iconify-fetch
```

The icons will be downloaded to your user directory (e.g., `~/.iconify`).

## Running the Application

Once the setup is complete, you can run the main application:

```bash
python main.py
```
