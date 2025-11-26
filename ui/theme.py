def set_theme(theme_cls):
    """
    Sets the application's theme style and primary/accent palettes.
    The actual colors are controlled by the palette overrides in theming_init.py.
    """
    theme_cls.theme_style = "Light"
    theme_cls.primary_palette = "Green"
    theme_cls.accent_palette = "Blue"
