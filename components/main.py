from twitchio.ext import commands

help_msg = '''
thechosenbot (v1.0) by sethechosenone_________________________________ Here's a list of available commands (with more to come!):________________________________________ !help - display this help message________________ !socials - display link to socials__________________ !donate - display donation link (you can play a text to speech message!!!)
'''

class MainComponent(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name = 'help')
    async def help(self, ctx: commands.Context):
        await ctx.send(help_msg)

    @commands.command(name = 'donate')
    async def donate(self, ctx: commands.Context):
        await ctx.send("Enjoying the stream? You can donate here: https://streamlabs.com/sethechosenone/tip")