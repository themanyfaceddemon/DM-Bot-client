import logging

from api import *
from DMBotNetwork import Client
from gui.start import DMClientApp
from root_path import ROOT_PATH
from systems.loc import Localization as loc

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    loc.load_translations(ROOT_PATH / "Content" / "Client" / "loc" / 'rus')
    
    app = DMClientApp()
    Client()
    app.setup()
    app.run()
