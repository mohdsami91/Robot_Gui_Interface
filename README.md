# Glowing Buttons GUI Interface

This project is a Python-based GUI application using PySide6 that showcases advanced button customization and animations. The button styles, including colors, animations, and effects are configured through a `button_themes.json` file.

## Features

- Customizable button animations
- Gradient color themes
- Hover and click effects
- Shadow effects
- JSON-based theme configuration
- Built-in icon support
- Animation timing and easing curves

## Requirements

- Python 3.12 or later
- PySide6 and its components
- iconify

## Setup and Installation

### 1. Create a Virtual Environment

It is recommended to use a virtual environment to manage project dependencies:

```bash
python -m venv myenv
```

### 2. Activate the Environment

**On Windows:**
```powershell
.\myenv\Scripts\activate
```

**On macOS/Linux:**
```bash
source myenv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages with their exact versions:

```bash
pip install iconify==0.0.103
pip install PySide6==6.10.0
```

Note: Installing PySide6 will automatically install the required components:
- PySide6_Addons==6.10.0
- PySide6_Essentials==6.10.0

## Running the Application

Once the setup is complete, you can run the main application:

```bash
python main.py
```

## Button Customization

You can customize buttons using the `button_themes.json` file. The following properties are supported:

- `name`: The name of the button
- `theme`: Theme number (1 to 13)
- `customTheme`: Custom theme colors (color1 and color2)
- `animateOn`: Animation trigger event (hover or click)
- `animation`: Part of button to animate (border, background, or both)
- `animationDuration`: Animation duration in milliseconds
- `animationEasingCurve`: Animation easing curve
- `fallBackStyle`: Style applied after animation
- `defaultStyle`: Base style applied with animation
- `shadow`: Button shadow effects configuration

## Example Button Theme Configuration

```json
{
    "name": "pushButton",
    "customTheme": [
        {
            "color1": "#2596be",
            "color2": "rgb(37, 150, 190)"
        }
    ],
    "animateOn": "hover",
    "animation": "both",
    "animationDuration": 500,
    "shadow": [
        {
            "color": "white",
            "applyShadowOn": "hover",
            "animateShadow": true,
            "blurRadius": 100,
            "xOffset": 0,
            "yOffset": 0
        }
    ]
}
```

## Directory Structure

```
glowing_buttons/
├── main.py              # Main application entry point
├── custom_buttons.py    # Custom button implementations
├── ui_interface.py      # UI layout and components
├── button_themes.json   # Button theme configurations
└── README.md           # This documentation
```

## Troubleshooting

If you encounter any issues:

1. Make sure you're using Python 3.12 or later
2. Verify that PySide6 is installed correctly
3. Check that the button_themes.json file exists and is properly formatted
4. Ensure all paths in import statements are correct

## License

This project is open-source and available under the MIT License.
