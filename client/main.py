import asyncio

from gui.gui_manager import GUIManager



def main():
    gui = GUIManager()
    try:
        asyncio.run(gui.main())
    except ValueError:
        print("Приложение закрыто")

if __name__ == "__main__":
   main()
