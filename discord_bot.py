# DISCORD Bot
# SOME AI USED


# NEEDS FROM BACKEND:

# can you buy after start date?
# should i rename the commands? my-games and my-stocks are a bit annoying to type
# is my_games necessary?

import datetime
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from helpers.backend_manager import Backend
from helpers.bot import StockGameBot
from helpers.logic_manager import Frontend

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents with all necessary permissions
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
# intents.dm_messages = True # for invite user command

bot = StockGameBot()



# TODO ask how start date works and remove "can users join after start" if not needed
# this code is a complete mess at the moment, trying to get it to work my way but it is taking more time than it's worth
# THIS ITERATION IS WORKING IN THE CURRENT STATE
# TODO Add user to game
# TODO Return success/error embed


@bot.tree.command(name="join-game", description="Join an existing stock game")
@app_commands.describe(
    game_id="ID of the game to join"
)
async def join_game(
    interaction: discord.Interaction, 
    game_id: int,
    name: str | None = None
):
    pass

# TODO Process purchase
# TODO Return transaction embed
@bot.tree.command(name="buy-stock", description="Buy a stock in a game")
@app_commands.describe(
    game_id="ID of the game",
    ticker="Stock ticker symbol",
    shares="Number of shares to buy"
)
async def buy_stock(
    interaction: discord.Interaction, 
    game_id: int, 
    ticker: str, 
    shares: int
):
    pass

# TODO Add remove stock pick
# TODO Return transaction embed
@bot.tree.command(name="remove-stock", description="Remove a stock from your picks")
@app_commands.describe(
    game_id="ID of the game",
    ticker="Stock ticker symbol"
)
async def remove_stock(
    interaction: discord.Interaction, 
    game_id: int, 
    ticker: str
):
    pass

# TODO Get user's stocks from frontend
# TODO Add autofill for user's games
# TODO Display stocks in an embed with stock info
# TODO Add buttons for buying/selling stocks?
# TODO Add pagination if there are many stocks (10+)
# TODO Add last updated date/time
@bot.tree.command(name="my-stocks", description="View your stocks in a game")
@app_commands.describe(
    game_id="ID of the game"
)
async def my_stocks(
    interaction: discord.Interaction,
    game_id: int
):
    pass

# TODO Add join game button to game info embed
# TODO change to show only public games
# TODO add buttons for joining games?
# TODO add autofill for user's games?
@bot.tree.command(name="game-info", description="View information about a game")
@app_commands.describe(
    game_id="ID of the game to view"
)
async def game_info(
    interaction: discord.Interaction, 
    game_id: int
):
        
    game = bot.frontend.game_info(game_id)

    if not game:
        embed = discord.Embed(
            title="Game Not Found",
            description=f"Could not find a game with ID {game_id}.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="Game #{game_id}",
            description=f"Name: {game['name']}\nStart Date: {game['start_date']}\nEnd Date: {game['end_date']}\nStarting Money: ${game['starting_money']}\nTotal Picks: {game['total_picks']}\nExclusive Picks: {game['exclusive_picks']}\nJoin After Start: {game['join_after_start']}\nSell During Game: {game['sell_during_game']}\nStatus: {game['status']}",
            color=discord.Color.blue()
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

# TODO get list of public games
#   - list the user count
#   - list the game status
#   - list the game name
# TODO add pagination if there are many games (10+)
# TODO add buttons for joining games?
# TODO add a joinable parameter?
@bot.tree.command(name="game-list", description="View a list of all games")
async def game_list(
    interaction: discord.Interaction
):
    pass

@bot.tree.command(name="my-games", description="View your games and their status")
async def my_games(
    interaction: discord.Interaction
):
    # Get user's games from frontend
    games = bot.frontend.my_games(interaction.user.id)
    
    # Create embed for the response
    embed = discord.Embed(
        title="Your Games",
        color=discord.Color.blue()
    )
    
    if not games:
        embed.description = "No games found"
    else:
        # Add each game to the embed
        for game in games:
            # Create status indicator
            status_emoji = "🟢" if game['status'] == 'open' else "🔴"
            
            # Add game field
            embed.add_field(name=f"{status_emoji} Game #{game['id']}: {game['name']}")
    
    # Add footer with command usage
    embed.set_footer(text=f"Use /game-info <game_id> for more details")
    
    # Send the response
    await interaction.response.send_message(embed=embed, ephemeral=True)

# TODO Get leaderboard data from backend
# TODO Create autofill for user's games
# TODO Create paginated embed with leaderboard
# TODO Add navigation buttons if multiple pages
@bot.tree.command(name="leaderboard", description="View game leaderboard")
@app_commands.describe(
    game_id="ID of the game",
    user_id="Optional: View specific user's position"
)
async def leaderboard(
    interaction: discord.Interaction, 
    game_id: int, 
    user_id: discord.User = None
):
    pass

# Run the bot using the token
if TOKEN:
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("Login Failed: Improper token has been passed.")
    except discord.errors.PrivilegedIntentsRequired:
        print("Privileged Intents Required: Make sure Message Content Intent is enabled on the Discord Developer Portal.")
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")
else:
    print("Error: DISCORD_TOKEN environment variable not found.")
    print("Please set the DISCORD_TOKEN environment variable before running the bot.")
    print("Error: DISCORD_TOKEN environment variable not found.")
    print("Please set the DISCORD_TOKEN environment variable before running the bot.")
