from models.game_model import GameModel
from view.gui_view import GUIView
from controllers.game_controller import GameController
 
 
def main():
    GameController(GameModel(), GUIView()).run()
 
 
if __name__ == "__main__":
    main()