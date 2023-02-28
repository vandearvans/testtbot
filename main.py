import discord
from discord.ext import commands

client = commands.Bot(command_prefix='!')

support_categories = {
    'general': 1234567890, # Replace with your channel IDs
    'billing': 1234567890,
    'technical': 1234567890
}

status_messages = {
    'open': 'Awaiting Staff Response',
    'in_progress': 'Being Handled by Staff',
    'closed': 'This Ticket has been Resolved'
}

class Ticket:
    def __init__(self, category, user, subject, description):
        self.category = category
        self.user = user
        self.subject = subject
        self.description = description
        self.status = 'open'
        self.channel = None
        self.message = None

    def set_channel(self, channel):
        self.channel = channel

    def set_message(self, message):
        self.message = message

    def close(self):
        self.status = 'closed'
        self.message.edit(content=f'Ticket Status: {status_messages[self.status]}')

    def update_status(self, status):
        self.status = status
        self.message.edit(content=f'Ticket Status: {status_messages[self.status]}')

tickets = {}

@client.command()
async def create(ctx, category: str, subject: str, *, description: str):
    if category.lower() not in support_categories:
        await ctx.send(f'Error: Invalid Category. Please use one of the following: {", ".join(support_categories.keys())}')
        return

    category_id = support_categories[category.lower()]
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await ctx.guild.create_text_channel(name=f'{ctx.author.name}-ticket', category=discord.utils.get(ctx.guild.categories, id=category_id), overwrites=overwrites)
    message = await channel.send(f'**{subject}**\n\n{description}\n\nCreated by {ctx.author.mention}\n\nTicket Status: {status_messages["open"]}')
    ticket = Ticket(category.lower(), ctx.author, subject, description)
    ticket.set_channel(channel)
    ticket.set_message(message)
    tickets[channel.id] = ticket

@client.command()
async def close(ctx):
    if ctx.channel.id not in tickets:
        await ctx.send('Error: This is not a Ticket Channel.')
        return

    ticket = tickets[ctx.channel.id]
    ticket.close()
    del tickets[ctx.channel.id]

@client.command()
async def status(ctx, status: str):
    if ctx.channel.id not in tickets:
        await ctx.send('Error: This is not a Ticket Channel.')
        return

    if status.lower() not in status_messages:
        await ctx.send(f'Error: Invalid Status. Please use one of the following: {", ".join(status_messages.keys())}')
        return

    ticket = tickets[ctx.channel.id]
    ticket.update_status(status.lower())

client.run('YOUR_DISCORD_BOT_TOKEN')
