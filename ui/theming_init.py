from kivy.utils import get_color_from_hex

from kivymd.color_definitions import colors

# This file is imported at the very top of main.py to ensure that the
# KivyMD color definitions are updated before any other KivyMD modules are imported.

# For a 'Light' theme:
# - Main background is 'bg_light', which uses Gray['100']
# - Card/Surface background is 'surface_light', which uses Gray['50']
# - Primary text color is 'text_color', which uses Gray['800']
# - Secondary text color is 'secondary_text_color', which uses Gray['600']

# Override the default Gray palette with high-contrast Solarized values.
# This is the correct way to control background and text colors.

# Light Theme Colors
colors["Gray"]["50"] = "#eee8d5"   # Surface color (cards, dialogs) - BASE2
colors["Gray"]["100"] = "#fdf6e3"  # Main background color - BASE3
colors["Gray"]["200"] = "#93a1a1"  # Hint/Disabled Text - BASE1
colors["Gray"]["400"] = "#586e75"  # Secondary Text - BASE01
colors["Gray"]["600"] = "#073642"  # Primary Text - BASE02
colors["Gray"]["800"] = "#002b36"  # Strongest Text - BASE03

# Dark Theme Colors (for elements like the log window card)
colors["Gray"]["300"] = "#586e75"  # Dark theme secondary text - BASE01
colors["Gray"]["500"] = "#073642"  # Dark theme surface - BASE02
colors["Gray"]["700"] = "#eee8d5"  # Dark theme primary text - BASE2
colors["Gray"]["900"] = "#002b36"  # Dark theme background - BASE03
