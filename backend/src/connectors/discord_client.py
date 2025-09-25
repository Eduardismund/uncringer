import discord
import asyncio
from datetime import datetime, timezone, timedelta


class DiscordClient:
    
    def __init__(self, token: str, server_id: str):
        self.token = token
        self.server_id = server_id
        self.audios = []
    
    async def fetch_audio_messages(self, after_message_id: str = "0", lookback_hours: int = 24):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        
        client = discord.Client(intents=intents)
        self.audios = []
        
        @client.event
        async def on_ready():
            guild = client.get_guild(int(self.server_id))
            if not guild:
                await client.close()
                return
            
            after_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
            
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(after=after_time, limit=100):
                        if str(message.id) <= after_message_id:
                            continue
                        
                        audio_data = self._extract_audio_data(message)
                        if audio_data:
                            self.audios.extend(audio_data)
                            
                except:
                    pass
            
            await client.close()
        
        await client.start(self.token)
        return sorted(self.audios, key=lambda x: x["message_id"])
    
    def _extract_audio_data(self, message):
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.webm', '.opus']
        audio_list = []
        
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in audio_extensions):
                reactions = self._get_reactions(message)
                
                audio_list.append({
                    "message_id": str(message.id),
                    "author": str(message.author),
                    "channel_id": str(message.channel.id),
                    "filename": attachment.filename,
                    "audio_url": attachment.url,
                    "reactions": reactions,
                    "total_reactions": sum(reactions.values()),
                    "posted_at": message.created_at
                })
        
        return audio_list
    
    def _get_reactions(self, message):
        reactions = {}
        for reaction in message.reactions:
            reactions[str(reaction.emoji)] = reaction.count
        return reactions