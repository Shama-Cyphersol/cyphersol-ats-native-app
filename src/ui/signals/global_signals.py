from PyQt6.QtCore import pyqtSignal, QObject

class GlobalSignalManager(QObject):
    update_table = pyqtSignal(str)  # Signal to broadcast case updation

global_signal_manager = GlobalSignalManager()
