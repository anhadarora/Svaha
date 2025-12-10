import random
from PySide6.QtWidgets import QComboBox, QSpinBox, QCheckBox
from PySide6.QtCore import Qt

class WizardWalker:
    """
    A 'monkey testing' utility to automatically walk through and interact with
    the SetupTabWidget wizard.
    """

    def __init__(self, main_window, qtbot):
        """
        Initializes the walker.

        Args:
            main_window: The main application window instance.
            qtbot: The qtbot fixture for UI interaction.
        """
        self.main_window = main_window
        self.qtbot = qtbot
        self.setup_widget = main_window.trainer_screen.setup_tab
        self.history = []

    def inspect_current_page(self):
        """
        Finds all interactive widgets on the current wizard page.

        Returns:
            A list of enabled QComboBox, QSpinBox, and QCheckBox widgets.
        """
        current_page = self.setup_widget.stack.currentWidget()
        if not current_page:
            return []

        widgets = []
        widgets.extend(current_page.findChildren(QComboBox))
        widgets.extend(current_page.findChildren(QSpinBox))
        widgets.extend(current_page.findChildren(QCheckBox))

        # Filter for only enabled widgets that are visible
        return [w for w in widgets if w.isEnabled() and w.isVisible()]

    def fuzz_page(self, iterations=5):
        """
        Randomly interacts with widgets on the current page.

        Args:
            iterations (int): The number of random interactions to perform.
        """
        fuzzable_widgets = self.inspect_current_page()
        if not fuzzable_widgets:
            self.history.append("No fuzzable widgets found on this page.")
            return

        for i in range(iterations):
            widget = random.choice(fuzzable_widgets)
            widget_name = widget.objectName() or f"{type(widget).__name__}_{i}"

            if isinstance(widget, QComboBox):
                if widget.count() > 0:
                    index = random.randint(0, widget.count() - 1)
                    widget.setCurrentIndex(index)
                    self.history.append(f"Set {widget_name} to index {index} ('{widget.currentText()}')")
            
            elif isinstance(widget, QSpinBox):
                min_val, max_val = widget.minimum(), widget.maximum()
                if min_val < max_val:
                    value = random.randint(min_val, max_val)
                    widget.setValue(value)
                    self.history.append(f"Set {widget_name} to {value}")

            elif isinstance(widget, QCheckBox):
                checked = not widget.isChecked()
                widget.setChecked(checked)
                self.history.append(f"Set {widget_name} to {checked}")
            
            # Let the UI process events after each change
            self.qtbot.wait(50)

    def try_navigate_next(self):
        """
        Clicks the 'Next' button and checks if navigation was successful.

        Returns:
            True if the wizard moved to the next page, False otherwise.
        """
        stack = self.setup_widget.stack
        next_button = self.setup_widget.next_button
        
        if not next_button.isEnabled():
            self.history.append("Next button is disabled. Cannot navigate.")
            return False

        old_index = stack.currentIndex()
        self.qtbot.mouseClick(next_button, Qt.LeftButton)
        self.qtbot.wait(100) # Wait for UI to update
        new_index = stack.currentIndex()

        if new_index > old_index:
            self.history.append(f"Navigated from page {old_index} to {new_index}.")
            return True
        else:
            self.history.append(f"Failed to navigate from page {old_index}. Still on the same page.")
            return False

    def walk_wizard(self):
        """
        Walks through the entire wizard, fuzzing each page.

        The process is:
        1. Fuzz the current page.
        2. Try to navigate to the next page.
        3. Repeat until the last page is reached or navigation fails.

        Returns:
            A list of strings logging all actions taken.
        """
        self.history.append("Starting wizard walk...")
        
        # The wizard requires a data source to be selected to enable other pages.
        # This is a specific action to "un-stick" the fuzzer from the first page.
        # A more advanced fuzzer might learn this, but for now, we hardcode it.
        if self.setup_widget.stack.currentIndex() == 0:
            self.history.append("Pre-fuzz action: Selecting a data source to enable wizard.")
            data_source_widget = self.setup_widget.data_source_widget
            # This is a simplified interaction; assumes the list has items.
            if data_source_widget.available_instruments_list.count() > 0:
                data_source_widget.available_instruments_list.setCurrentRow(0)
                data_source_widget.add_selected()
                self.qtbot.wait(100) # Wait for signal propagation

        while self.setup_widget.stack.currentIndex() < self.setup_widget.stack.count() - 1:
            current_page_index = self.setup_widget.stack.currentIndex()
            self.history.append(f"--- Fuzzing Page {current_page_index} ---")
            
            self.fuzz_page()
            
            if not self.try_navigate_next():
                self.history.append("Wizard walk stuck. Aborting.")
                break
        
        # Fuzz the final page
        final_page_index = self.setup_widget.stack.currentIndex()
        self.history.append(f"--- Fuzzing Final Page {final_page_index} ---")
        self.fuzz_page()

        self.history.append("Wizard walk finished.")
        return self.history
