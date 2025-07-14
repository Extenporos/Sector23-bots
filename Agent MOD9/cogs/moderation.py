import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta

PROTECTED_FILE = "./data/protected.json"

def set_rol_protegido(guild_id, role_name):
    if not os.path.exists(PROTECTED_FILE):
        data = {}
    else:
        with open(PROTECTED_FILE, "r") as f:
            data = json.load(f)
    data[str(guild_id)] = role_name
    with open(PROTECTED_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_role_protegido(guild):
    if not os.path.exists(PROTECTED_FILE):
        return None
    with open(PROTECTED_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(guild.id), None)

def tiene_rol_protegido(member):
    protegido = get_role_protegido(member.guild)
    if protegido:
        return any(role.name == protegido for role in member.roles)
    return False
    
HISTORY_FILE = "./data/history.json"
ROL_PROTEGIDO = "Creador y desarrollador de Sector 23"

def cargar_historial():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def guardar_historial(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def registrar_evento(guild_id, user_id, accion, moderador):
    data = cargar_historial()
    guild_id = str(guild_id)
    user_id = str(user_id)
    if guild_id not in data:
        data[guild_id] = {}
    if user_id not in data[guild_id]:
        data[guild_id][user_id] = []
    data[guild_id][user_id].append({
        "accion": accion,
        "por": moderador,
        "fecha": datetime.utcnow().isoformat()
        await interaction.response.send_message(
    f"🔇 {usuario.mention} fue muteado por {tiempo} minutos. "
    f"Se desmuteará a las { (ahora + timedelta(minutes=tiempo)).strftime('%H:%M:%S') } hora CDMX."

        )

    })
    guardar_historial(data)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def tiene_rol_protegido(self, member):
        return any(role.name == ROL_PROTEGIDO for role in member.roles)

    @app_commands.command(name="kick", description="Expulsa a un usuario.")
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón"):
        if self.tiene_rol_protegido(usuario):
            await interaction.response.send_message("❌ No puedes expulsar a este usuario.", ephemeral=True)
            return
        await usuario.kick(reason=razon)
        registrar_evento(interaction.guild.id, usuario.id, f"Kicked: {razon}", str(interaction.user))
        await interaction.response.send_message(f"👢 {usuario.mention} ha sido expulsado.")

    @app_commands.command(name="ban", description="Banea a un usuario.")
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón"):
        if self.tiene_rol_protegido(usuario):
            await interaction.response.send_message("❌ No puedes banear a este usuario.", ephemeral=True)
            return
        await usuario.ban(reason=razon)
        registrar_evento(interaction.guild.id, usuario.id, f"Banned: {razon}", str(interaction.user))
        await interaction.response.send_message(f"🔨 {usuario.mention} ha sido baneado.")

    @app_commands.command(name="mute", description="Mutea a uno o más usuarios o un rol (excepto @everyone).")
    async def mute(self, interaction: discord.Interaction, objetivo: discord.Role | discord.Member, tiempo: int = 10, razon: str = "Sin razón"):
        if isinstance(objetivo, discord.Role):
            if objetivo.name == "@everyone" or objetivo.name == ROL_PROTEGIDO:
                await interaction.response.send_message("❌ No puedes mutear este rol.", ephemeral=True)
                return
            for member in interaction.guild.members:
                if objetivo in member.roles:
                    await member.timeout(timedelta(minutes=tiempo), reason=razon)
                    registrar_evento(interaction.guild.id, member.id, f"Muted por rol: {razon}", str(interaction.user))
            await interaction.response.send_message(f"🔇 Todos los del rol {objetivo.name} fueron muteados por {tiempo} minutos.")
        else:
            if self.tiene_rol_protegido(objetivo):
                await interaction.response.send_message("❌ No puedes mutear a este usuario.", ephemeral=True)
                return
            await objetivo.timeout(timedelta(minutes=tiempo), reason=razon)
            registrar_evento(interaction.guild.id, objetivo.id, f"Muted: {razon}", str(interaction.user))
            await interaction.response.send_message(f"🔇 {objetivo.mention} fue muteado por {tiempo} minutos.")

    @app_commands.command(name="changerole", description="Asigna un nuevo rol a un usuario.")
    async def changerole(self, interaction: discord.Interaction, usuario: discord.Member, nuevo_rol: discord.Role):
        if self.tiene_rol_protegido(usuario):
            await interaction.response.send_message("❌ No puedes cambiar el rol de este usuario.", ephemeral=True)
            return
        await usuario.add_roles(nuevo_rol)
        registrar_evento(interaction.guild.id, usuario.id, f"Rol añadido: {nuevo_rol.name}", str(interaction.user))
        await interaction.response.send_message(f"🎭 {usuario.mention} recibió el rol {nuevo_rol.name}.")

    @app_commands.command(name="history", description="Muestra el historial de moderación de un usuario o de todo el servidor.")
    async def history(self, interaction: discord.Interaction, usuario: discord.Member = None):
        data = cargar_historial()
        gid = str(interaction.guild.id)

        if gid not in data:
            await interaction.response.send_message("📂 No hay historial en el servidor.")
            return

        if usuario:
            uid = str(usuario.id)
            eventos = data[gid].get(uid, [])
            if not eventos:
                await interaction.response.send_message(f"📂 No hay historial para el {usuario.mention}.")
                return
            texto = f"📑 Historial de {usuario.mention}:\n" + "\n".join([f"- {e['accion']} por {e['por']} el {e['fecha']}" for e in eventos])
        else:
            texto = "📑 Historial del servidor:\n"
            for uid, eventos in data[gid].items():
                miembro = interaction.guild.get_member(int(uid))
                nombre = miembro.mention if miembro else f"ID: {uid}"
                texto += f"\n**{nombre}**\n" + "\n".join([f"- {e['accion']} por {e['por']} el {e['fecha']}" for e in eventos]) + "\n"

        await interaction.response.send_message(texto[:2000])

async def setup(bot):
    await bot.add_cog(Moderation(bot))
