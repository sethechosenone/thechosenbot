from twitchio.ext import commands

socials_help_msg = '''
____________________________ !insta - link to sethechosenone on instagram__ !tiktok - link to sethechosenone on tiktok______ !youtube - link to sethechosenone on youtube
'''

class SocialsComponent(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name = 'socials', invoke_fallback = True)
    async def socials(self, ctx: commands.Context):
        await ctx.send(socials_help_msg)

    @socials.command(name = 'insta')
    async def insta(self, ctx: commands.Context):
        await ctx.send('You can follow sethechosenone on Instagram here: https://www.instagram.com/sethechosenone/')

    @socials.command(name = 'tiktok')
    async def tiktok(self, ctx: commands.Context):
        await ctx.send('You can follow sethechosenone on TikTok here: https://www.tiktok.com/@sethechosenone')

    @socials.command(name = 'youtube')
    async def youtube(self, ctx: commands.Context):
        await ctx.send('You can subscribe to sethechosenone on YouTube here: https://www.youtube.com/@sethechosenone')