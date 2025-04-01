import asyncio

from gui.gui_manager import GUIManager



def main():
    gui = GUIManager()
    asyncio.run(gui.main())

if __name__ == "__main__":
   main()
