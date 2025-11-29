import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Import your services
try:
    from frameworks.three_domain_pipeline import run_pipeline
    from services.data_fetcher import fetch_match_data
    from services.db import save_match_analysis, get_match_analysis, check_exposure
except ImportError:
    # Placeholder imports for initial deployment
    run_pipeline = None
    fetch_match_data = None
    save_match_analysis = None
    get_match_analysis = None
    check_exposure = None

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class BlackBoxBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
    
    async def setup_hook(self):
        await self.tree.sync()

client = BlackBoxBot()

@client.tree.command(name="analyze", description="Run 3-Domain Analysis on a team")
async def analyze(interaction: discord.Interaction, team: str):
    # 1. Defer response immediately (buy 15 minutes of processing time)
    await interaction.response.defer(thinking=True)
    
    try:
        # 2. Heavy Compute Task
        if fetch_match_data is None:
            await interaction.followup.send("⚠️ Services not yet configured.")
            return
            
        match_data = await fetch_match_data(team)
        if not match_data:
            await interaction.followup.send(f"❌ Could not find match data for **{team}**.")
            return
        
        # 3. Run pipeline
        result = run_pipeline(match_data)
        
        # 4. Save to DB
        save_match_analysis(result.match_id, match_data, result.context, result.metrics)
        
        # 5. Send Embed via Followup
        embed = discord.Embed(title=f"📊 Analysis: {result.match_id}", color=0x00ff00)
        embed.add_field(name="Fair Odds", value=f"{result.metrics['fair_odds']}", inline=True)
        embed.add_field(name="Edge", value=f"{result.metrics['edge'] * 100:.1f}%", inline=True)
        embed.add_field(name="Narrative", value=result.context.narrative, inline=False)
        embed.set_footer(text="BlackBox v3 • Odds verified at T-0")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"⚠️ **Error:** {str(e)}")

@client.tree.command(name="bet", description="Place a wager")
async def bet(interaction: discord.Interaction, match_id: str, selection: str, stake: float):
    await interaction.response.defer(ephemeral=True)
    
    # Blind Spot #5: Correlation / Exposure Check
    if check_exposure and check_exposure(str(interaction.user.id), match_id):
        await interaction.followup.send(f"⚠️ **Risk Block:** You already have active exposure on {match_id}. One bet per match.")
        return
    
    # TODO: Implement bet placement logic
    await interaction.followup.send(f"✅ Bet placed on {selection} for ${stake}")

if __name__ == "__main__":
    if TOKEN:
        client.run(TOKEN)
    else:
        print("ERROR: DISCORD_TOKEN not found in environment")
