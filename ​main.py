import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID của Owner chính
OWNER_ID = 1528398105207378032

# Danh sách chứa ID các user được cấp quyền dùng lệnh
authorized_users = set()

# Biến lưu nội dung cần treo
content_to_spam = ""

# Hàm kiểm tra quyền (Owner hoặc User đã được cấp quyền)
def is_authorized():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID or ctx.author.id in authorized_users:
            return True
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
        return False
    return commands.check(predicate)

# Hàm kiểm tra duy nhất Owner
def is_owner_only():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID:
            return True
        await ctx.send("❌ Chỉ có **Owner** mới có thể thực hiện lệnh này!")
        return False
    return commands.check(predicate)

@tasks.loop(seconds=0.8)
async def spam_task(ctx):
    if content_to_spam:
        await ctx.send(content_to_spam)

@bot.event
async def on_ready():
    print(f"✅ Bot đã sẵn sàng: {bot.user}")

@bot.command()
@is_authorized()
async def treo(ctx, *, text: str = None):
    global content_to_spam
    if not text:
        await ctx.send("❌ Vui lòng nhập nội dung! Ví dụ: `!treo è`")
        return

    if spam_task.is_running():
        await ctx.send("⚠️ Bot đang treo rồi!")
        return

    content_to_spam = text
    spam_task.start(ctx)
    await ctx.send(f"🚀 Bắt đầu treo: **{text}**")

@bot.command()
@is_authorized()
async def stoptreo(ctx):
    global content_to_spam
    if not spam_task.is_running():
        await ctx.send("⚠️ Bot hiện không treo.")
        return

    spam_task.stop()
    content_to_spam = ""
    await ctx.send("🛑 Đã dừng treo!")

# Lệnh dành riêng cho Owner để cấp quyền
@bot.command()
@is_owner_only()
async def capquyen(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Vui lòng tag người dùng cần cấp quyền! Ví dụ: `!capquyen @user`")
        return
    
    if member.id in authorized_users:
        await ctx.send(f"⚠️ {member.mention} đã có quyền từ trước!")
        return

    authorized_users.add(member.id)
    await ctx.send(f"✅ Đã cấp quyền sử dụng bot cho {member.mention}!")

# Lệnh dành riêng cho Owner để xóa quyền
@bot.command()
@is_owner_only()
async def xoaquyen(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Vui lòng tag người dùng cần xóa quyền! Ví dụ: `!xoaquyen @user`")
        return
    
    if member.id not in authorized_users:
        await ctx.send(f"⚠️ {member.mention} chưa được cấp quyền!")
        return

    authorized_users.remove(member.id)
    await ctx.send(f"🗑️ Đã tước quyền của {member.mention}!")

TOKEN = "MTU1NDQ1MjM0MDgxMDE4Njg0Mg.GTgPuI.3CwMMgq9up3NQab9pXpCvst5n4KBxCUSzPhQMY"
bot.run(TOKEN)
