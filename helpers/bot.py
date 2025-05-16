import asyncio
import logging
import random
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import format_dt

from helpers.backend_manager import Backend
from helpers.logic_manager import Frontend


class StockGameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        self.frontend = Frontend()
        self.backend = Backend()
        
        super().__init__(
            "$",
            intents=intents,
            )

    async def on_ready(self):
        """Prints a message to the console when the bot is online and syncs slash commands."""
        asyncio.create_task(self.sync_commands())
        
        print(self.backend.get_game(1))
        
        assert self.user is not None
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        

    async def setup_hook(self):
        """Is run whenever the bot starts up to initialize things"""
        self.tree.on_error = self.on_tree_error

        cog_list = [
            "stock_cog"
        ]
        await self.load_cogs(cog_list)
        self.add_persistent_views()


    async def sync_commands(self):
        """Update all the bot's slash commands"""
        
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
            for command in synced:
                print(f"   - {command.name}: {command.description}")
        except Exception as e:
            print(f"Failed to sync commands: {e}")



    def add_persistent_views(self):
        """To be used to add persistent views to the bot"""
        pass

    async def load_cogs(self, cog_list: list[str]):
        """Load all the commands/cogs for the bot"""
        for cog_name in cog_list:
            try:
                await self.load_extension("cogs." + cog_name)
            except commands.errors.ExtensionNotFound:
                logging.exception(cog_name + " cog not found")
            except commands.errors.ExtensionAlreadyLoaded:
                pass
            except commands.errors.NoEntryPointError:
                logging.exception("Put the setup() function back in " + cog_name + " fool.")
    
    @tasks.loop(minutes=5)
    async def _update_status_loop(self):
        """Updates the bot's status every 5 minutes"""
        await self.update_status()


    async def update_status(self):
        """The command to update the bot's status, pulled out in case we want to run it elsewhere"""
        amount_of_money_watching = random.randint(9000000, 11000000)
        
        new_status = f"${amount_of_money_watching} get traded 💸"
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=new_status))


    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        """When the bot gets an error, this will automatically give an error message"""
        if isinstance(error, app_commands.CommandOnCooldown):
            s= format_dt(datetime.now() + timedelta(seconds=error.retry_after), "R")
            await interaction.response.send_message(f"This command is on cooldown! Please try again in {s} seconds!", ephemeral=True)

        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permissions to run this command!", ephemeral=True)
        
        else:
            await interaction.response.send_message("Something went wrong running this command! Please try again, or let us know if this keeps happening!", ephemeral=True)
        
        print(error.with_traceback(None))
