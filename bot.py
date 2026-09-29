import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

MAX_MESSAGES = 5
DELAY = 1


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents
        )


bot = MyBot()


@bot.event
async def on_ready():
    print(f"Giriş yapıldı: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi.")
    except Exception as e:
        print(f"SYNC HATASI: {e}")

    print("Bot hazır!")


@bot.tree.command(
    name="test",
    description="Belirlediğin mesajı sınırlı sayıda test eder."
)
@app_commands.describe(
    mesaj="Gönderilecek mesaj",
    adet="Kaç kez gönderilecek (1-5)"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def test(
    interaction: discord.Interaction,
    mesaj: str,
    adet: app_commands.Range[int, 1, MAX_MESSAGES]
):
    print(
        f"{interaction.user} "
        f"/test kullandı | adet={adet}"
    )

    await interaction.response.send_message(
        f"✅ Test başladı. {adet} mesaj gönderilecek.",
        ephemeral=True
    )

    for i in range(adet):
        try:
            await interaction.followup.send(mesaj)

            if i < adet - 1:
                await asyncio.sleep(DELAY)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Bu kanalda mesaj gönderemiyorum.",
                ephemeral=True
            )
            break

        except Exception as e:
            print(f"TEST HATASI: {e}")

            await interaction.followup.send(
                f"❌ Hata oluştu: {e}",
                ephemeral=True
            )
            break


@bot.tree.command(
    name="dmtest",
    description="DM konuşmasına test mesajı gönderir."
)
@app_commands.describe(
    mesaj="Gönderilecek mesaj"
)
@app_commands.allowed_contexts(
    guilds=False,
    dms=True,
    private_channels=True
)
async def dmtest(
    interaction: discord.Interaction,
    mesaj: str
):
    try:
        await interaction.response.send_message(
            "✅ DM test gönderiliyor.",
            ephemeral=True
        )

        await interaction.followup.send(mesaj)

    except Exception as e:
        print(f"DMTEST HATASI: {e}")


@test.error
async def test_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    print(
        f"TEST COMMAND ERROR: "
        f"{type(error).__name__}: {error}"
    )

    if isinstance(error, app_commands.MissingPermissions):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Mesajları Yönet yetkisine sahip olmalısın.",
                ephemeral=True
            )
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Hata: {error}",
                ephemeral=True
            )


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    print(
        f"APP COMMAND ERROR: "
        f"{type(error).__name__}: {error}"
    )

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Hata: {error}",
                ephemeral=True
            )
    except Exception:
        pass


if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN bulunamadı."
    )

bot.run(TOKEN)
