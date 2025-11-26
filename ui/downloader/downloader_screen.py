from kivymd.app import MDApp
from ..logger import UILogger  # Import UILogger
from .download_worker import DownloadWorker
from datetime import datetime
import os
import threading
import pandas as pd
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    ListProperty,
    BooleanProperty,
    StringProperty,
    ObjectProperty,
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.filemanager import MDFileManager

Builder.load_file(os.path.join(
    os.path.dirname(__file__), 'downloaderscreen.kv'))


class DownloaderScreen(MDScreen):
    """
    UI Controller for the Downloader Screen.
    Manages user input, filtering, and launching the download worker.
    """
    logs = ListProperty([])
    is_resume_mode = BooleanProperty(False)
    master_df = ObjectProperty(None, allownone=True)
    available_symbols = ListProperty([])
    selected_symbols = ListProperty([])
    selected_count_text = StringProperty("Selected: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interval_menu = None
        self.sharding_menu = None
        self.sector_menu = None
        self.index_menu = None
        self.file_manager = None
        self._menus_initialized = False

    def load_master_data(self):
        Clock.schedule_once(self.setup_ui_with_data)

    def on_enter(self, *args):
        """
        Event handler for when the screen is entered.
        This is the correct place to initialize data-dependent UI elements.
        """
        if not self._menus_initialized:
            self.setup_menus()
        # Disable filter controls while data is loading
        self.ids.search_filter.disabled = True
        self.ids.sector_filter.disabled = True
        self.ids.index_filter.disabled = True
        UILogger.add_log_entry(self.logs, "Loading master data...")
        threading.Thread(target=self.load_master_data, daemon=True).start()

    def _on_interval_select(self, text_item):
        """Handles selection of an interval item."""
        self.set_menu_item(self.ids.interval_field,
                           text_item, self.interval_menu)

    def _on_sharding_select(self, text_item):
        """Handles selection of a sharding item."""
        self.set_menu_item(self.ids.sharding_field,
                           text_item, self.sharding_menu)

    def _on_sector_select(self, text_item):
        """Handles selection of a sector item."""
        self.set_menu_item(
            self.ids.sector_filter, text_item, self.sector_menu, self.filter_symbols
        )

    def _on_index_select(self, text_item):
        """Handles selection of an index item."""
        self.set_menu_item(
            self.ids.index_filter, text_item, self.index_menu, self.filter_symbols
        )

    def setup_menus(self):
        """Initializes all MDDropdownMenu instances."""
        # This method is called from on_enter, ensuring `self.ids` is populated.
        interval_menu_items = [
            {
                "text": item,
                "on_release": lambda x=item: self._on_interval_select(x),
            }
            for item in ["minute", "3minute", "5minute", "10minute", "15minute", "30minute", "60minute", "day"]
        ]
        self.interval_menu = MDDropdownMenu(
            caller=self.ids.interval_field, items=interval_menu_items, position="auto", width_mult=4)

        sharding_menu_items = [
            {
                "text": item,
                "on_release": lambda x=item: self._on_sharding_select(x),
            }
            for item in ["None", "By Month", "By Year"]
        ]
        self.sharding_menu = MDDropdownMenu(
            caller=self.ids.sharding_field, items=sharding_menu_items, position="auto", width_mult=4)

        self._menus_initialized = True

    def setup_ui_with_data(self, *args):
        """
        Sets up UI elements that depend on the master data being loaded.
        Called via Clock.schedule_once after load_master_data completes.
        """
        self.ids.search_filter.disabled = False
        self.ids.sector_filter.disabled = False
        self.ids.index_filter.disabled = False

        # Populate sector filter
        unique_sectors = ["All Sectors"] + \
            sorted(self.master_df['Industry'].dropna().unique().tolist())
        sector_menu_items = [{
            "text": item,
            "on_release": lambda x=item: self._on_sector_select(x),
        } for item in unique_sectors]
        self.sector_menu = MDDropdownMenu(
            caller=self.ids.sector_filter,
            items=sector_menu_items,
            position="auto",
            width_mult=4,
        )

        # Populate index filter
        # Assuming 'Indices' column might have multiple indices separated by ','
        all_indices = self.master_df['Indices'].dropna().apply(
            lambda x: [idx.strip() for idx in x.split(',')]).explode().unique().tolist()
        unique_indices = ["All Indices"] + sorted(all_indices)
        index_menu_items = [{
            "text": item,
            "on_release": lambda x=item: self._on_index_select(x),
        } for item in unique_indices]
        self.index_menu = MDDropdownMenu(
            caller=self.ids.index_filter,
            items=index_menu_items,
            position="auto",
            width_mult=4,
        )

        # Populate initial available symbols
        self.available_symbols = self.master_df['Symbol'].tolist()
        self.filter_symbols()
        UILogger.add_log_entry(
            self.logs, "UI elements updated with master data.")

    def set_menu_item(self, field, text, menu, callback=None):
        """Generic method to set a dropdown field's text and dismiss the menu."""
        UILogger.add_log_entry(
            self.logs, f"Selected '{text}' for '{field.id}'")
        field.text = text
        menu.dismiss()
        if callback:
            callback()

    def log_dropdown_press(self, widget_id):
        """Adds a log entry when a dropdown is pressed."""
        UILogger.add_log_entry(self.logs, f"Dropdown '{widget_id}' pressed.")

    def _open_dropdown_menu(self, menu_instance):
        """Opens the dropdown menu, scheduled for the next frame."""
        if menu_instance:
            Clock.schedule_once(lambda dt: menu_instance.open(), 0)

    def filter_symbols(self):
        """Filters the available symbols based on UI controls."""
        if self.master_df is None:
            return

        df = self.master_df.copy()
        search_term = self.ids.search_filter.text.upper()
        sector = self.ids.sector_filter.text
        index = self.ids.index_filter.text

        if search_term:
            df = df[df['Symbol'].str.contains(search_term, na=False)]
        if sector and sector != "All Sectors":
            df = df[df['Industry'] == sector]
        if index and index != "All Indices":
            df = df[df['Indices'].str.contains(index, na=False)]

        self.available_symbols = df['Symbol'].tolist()

    def add_symbol_to_queue(self, symbol):
        """Adds a symbol to the selection queue if not already present."""
        if symbol not in self.selected_symbols:
            self.selected_symbols.append(symbol)
            self.selected_symbols.sort()
            self.update_selected_count()

    def remove_symbol_from_queue(self, symbol):
        """Removes a symbol from the selection queue."""
        if symbol in self.selected_symbols:
            self.selected_symbols.remove(symbol)
            self.update_selected_count()

    def update_selected_count(self):
        self.selected_count_text = f"Selected: {len(self.selected_symbols)}"

    def show_date_picker(self, field):
        """Shows the MDDatePicker and binds its save event."""
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=lambda instance, value,
                         date_range: self.on_date_save(value, field, date_dialog))
        date_dialog.open()

    def on_date_save(self, value, field, dialog):
        """Formats and sets the date text field."""
        field.text = value.strftime('%Y-%m-%d')
        dialog.dismiss()

    def trigger_output_dir_chooser(self):
        """Opens the file manager to select an output directory."""
        self.show_file_manager(self.set_output_dir, select_path=True)

    def trigger_manifest_file_chooser(self):
        """Opens the file manager to select a manifest file."""
        self.show_file_manager(self.set_manifest_file,
                               select_path=False, ext=[".json"])

    def show_file_manager(self, callback, select_path=False, ext=None):
        """Configures and shows the MDFileManager."""
        # ALWAYS create a new instance of the file manager.
        # Reusing an old instance can lead to crashes, especially if it's
        # opened again before it has fully closed.
        self.file_manager = MDFileManager(
            exit_manager=self.close_file_manager,
            select_path=callback,
        )
        if select_path:
            self.file_manager.select_dir = True
            self.file_manager.selector = 'folder'
        else:
            self.file_manager.ext = ext or []

        # Start in user's home directory
        self.file_manager.show(os.path.expanduser("~"))

    def set_output_dir(self, selection):
        """Callback for the output directory file manager."""
        self.ids.output_dir_field.text = selection
        self.close_file_manager()

    def set_manifest_file(self, selection):
        """Callback for the manifest file manager."""
        self.ids.manifest_file_field.text = selection
        self.close_file_manager()

    def close_file_manager(self, *args):
        """Closes the file manager."""
        if self.file_manager:
            self.file_manager.close()
        self.file_manager = None

    def start_download(self):
        """Validates UI parameters and starts the DownloadWorker thread."""
        params = {}
        try:
            params['resume_mode'] = self.is_resume_mode
            if self.is_resume_mode:
                params['manifest_path'] = self.ids.manifest_file_field.text
                if not os.path.exists(params['manifest_path']):
                    raise ValueError("Manifest file not found.")
            else:
                params['symbols'] = self.selected_symbols[:]
                if not params['symbols']:
                    raise ValueError("No symbols selected in the queue.")

            params['start_date'] = datetime.strptime(
                self.ids.start_date_field.text, '%Y-%m-%d')
            params['end_date'] = datetime.strptime(
                self.ids.end_date_field.text, '%Y-%m-%d')
            params['interval'] = self.ids.interval_field.text

            params['output_dir'] = self.ids.output_dir_field.text
            if not os.path.isdir(params['output_dir']):
                raise ValueError("Output directory is not valid.")

            params['save_csv'] = self.ids.save_csv_check.active
            params['save_parquet'] = self.ids.save_parquet_check.active
            params['sharding'] = self.ids.sharding_field.text

            if not params['save_csv'] and not params['save_parquet']:
                raise ValueError(
                    "Select at least one save format (CSV or Parquet).")

            self.logs.clear()
            self.ids.progress_bar.value = 0
            self.ids.start_button.disabled = True

            # Get the authenticated kite session from the main app instance
            app = MDApp.get_running_app()
            if not hasattr(app, 'kite') or not app.kite:
                raise ConnectionError(
                    "Kite session not available. Please log in.")

            # Pass the authenticated session to the worker
            worker = DownloadWorker(params, self, kite_session=app.kite)
            worker.start()

        except Exception as e:
            UILogger.add_log_entry(self.logs, f"Configuration Error: {e}")
            self.ids.start_button.disabled = False

    def go_back(self):
        """Navigates back to the home screen within the main screen."""
        self.manager.current = 'home'
