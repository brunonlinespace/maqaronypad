#!/usr/bin/env python3
"""Existing MaqaronyPad document and file-lifecycle methods, moved unchanged."""
from __future__ import annotations
import locale
from pathlib import Path
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QCheckBox, QFileDialog, QInputDialog, QMessageBox
from document_io import (MAX_FILE_BYTES, SUPPORTED_EXTENSIONS, FileSnapshot, FileStateChangedError,
    absolute_user_path, current_file_state, encode_document, fsync_directory, load_document,
    path_lexists, read_regular_file, rename_path_no_replace, safe_atomic_save, write_new_bytes)
from legacy_ricopad import strip_legacy_envelope


class EditorLifecycleMixin:

    def _clear_document_watcher(self) -> None:
        paths = self.file_watcher.files() + self.file_watcher.directories()
        if paths:
            self.file_watcher.removePaths(paths)

    def _bind_document_watcher(self) -> None:
        """Watch the live target and, when different, its opened symlink entry."""
        self._clear_document_watcher()
        if self.current_path is None:
            return
        watched: list[Path] = [self.current_path]
        if self.backing_path is not None and self.backing_path != self.current_path:
            watched.append(self.backing_path)
        directories: list[str] = []
        files: list[str] = []
        for path in watched:
            parent_text = str(path.parent)
            if path.parent.exists() and parent_text not in directories:
                directories.append(parent_text)
            path_text = str(path)
            if path.exists() and path_text not in files:
                files.append(path_text)
        if directories:
            self.file_watcher.addPaths(directories)
        if files:
            self.file_watcher.addPaths(files)

    def _queue_backing_check(self, *_args) -> None:
        if self.current_path is not None:
            self.backing_check_timer.start()

    def _set_backing_state(self, state: str) -> None:
        if state not in {"normal", "changed", "missing"}:
            raise ValueError(f"Unknown backing state: {state}")
        self.backing_state = state
        if state == "normal":
            self.statusBar().clearMessage(warning_id="backing_file")
        if state == "normal":
            self.reload_external_button.setEnabled(True)
            self.external_label.setText("This file changed on disk after it was opened.")
            self.external_banner.hide()
        elif state == "missing":
            self.external_label.setText(
                "This file is no longer available at its original disk path. "
                "Save Version As preserves the live document; Reload is unavailable."
            )
            self.reload_external_button.setEnabled(False)
            self.external_banner.show()
        else:
            self.external_label.setText("This file changed on disk after it was opened.")
            self.reload_external_button.setEnabled(True)
            self.external_banner.show()
        self._update_ui_state()

    def _current_disk_snapshot(self) -> FileSnapshot | None:
        if self.current_path is None:
            return None
        source_path = self.backing_path or self.current_path
        try:
            _payload, snapshot = read_regular_file(source_path, MAX_FILE_BYTES)
        except OSError:
            return None
        return snapshot

    def handle_backing_path_event(self) -> None:
        """Resolve a watcher event from the exact current-file byte snapshot."""
        if self.current_path is None or self.disk_snapshot is None:
            self._set_backing_state("normal")
            self._bind_document_watcher()
            return
        previous_state = self.backing_state
        current = self._current_disk_snapshot()
        if current is None:
            self._set_backing_state("missing")
        elif current.digest == self.disk_snapshot.digest:
            # Timestamp-only touches are not content changes.
            self.disk_snapshot = current
            self.disk_signature = (
                current.state.device, current.state.inode,
                current.state.size, current.state.mtime_ns,
            )
            self._set_backing_state("normal")
        else:
            self._set_backing_state("changed")
        if self.backing_state != previous_state:
            if self.backing_state == "missing":
                self.statusBar().showMessage(
                    "Backing file missing; the live MaqaronyPad document remains protected.",
                    6000, warning_id="backing_file"
                )
            elif self.backing_state == "changed":
                self.statusBar().showMessage(
                    "File changed outside MaqaronyPad.", 5000, warning_id="backing_file"
                )
        # QFileSystemWatcher drops a file path after deletion/replacement; the
        # parent watch lets us reattach if the path appears again.
        self._bind_document_watcher()

    def _has_external_change(self) -> bool:
        if self.current_path is None or self.disk_snapshot is None:
            return False
        current = self._current_disk_snapshot()
        return current is None or current.digest != self.disk_snapshot.digest

    def _external_change_action(self) -> str:
        """Resolve every Save conflict without silently destroying either version."""
        if self.current_path is None or self.disk_snapshot is None:
            self._overwrite_snapshot = None
            return "overwrite"
        current = self._current_disk_snapshot()
        if current is not None and current.digest == self.disk_snapshot.digest:
            self.disk_snapshot = current
            self._overwrite_snapshot = current
            self._set_backing_state("normal")
            return "overwrite"

        self._set_backing_state("missing" if current is None else "changed")
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(dialog_title("File Changed on Disk"))
        if current is None:
            dialog.setText("This file is no longer available at its original disk path.")
            dialog.setInformativeText(
                "Save Version As preserves the current MaqaronyPad document at a new path. "
                "Overwrite explicitly recreates the original path. Reload is unavailable "
                "until a disk copy exists again."
            )
        else:
            dialog.setText("This file has changed on disk since MaqaronyPad opened or saved it.")
            dialog.setInformativeText(
                "Choose Reload to discard the current MaqaronyPad edits and use the disk copy, "
                "Save Version As to preserve both versions, or Overwrite to explicitly "
                "replace the changed disk copy with the current document."
            )
        reload_button = dialog.addButton("Reload", QMessageBox.ButtonRole.ActionRole)
        reload_button.setEnabled(current is not None)
        version_button = dialog.addButton("Save Version As…", QMessageBox.ButtonRole.ActionRole)
        overwrite_button = dialog.addButton("Overwrite", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(cancel_button)
        dialog.setEscapeButton(cancel_button)
        dialog.exec()
        clicked = dialog.clickedButton()
        if clicked is reload_button:
            self.reload_external_change()
            return "cancel"
        if clicked is version_button:
            return "handled_success" if self.save_version_as() else "cancel"
        if clicked is overwrite_button:
            self._overwrite_snapshot = current
            return "overwrite"
        return "cancel"

    def reload_external_change(self) -> bool:
        source_path = self.backing_path or self.current_path
        if source_path is None or not source_path.is_file():
            return False
        if self.editor.document().isModified():
            response = QMessageBox.question(
                self, dialog_title("Discard Editor Changes"),
                "Reloading will discard your unsaved editor changes. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if response != QMessageBox.StandardButton.Yes:
                return False
        return self.open_path(str(source_path), skip_save_check=True)

    def save_and_exit(self) -> None:
        if self.save_document():
            self.close()

    def _confirm_close_missing_backing(self) -> bool:
        if self.current_path is None:
            return True
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(dialog_title("Backing File Missing"))
        dialog.setText(f"{self.current_path.name} is no longer available at its original path.")
        dialog.setInformativeText(
            "This open editor may be the only remaining copy. Save Version As preserves "
            "it at a new path. Recreate Original enters the protected Save flow, where "
            "Overwrite is still an explicit confirmation."
        )
        save_version = dialog.addButton("Save Version As…", QMessageBox.ButtonRole.AcceptRole)
        recreate = dialog.addButton("Recreate Original…", QMessageBox.ButtonRole.ActionRole)
        close_without = dialog.addButton("Close Without Saving", QMessageBox.ButtonRole.DestructiveRole)
        cancel = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(save_version)
        dialog.setEscapeButton(cancel)
        dialog.exec()
        clicked = dialog.clickedButton()
        if clicked is save_version:
            return self.save_version_as()
        if clicked is recreate:
            return self.save_document()
        if clicked is close_without:
            return True
        return False

    def maybe_save(self) -> bool:
        # Missing backing is data-at-risk even when the editor itself is clean.
        if self.backing_state == "missing":
            return self._confirm_close_missing_backing()
        if not self.editor.document().isModified():
            return True
        answer = QMessageBox.question(
            self, dialog_title("Unsaved Changes"),
            "Save changes to this Markdown document?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Discard:
            return True
        return self.save_document()

    def new_document(self, _checked=False, *, force=False) -> None:
        if not force and not self.maybe_save():
            return
        self._loading = True
        self.editor.load_text("")
        self.editor.document().setModified(False)
        self._loading = False
        self.current_path = None
        self.backing_path = None
        self.file_encoding = "utf-8"
        self.file_bom = b""
        self.file_newline = "\n"
        self.disk_signature = None
        self.disk_snapshot = None
        self.legacy_ricopad_loaded = False
        self.preview.set_document_path(None)
        self._set_backing_state("normal")
        self._clear_document_watcher()
        self.set_view_mode(self.last_editable_view_mode, persist=False)

    def open_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, dialog_title("Open Markdown"), str(Path.home()),
            "Markdown (*.md *.markdown *.mdown *.mkd);;All Files (*)"
        )
        if path:
            self.open_path(path)

    def _choose_source_encoding(self, filename: str) -> str | None:
        system_encoding = locale.getpreferredencoding(False) or "utf-8"
        choices = ["Windows-1252", "ISO-8859-1", "UTF-16 LE", "UTF-16 BE", f"System encoding ({system_encoding})"]
        selected, accepted = QInputDialog.getItem(
            self, dialog_title("Choose Source Encoding"),
            f"{filename} is not valid UTF-8 or a recognised text encoding.\n\nOpen using:",
            choices, 0, False,
        )
        if not accepted:
            return None
        return {
            "Windows-1252": "cp1252", "ISO-8859-1": "iso-8859-1",
            "UTF-16 LE": "utf-16-le", "UTF-16 BE": "utf-16-be",
            f"System encoding ({system_encoding})": system_encoding,
        }[selected]

    def open_path(self, path: str, *, skip_save_check=False) -> bool:
        target = Path(path).expanduser()
        opened_path = absolute_user_path(target)
        if target.suffix.lower() not in SUPPORTED_EXTENSIONS:
            QMessageBox.warning(
                self, dialog_title("Unsupported File"),
                "MaqaronyPad opens Markdown files only (.md, .markdown, .mdown, .mkd)."
            )
            return False
        if not target.is_file():
            QMessageBox.warning(self, dialog_title("Open Failed"), f"File not found:\n{target}")
            return False
        if not skip_save_check and not self.maybe_save():
            return False
        try:
            try:
                data = load_document(opened_path)
            except UnicodeDecodeError:
                encoding = self._choose_source_encoding(target.name)
                if encoding is None:
                    return False
                data = load_document(opened_path, encoding_override=encoding)
            portable, legacy = strip_legacy_envelope(data.text)
        except (OSError, ValueError, UnicodeError) as exc:
            QMessageBox.critical(self, dialog_title("Open Failed"), str(exc))
            return False
        if legacy:
            QMessageBox.information(
                self, dialog_title("Legacy Ricopad Markdown"),
                "This file contains legacy Ricopad rich-format metadata. MaqaronyPad will edit "
                "only the portable Markdown content. Saving removes the Ricopad metadata."
            )
        self._loading = True
        if not self.editor.load_text(portable):
            self._loading = False
            QMessageBox.critical(
                self, dialog_title("Open Failed"),
                "Document exceeds the source editor safety limit."
            )
            return False
        self.editor.document().setModified(False)
        self._loading = False
        self.current_path = opened_path.resolve()
        self.backing_path = opened_path
        self.file_encoding = data.encoding
        self.file_bom = data.bom
        self.file_newline = data.newline
        self.disk_signature = data.signature
        self.disk_snapshot = data.snapshot
        self.legacy_ricopad_loaded = legacy
        self.preview.set_document_path(str(self.current_path))
        self._set_backing_state("normal")
        self._bind_document_watcher()
        self.schedule_preview()
        self._update_ui_state()
        self._focus_current_view()
        self.statusBar().showMessage(f"Loaded {self.current_path.name}", 3000)
        return True

    def _safe_save_current_to(
        self, target: Path, *, encoding: str, bom: bytes, expected: FileSnapshot | None
    ) -> FileSnapshot | None:
        try:
            return safe_atomic_save(
                target, self.editor.toPlainText(), encoding=encoding, bom=bom,
                newline=self.file_newline, expected=expected,
            )
        except FileStateChangedError as exc:
            QMessageBox.warning(self, dialog_title("Save Cancelled"), str(exc))
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, dialog_title("Save Failed"), str(exc))
        return None

    def save_document(self) -> bool:
        if self.current_path is None:
            return self.save_as()
        action = self._external_change_action()
        if action == "handled_success":
            return True
        if action != "overwrite":
            return False
        expected = self._overwrite_snapshot
        self._overwrite_snapshot = None
        snapshot = self._safe_save_current_to(
            self.backing_path or self.current_path,
            encoding=self.file_encoding, bom=self.file_bom, expected=expected,
        )
        if snapshot is None:
            return False
        self.disk_snapshot = snapshot
        self.disk_signature = (
            snapshot.state.device, snapshot.state.inode,
            snapshot.state.size, snapshot.state.mtime_ns,
        )
        self.legacy_ricopad_loaded = False
        self.editor.document().setModified(False)
        self._set_backing_state("normal")
        self._bind_document_watcher()
        self.statusBar().showMessage(f"Saved {self.current_path.name}.", 4000)
        self._update_ui_state()
        return True

    def _save_as_target(self, target: Path) -> bool:
        target = absolute_user_path(target)
        expected: FileSnapshot | None = None
        if path_lexists(target):
            if self.current_path is not None and target.resolve(strict=False) == self.current_path.resolve(strict=False):
                return self.save_document()
            answer = QMessageBox.question(
                self, dialog_title("Replace File"), f"Replace existing file?\n{target}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False
            try:
                _payload, expected = read_regular_file(target, MAX_FILE_BYTES)
            except OSError as exc:
                QMessageBox.warning(self, dialog_title("Save Cancelled"), str(exc))
                return False
        encoding = self.file_encoding
        bom = self.file_bom
        snapshot = self._safe_save_current_to(target, encoding=encoding, bom=bom, expected=expected)
        if snapshot is None:
            return False
        self.backing_path = target
        self.current_path = target.resolve(strict=False)
        self.file_encoding = encoding
        self.file_bom = bom
        self.disk_snapshot = snapshot
        self.disk_signature = (
            snapshot.state.device, snapshot.state.inode,
            snapshot.state.size, snapshot.state.mtime_ns,
        )
        self.legacy_ricopad_loaded = False
        self.editor.document().setModified(False)
        self.preview.set_document_path(str(self.current_path))
        self._set_backing_state("normal")
        self._bind_document_watcher()
        self._update_ui_state()
        return True

    def save_as(self) -> bool:
        initial = str(self.current_path or (Path.home() / "Untitled.md"))
        path, _ = QFileDialog.getSaveFileName(
            self, dialog_title("Save Markdown As"), initial,
            "Markdown (*.md);;Markdown variants (*.markdown *.mdown *.mkd)"
        )
        if not path:
            return False
        target = Path(path)
        if not target.suffix:
            target = target.with_suffix(".md")
        if target.suffix.lower() not in SUPPORTED_EXTENSIONS:
            QMessageBox.warning(self, dialog_title("Unsupported Extension"), "MaqaronyPad saves Markdown documents only.")
            return False
        same_document = self.current_path is not None and target.resolve(strict=False) == self.current_path
        saved = self._save_as_target(target)
        if saved and not same_document:
            self.statusBar().showMessage(f"Saved as {target.name}", 3000)
        return saved

    def save_version_as(self) -> bool:
        if self.current_path is None:
            return self.save_as()
        default = self.current_path.with_name(
            self.current_path.stem + "-version" + self.current_path.suffix
        )
        path, _ = QFileDialog.getSaveFileName(
            self, dialog_title("Save Version As"), str(default),
            "Markdown (*.md *.markdown *.mdown *.mkd)"
        )
        if not path:
            return False
        target = Path(path)
        if not target.suffix:
            target = target.with_suffix(".md")
        if target.suffix.lower() not in SUPPORTED_EXTENSIONS:
            QMessageBox.warning(self, dialog_title("Unsupported Extension"), "MaqaronyPad saves Markdown documents only.")
            return False
        if target.resolve(strict=False) == self.current_path.resolve(strict=False):
            QMessageBox.warning(
                self, dialog_title("Save Version As"),
                "Choose a different path so the changed disk copy is preserved."
            )
            return False
        # Preservation operation: keep the live document's current fidelity.
        prior_state = self.backing_state
        saved = self._save_as_target(target)
        if saved:
            if prior_state == "changed":
                message = f"Saved MaqaronyPad version as {target.name}; external disk copy preserved."
            elif prior_state == "missing":
                message = f"Saved MaqaronyPad version as {target.name}; the original path remains missing."
            else:
                message = f"Saved as {target.name}."
            self.statusBar().showMessage(message, 5000)
        return saved

    def _file_policy(self, key: str, allowed: set[str]) -> str:
        value = str(self.settings.get(key, "ask")).strip().lower()
        return value if value in allowed else "ask"

    def _set_file_policy(self, key: str, value: str) -> None:
        allowed = {
            "dirty_duplicate_action": {"ask", "current", "saved"},
            "dirty_external_action": {"ask", "save", "saved"},
        }.get(key, set())
        if value not in allowed:
            return
        self.settings[key] = value
        actions = self.dirty_duplicate_actions if key == "dirty_duplicate_action" else self.dirty_external_actions if key == "dirty_external_action" else {}
        for selected, action in actions.items():
            action.blockSignals(True); action.setChecked(selected == value); action.blockSignals(False)
        save_json_settings(self.settings)

    def duplicate_file(self) -> None:
        if not self.current_path:
            self.statusBar().showMessage("Save the document before duplicating it.", 3000)
            return
        if not self.current_path.is_file():
            QMessageBox.warning(self, dialog_title("Duplicate Failed"), "The Markdown file no longer exists.")
            return

        dirty = bool(self.editor.document().isModified())
        choice = self._file_policy("dirty_duplicate_action", {"ask", "current", "saved"})
        if dirty and choice == "ask":
            dialog = QMessageBox(self)
            dialog.setIcon(QMessageBox.Icon.Question)
            dialog.setWindowTitle(dialog_title("Unsaved Changes — Duplicate File"))
            dialog.setText("This document has unsaved changes.")
            dialog.setInformativeText(
                "Choose whether the duplicate should contain the current MaqaronyPad document "
                "including unsaved edits, or the last version stored on disk."
            )
            current_button = dialog.addButton("Duplicate Current Document", QMessageBox.ButtonRole.AcceptRole)
            saved_button = dialog.addButton("Duplicate Last Saved Version", QMessageBox.ButtonRole.ActionRole)
            cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
            remember = QCheckBox("Remember this choice", dialog)
            dialog.setCheckBox(remember)
            dialog.setDefaultButton(current_button)
            dialog.setEscapeButton(cancel_button)
            dialog.exec()
            clicked = dialog.clickedButton()
            if clicked is current_button:
                choice = "current"
            elif clicked is saved_button:
                choice = "saved"
            else:
                return
            if remember.isChecked():
                self._set_file_policy("dirty_duplicate_action", choice)

        default = self.current_path.with_name(self.current_path.stem + " copy" + self.current_path.suffix)
        path, _ = QFileDialog.getSaveFileName(
            self, dialog_title("Duplicate File"), str(default),
            "Markdown (*.md *.markdown *.mdown *.mkd)"
        )
        if not path:
            return
        destination = Path(path).expanduser().resolve(strict=False)
        if destination.suffix.lower() not in SUPPORTED_EXTENSIONS:
            destination = destination.with_suffix(self.current_path.suffix)
        if destination == self.current_path.resolve(strict=False):
            QMessageBox.warning(self, dialog_title("Duplicate Failed"), "Choose a different filename for the duplicate.")
            return
        if path_lexists(destination):
            QMessageBox.warning(self, dialog_title("Duplicate Failed"), f"'{destination.name}' already exists.")
            return
        try:
            if dirty and choice == "current":
                payload = encode_document(
                    self.editor.toPlainText(), encoding=self.file_encoding,
                    bom=self.file_bom, newline=self.file_newline,
                )
                mode = self.disk_snapshot.state.mode if self.disk_snapshot is not None else 0o666
            else:
                payload, snapshot = read_regular_file(self.current_path, MAX_FILE_BYTES)
                mode = snapshot.state.mode
            write_new_bytes(destination, payload, mode=mode)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, dialog_title("Duplicate Failed"), str(exc))
            return
        self.statusBar().showMessage(f"Duplicated as {destination.name}.", 4000)

    def _prepare_file_operation(self) -> bool:
        """Resolve unsaved edits before a destructive path operation."""
        if not self.editor.document().isModified():
            return True
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(dialog_title("Unsaved Changes"))
        dialog.setText("This document has unsaved changes.")
        save_button = dialog.addButton("Save", QMessageBox.ButtonRole.AcceptRole)
        discard_button = dialog.addButton("Discard", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(save_button)
        dialog.setEscapeButton(cancel_button)
        dialog.exec()
        clicked = dialog.clickedButton()
        if clicked is save_button:
            return self.save_document()
        if clicked is discard_button:
            if self.current_path is None or not self.current_path.is_file():
                return False
            return self.open_path(str(self.current_path), skip_save_check=True)
        return False

    def rename_file(self) -> None:
        if not self.current_path:
            return
        if not self.current_path.is_file():
            QMessageBox.warning(self, dialog_title("Rename Failed"), "The Markdown file no longer exists.")
            return
        if not self._prepare_file_operation():
            return
        name, ok = QInputDialog.getText(
            self, dialog_title("Rename File"), "New filename:", text=self.current_path.name
        )
        if not ok or not name.strip():
            return
        target = self.current_path.with_name(name.strip()).resolve(strict=False)
        if target.suffix.lower() not in SUPPORTED_EXTENSIONS:
            QMessageBox.warning(
                self, dialog_title("Rename File"),
                "The renamed file must remain a Markdown file."
            )
            return
        if target == self.current_path.resolve(strict=False):
            return
        if path_lexists(target):
            QMessageBox.warning(
                self, dialog_title("Rename Failed"),
                f"A file named '{target.name}' already exists in this folder."
            )
            return
        try:
            _payload, expected = read_regular_file(self.current_path, MAX_FILE_BYTES)
            # Re-check immediately before the no-replace rename.
            if current_file_state(self.current_path) != expected.state:
                raise FileStateChangedError("The Markdown file changed before it could be renamed.")
            old_path = self.current_path
            rename_path_no_replace(old_path, target)
            fsync_directory(target.parent)
            _payload_after, moved_snapshot = read_regular_file(target, MAX_FILE_BYTES)
        except FileStateChangedError as exc:
            QMessageBox.warning(self, dialog_title("Rename Cancelled"), str(exc))
            return
        except OSError as exc:
            QMessageBox.critical(self, dialog_title("Rename Failed"), str(exc))
            return
        self.current_path = target
        self.backing_path = target
        # If disk content had already diverged from the loaded editor, preserve
        # that knowledge across the rename rather than pretending the page synced.
        if self.disk_snapshot is not None and moved_snapshot.digest == self.disk_snapshot.digest:
            self.disk_snapshot = moved_snapshot
            self.disk_signature = (
                moved_snapshot.state.device, moved_snapshot.state.inode,
                moved_snapshot.state.size, moved_snapshot.state.mtime_ns,
            )
            self._set_backing_state("normal")
        else:
            self._set_backing_state("changed")
        self.preview.set_document_path(str(self.current_path))
        self._bind_document_watcher()
        self._update_ui_state()
        self.statusBar().showMessage(f"Renamed {old_path.name} to {target.name}.", 4000)

    def delete_file(self) -> None:
        if not self.current_path:
            return
        if not self.current_path.is_file():
            self._set_backing_state("missing")
            return
        if not self._prepare_file_operation():
            return
        try:
            expected = current_file_state(self.current_path)
        except OSError as exc:
            QMessageBox.warning(self, dialog_title("Delete Cancelled"), str(exc))
            return
        answer = QMessageBox.warning(
            self, dialog_title("Delete File"),
            f"Permanently delete this file?\n{self.current_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            if current_file_state(self.current_path) != expected:
                raise FileStateChangedError(
                    "The Markdown file changed after the confirmation dialog. Nothing was deleted."
                )
            self.current_path.unlink()
            fsync_directory(self.current_path.parent)
        except FileStateChangedError as exc:
            QMessageBox.warning(self, dialog_title("Delete Cancelled"), str(exc))
            return
        except FileNotFoundError:
            pass
        except OSError as exc:
            QMessageBox.critical(self, dialog_title("Delete Failed"), str(exc))
            return
        # Keep the live editor. It is now the only guaranteed surviving copy.
        # Delete retains MaqaronyPad's historical resolved-target semantics even if
        # the document was originally opened through a symlink.
        self.backing_path = self.current_path
        self._set_backing_state("missing")
        self._bind_document_watcher()
        self.statusBar().showMessage(f"Deleted {self.current_path.name}; the open document is retained.", 4000)

    def open_containing_folder(self) -> None:
        folder = self.current_path.parent if self.current_path else Path.home()
        if QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
            if self.current_path:
                self.statusBar().showMessage(f"Opened the folder containing {self.current_path.name}.", 3000)
            else:
                self.statusBar().showMessage(f"Opened {folder.name} externally.", 3000)

    def open_external_editor(self) -> None:
        if not self.current_path:
            QMessageBox.information(self, dialog_title("External Editor"), "Save the file first.")
            return
        if not self.current_path.is_file():
            QMessageBox.warning(self, dialog_title("External Editor"), "The Markdown file no longer exists.")
            return
        dirty = bool(self.editor.document().isModified())
        choice = self._file_policy("dirty_external_action", {"ask", "save", "saved"})
        if dirty and choice == "ask":
            dialog = QMessageBox(self)
            dialog.setIcon(QMessageBox.Icon.Question)
            dialog.setWindowTitle(dialog_title("Unsaved Changes — External Editor"))
            dialog.setText("This document has unsaved changes.")
            dialog.setInformativeText(
                "Choose whether to save the current MaqaronyPad document before opening it "
                "externally, or open the last version already stored on disk."
            )
            save_button = dialog.addButton("Save Changes and Open", QMessageBox.ButtonRole.AcceptRole)
            saved_button = dialog.addButton("Open Last Saved Version", QMessageBox.ButtonRole.ActionRole)
            cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
            remember = QCheckBox("Remember this choice", dialog)
            dialog.setCheckBox(remember)
            dialog.setDefaultButton(save_button)
            dialog.setEscapeButton(cancel_button)
            dialog.exec()
            clicked = dialog.clickedButton()
            if clicked is save_button:
                choice = "save"
            elif clicked is saved_button:
                choice = "saved"
            else:
                return
            if remember.isChecked():
                self._set_file_policy("dirty_external_action", choice)
        if dirty and choice == "save":
            if not self.save_document():
                return
        target = self.current_path
        if target is None or not target.is_file():
            QMessageBox.warning(self, dialog_title("External Editor"), "The Markdown file no longer exists.")
            return
        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))
        if opened:
            self.statusBar().showMessage(f"Opened {target.name} in an external editor.", 3000)
        if not opened:
            QMessageBox.warning(
                self, dialog_title("External Editor"),
                "The desktop could not open this Markdown file with its associated application."
            )
