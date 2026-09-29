import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

MAX_MESSAGES = 50
DELAY = 0.5


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        await self.tree.sync()


bot = MyBot()


@bot.event
async def on_ready():
    print(f"Giriş yapıldı: {bot.user}")
    print("Bot hazır!")


@bot.tree.command(
    name="spam",
    description="Belirlediğin mesajı sınırlı sayıda spam atar."
)
@app_commands.describe(
    mesaj="Gönderilecek mesaj",
    adet="Kaç kez gönderilecek (1-50)"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def test(
    interaction: discord.Interaction,
    mesaj: str,
    adet: app_commands.Range[int, 1, MAX_MESSAGES]
):
    # User Install / External App modunda normal channel.send()
    # yerine interaction follow-up mesajları kullanılır.
    await interaction.response.send_message(
        f"Test başlıyor: **{adet} mesaj**, **{DELAY} saniye arayla**.",
        ephemeral=True
    )

    for i in range(adet):
        await asyncio.sleep(DELAY)

        try:
            await interaction.followup.send(mesaj)
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Discord bu kanalda External App'ın herkese açık mesaj göndermesine izin vermiyor. "
                "Sunucuda **Uygulamaları Kullan / Use External Apps** iznini kontrol et.",
                ephemeral=True
            )
            break
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Mesaj gönderilemedi: `{e}`",
                ephemeral=True
            )
            break


@bot.tree.command(
    name="dmspam",
    description="Bulunduğun DM konuşmasına tek bir test mesajı gönderir."
)
@app_commands.describe(mesaj="Gönderilecek mesaj")
@app_commands.allowed_contexts(
    guilds=False,
    dms=True,
    private_channels=True
)
async def dmtest(
    interaction: discord.Interaction,
    mesaj: str
):
    # Birebir DM veya Grup DM desteği
    if not isinstance(interaction.channel, (discord.DMChannel, discord.GroupChannel)):
        await interaction.response.send_message(
            "❌ Bu komut yalnızca birebir DM veya Grup DM'de kullanılabilir.",
            ephemeral=True
        )
        return

    try:
        await interaction.response.send_message(
            "✅ DM test mesajı gönderiliyor.",
            ephemeral=True
        )
        await interaction.followup.send(mesaj)
    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ DM mesajı gönderilemedi.",
                ephemeral=True
            )
    except discord.HTTPException as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Mesaj gönderilemedi: `{e}`",
                ephemeral=True
            )


@test.error
async def test_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Bu komutu kullanmak için **Mesajları Yönet** yetkisine sahip olmalısın.",
                ephemeral=True
            )
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Bir hata oluştu.",
                ephemeral=True
            )


if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN bulunamadı. Tokenı ortam değişkeni olarak ekle."
    )

bot.run(TOKEN)
