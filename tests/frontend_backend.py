import os

from helpers.logic_manager import Frontend

if __name__ == "__main__":
    DB_NAME = os.getenv('DB_NAME')
    _owner = os.getenv("OWNER")
    assert DB_NAME is not None
    assert _owner is not None
    OWNER = int(_owner)
    
    game = Frontend(database_name=DB_NAME, owner_user_id=OWNER) # Create frontend 
    # Misc tests
    print(game.backend.list_users(ids_only=True)) # List users from the backend
    #create = game.new_game(user_id=OWNER, name="TestGame", start_date="2025-05-06", end_date="2025-05-30") # Try to create game
    print(game.join_game(user_id=OWNER,game_id=1)) # Try to join a game
    print(game.my_games(user_id=OWNER)) # Try to list games you are joined to
    
    
    print(game.list_games()) # Print list of games
    print(game.buy_stock(OWNER, 1, 'MSFT')) # Try to purchase stock
    print(game.update(OWNER)) # Try to update