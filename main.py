import sys

from PyQt5.QtWidgets import QApplication

from editor import DevWorkspace


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Prism Workspace")

    window = DevWorkspace()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
