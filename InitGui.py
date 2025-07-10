# Launcher widget for FreeCAD
# Copyright (C) 2016, 2017, 2018 triplus @ FreeCAD
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA


# Launcher widget for FreeCAD (fixed for 2025+ with PySide2 and proper shortcut/focus)
# Updated: July 10, 2025

import FreeCADGui as Gui
from PySide2 import QtWidgets, QtGui, QtCore

def singleInstance():
    """Ensure only one instance is running."""
    mw = Gui.getMainWindow()
    if mw:
        for i in mw.findChildren(QtWidgets.QDockWidget):
            if i.objectName() == "Launcher":
                i.deleteLater()

singleInstance()

def dockWidget():
    """Create and show the Launcher dock widget."""
    mw = Gui.getMainWindow()

    # Placeholder icon
    icon = """<svg xmlns="http://www.w3.org/2000/svg" height="64" width="64">
              <rect height="64" width="64" fill="none" /></svg>"""
    iconPixmap = QtGui.QPixmap()
    iconPixmap.loadFromData(str.encode(icon))

    # Launcher input field with keyboard interaction
    class LauncherEdit(QtWidgets.QLineEdit):
        def focusInEvent(self, e):
            if e.reason() != QtCore.Qt.PopupFocusReason:
                modelData()

        def keyPressEvent(self, e):
            if e.key() == QtCore.Qt.Key_Down:
                self.clear()
                completer.setCompletionPrefix("")
                completer.complete()
            else:
                super().keyPressEvent(e)
                index = model.index(0, 0)
                completer.popup().setCurrentIndex(index)

    # Setup completer
    completer = QtWidgets.QCompleter()
    completer.setMaxVisibleItems(16)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    try:
        completer.setFilterMode(QtCore.Qt.MatchContains)
    except AttributeError:
        pass

    edit = LauncherEdit()
    edit.setCompleter(completer)

    model = QtGui.QStandardItemModel()
    completer.setModel(model)

    # Create the dock widget
    dock = QtWidgets.QDockWidget("Launcher")
    dock.setObjectName("Launcher")
    dock.setWidget(edit)
    mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

    def modelData():
        """Fill available actions into the launcher."""
        actions = {}
        for i in mw.findChildren(QtWidgets.QAction):
            if i.objectName() and i.isEnabled():
                actions[i.objectName()] = i

        model.clear()
        for objName, action in actions.items():
            item = QtGui.QStandardItem()
            item.setText(action.text().replace("&", ""))
            item.setIcon(action.icon() if action.icon() else QtGui.QIcon(iconPixmap))
            item.setToolTip(action.toolTip())
            item.setData(objName, QtCore.Qt.UserRole)
            model.appendRow(item)

    def onCompleter(modelIndex):
        """Trigger action when selected from the list."""
        index = completer.completionModel().mapToSource(modelIndex)
        item = model.itemFromIndex(index)
        cmd = item.data(QtCore.Qt.UserRole)
        for act in mw.findChildren(QtWidgets.QAction):
            if act.objectName() == cmd:
                act.trigger()
                break
        edit.clear()
        edit.clearFocus()
        edit.setFocus()

    completer.activated[QtCore.QModelIndex].connect(onCompleter)

    # --- Fix: Ensure the launcher gets focus every time ---
    def focusLauncher():
        dock.show()
        dock.raise_()
        edit.setFocus(QtCore.Qt.ShortcutFocusReason)

    # --- Bind ` grave key as shortcut ---
    action_grave = QtWidgets.QAction("Launcher Grave Focus", mw)
    action_grave.setShortcut(QtGui.QKeySequence("`"))
    action_grave.setObjectName("SetLauncherFocusGrave")
    action_grave.triggered.connect(focusLauncher)
    mw.addAction(action_grave)

    # Optional backup shortcut: Ctrl+Shift+Q
    action_alt = QtWidgets.QAction("Launcher Alt Focus", mw)
    action_alt.setShortcut(QtGui.QKeySequence("Ctrl+Shift+Q"))
    action_alt.setObjectName("SetLauncherFocusAlt")
    action_alt.triggered.connect(focusLauncher)
    mw.addAction(action_alt)

    # Show launcher and build initial model
    modelData()
    focusLauncher()

dockWidget()
