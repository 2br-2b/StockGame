# INTERFACE INTERACTIONS.  SHOULD EXPECT CRAP FROM USERS AND VALIDATE DATA
from datetime import date, datetime

from helpers.backend_manager import Backend
from helpers.sqlhelper import _iso8601


class Frontend: # This will be where a bot (like discord) interacts
    def __init__(self, database_name: str, owner_user_id: int, default_permissions: int = 210):
        """For use with a discord bot or other frontend. 
        
        Provides  basic error handling, data validation, more user friendly commands, and more.

        Args:
            owner_user_id (int): User ID of the owner.  This user will be able to control everything.
            default_permissions (int, optional): Default permissions for new users. Defaults to 210. (Users can view and join games, but not create their own)
        """
        self.version = "0.0.1"
        self.backend = Backend(database_name)
        self.default_perms = default_permissions
        self.register(owner_user_id, owner_user_id) # Try to register user
        self.backend.update_user(user_id=owner_user_id, permissions = 288)
        self.owner_id = owner_user_id
        pass
    
    # Game actions (Return information that is relevant to overall games)
    def new_game(self, user_id: int, name:str, start_date: str, end_date: str | None = None, starting_money: float = 10000.00, pick_date: str | None = None, private_game: bool = False, total_picks: int = 10, draft_mode: bool = False, sell_during_game: bool = False, update_frequency:str='daily'):
        """Create a new stock game!
        
        WARNING: If using realtime, expect issues

        Args:
            user_id (int): Game creators user ID
            name (str): Name for this game
            start_date (str): Start date in ISO8601 (YYYY-MM-DD)
            end_date (str, optional): End date ISO8601 (YYYY-MM-DD). Defaults to None.
            starting_money (float, optional): Starting money. Defaults to $10000.00.
            pick_date (str, optional): Date stocks must be picked by in ISO8601 (YYYY-MM-DD). Defaults to None (allow players to join anytime)
            private_game(bool, optional): Whether the game is private or not
            total_picks (int, optional): Amount of stocks each user picks. Defaults to 10.
            draft_mode (bool, optional): Whether multiple users can pick the same stock.  If enabled (players cannot pick the same stocks), pick date must be on or before start date Defaults to False.
            sell_during_game (bool, optional): Whether users can sell stocks during the game. Defaults to False.
            update_frequency (str, optional): How often prices should update ('daily', 'hourly', 'minute', 'realtime'). Defaults to 'daily'.
            
        Returns:
            str: Game creation status
        """
        #TODO Should the user be automatically added to their own game? Probably?
        # Data validation
        #TODO add validation for update_frequency
        try: # Validate dates are correct format
            startdate = datetime.strptime(start_date, "%Y-%m-%d").date()
            enddate = datetime.strptime(end_date, "%Y-%m-%d").date()
            #pickdate = datetime.strptime(pick_date, "%Y-%m-%d").date() #TODO add me!
        except: #TODO find specific exceptions
            return "Error! Start or end date format is invalid!"
            
        # Date checks
        if datetime.strptime(start_date, "%Y-%m-%d").date() < date.today():
            return "Error! Start date must not be in the past!"
        
        elif end_date != None and datetime.strptime(start_date, "%Y-%m-%d").date() > datetime.strptime(end_date, "%Y-%m-%d").date():
            return "Error! End date cannot be before start date!"
        
        try: # Try to get user
            user = self.backend.get_user(user_id=user_id)
            
        except KeyError: # User doesn't exist, create.
            try:
                self.backend.add_user(user_id=user_id, display_name=user_id, permissions=self.default_perms) # Try to create a user with no name #TODO log a warning that the user was created with no name
                user = self.backend.get_user(user_id=user_id)
            
            except Exception as e:
                raise e
        
        permissions = user['permissions']
        if permissions - 200 < 0 or permissions - 200 < 19: # User is inactive, banned, or not allowed to create game #TODO this won't work with custom perms!
            reason = "banned" if permissions < 100 else "not allowed to create games!"
            return f"Error! User is {reason}" 
    
        try:  # User is allowed to create games
            self.backend.add_game(
                user_id=int(user_id), 
                name=str(name), 
                start_date=str(start_date), 
                end_date=str(end_date), 
                starting_money=float(starting_money), 
                total_picks=int(total_picks), 
                pick_date=str(pick_date), 
                draft_mode=bool(draft_mode), 
                sell_during_game=bool(sell_during_game), 
                update_frequency=str(update_frequency)
                )
            
        except Exception as e: #TODO find errors
            return e
    
    def list_games(self): #TODO allow filtering
        """List all games.

        Returns:
            list: List of games
        """
        games = self.backend.list_games()
        return games
    
    def game_info(self, game_id:int): 
        """Get information about a specific game.

        Args:
            game_id (int): Game ID

        Returns:
            dict: Game information
        """
        #TODO validate game ID?
        game = self.backend.get_game(game_id=int(game_id))
        return game
    
    # User actions (Return information that is relevant to a specific user)
    
    def register(self, user_id: int, username: str):
        user = self.backend.add_user(user_id=user_id ,display_name=username, permissions=self.default_perms)
        if user['status'] == 'success':
            return "Registered"
        
        elif user['reason'] == 'SQLITE_CONSTRAINT_PRIMARYKEY':
            return "User already registered"
        
        else: #TODO add logging here
            return "Unknown error occurred while registering user"

    def change_name(self, user_id:int, name:str):
        """Change your display name (nickname).

        Args:
            user_id (int): User ID.
            name (str): New name.

        Returns:
            unk: NO idea
        """#TODO what does this reurn
        user = self.backend.update_user(user_id=int(user_id), display_name=str(name))
        return user #TODO return an error instead
    
    def join_game(self, user_id:int, game_id:int):
        """Join a game.

        Args:
            user_id (int): User ID.
            game_id (int): Game ID.

        Returns:
            unk: I have no idea
        """# TODO what does this return?
        #TODO check permissions before running
        game = self.backend.add_user_to_game(user_id=int(user_id), game_id=int(game_id))
        return game
    
    def my_games(self, user_id:int): 
        games = self.backend.list_game_members(user_id=user_id)
        return games #TODO get a friendly name and game name?
    
    def buy_stock(self, user_id:int, game_id:int, ticker:str):
        part_id = self.backend.get_participant_id(user_id=user_id, game_id=game_id)
        stock = self.backend.get_stock(ticker=str(ticker)) # Try to get the stock 
        if stock == "No stocks found": # Stock not yet added:
            self.backend.add_stock(ticker=str(ticker)) #TODO handle invalid tickers!
            stock = self.backend.get_stock(ticker=str(ticker)) #TODO clean this up
        
        pick = self.backend.add_stock_pick(participant_id=part_id, stock_id=stock['id']) # Add the pick
        return pick 
    
    def sell_stock(self, user_id:int, game_id:int, ticker:str): # Will also allow for cancelling an order #TODO add sell_stock
        pass
    
    def my_stocks(self, user_id:int, game_id:int):
        """Get your stocks for a specific game.

        Args:
            user_id (int): User ID.
            game_id (int): Game ID.

        Returns:
            list: Stocks both owned and pending
        """
        #TODO hide sold stocks
        part_id = self.backend.get_participant_id(user_id=user_id, game_id=game_id) # TODO error validation
        picks = self.backend.list_stock_picks(participant_id=part_id)
        return picks
    
    def start_draft(self, user_id:int, game_id:int): #TODO add
        pass
    
    def update(self, user_id:int, game_id:int | None=None, force:bool=False): # Update games or a specific game #TODO add docstring
        #TODO VALIDATION!!!!!!!!!
        if user_id != self.owner_id:
            return "You do not have permission to do this"
        
        self.backend.update_stock_prices() # Update stock prices
        self.backend.update_stock_picks(date=_iso8601('date')) # Update picks
        #TODO update account values!
        #TODO update the rest!
        
    def manage_game(self, user_id:int,): #TODO allow game management here, including approving pending users
        pass
    
    def approve_game_users(self, user_id:int):
        pass


