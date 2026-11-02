#!/usr/bin/env python3
# Original x5.0 preferences methods relocated unchanged for x6.0.
from __future__ import annotations

# The host binds its unchanged save_json_settings helper after the module loads.

class EditorPreferencesMixin:

    def _restore_preferences(self) -> None:
        self.word_wrap_action.setChecked(bool(self.settings.get("word_wrap", True)))
        self.line_numbers_action.setChecked(bool(self.settings.get("line_numbers", True)))
        self.status_bar_action.setChecked(bool(self.settings.get("status_bar", True)))
        self.statusBar().setVisible(self.status_bar_action.isChecked())
        locked = bool(self.settings.get("locked_mode", self.settings.get("view_only", False)))
        self.view_only_action.setChecked(locked)
        self.editor.set_view_only(locked)
        self.settings.pop("view_only", None)
        self.editor.set_word_wrap_enabled(self.word_wrap_action.isChecked())
        self.editor.set_line_numbers_visible(self.line_numbers_action.isChecked())
        self.editor.set_tab_width_spaces(int(self.settings.get("tab_width", 4)))
        self.tabbed_mode_action.setChecked(self.toolbar_mode == "tabbed")
        self.classic_mode_action.setChecked(self.toolbar_mode == "classic")
        self.editor_canvas_theme_action.setChecked(not self.editor_canvas_light)
        self.drop_active_action.setChecked(self.drop_open_mode == "active_window")
        self.drop_new_window_action.setChecked(self.drop_open_mode == "new_window")
        getattr(self, f"theme_{self.theme}_action", self.theme_system_action).setChecked(True)
        sizes = self.settings.get("splitter_sizes")
        self._last_splitter_sizes = ([max(1, int(v)) for v in sizes] if isinstance(sizes, list) and len(sizes) == 2 else [3, 2])
        self.set_view_mode(self.view_mode, persist=False)
        self.set_tabbed_collapsed(bool(self.settings.get("tabbed_collapsed", self.settings.get("ribbon_collapsed", False))), persist=False)
        self._apply_toolbar_button_style()

    def persist_preferences(self) -> None:
        if self.view_mode == "split":
            sizes = self.splitter.sizes()
            if len(sizes) == 2 and all(int(v) > 0 for v in sizes):
                self._last_splitter_sizes = [int(v) for v in sizes]
        self.settings.update({
            "theme": self.theme, "icon_family": self.icon_family,
            "toolbar": self.toolbar_mode, "view_mode": self.view_mode,
            "last_editable_view_mode": self.last_editable_view_mode,
            "word_wrap": self.word_wrap_action.isChecked(), "line_numbers": self.line_numbers_action.isChecked(),
            "status_bar": self.status_bar_action.isChecked(), "locked_mode": self.view_only_action.isChecked(), "tab_width": self.editor._tab_width_spaces,
            "zoom": self.zoom_percent, "splitter_sizes": getattr(self, "_last_splitter_sizes", [3, 2]),
            "drop_open_mode": self.drop_open_mode,
            "editor_canvas_light": self.editor_canvas_light,
            "classic_toolbar_items": list(self.classic_toolbar_items),
            "tabbed_collapsed": bool(getattr(self, "_tabbed_collapsed", False)),
            "tutorial_seen": bool(self.tutorial_seen),
        })
        # MaqaronyPad deliberately stores no recent-file history.
        self.settings.pop("recent_files", None)
        self.settings.pop("interface", None)
        self.settings.pop("button_labels", None)
        self.settings.pop("retro_toolbar_items", None)
        self.settings.pop("ribbon_collapsed", None)
        save_json_settings(self.settings)

