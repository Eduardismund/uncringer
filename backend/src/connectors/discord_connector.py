import discord
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict


class DiscordConnector:

    def __init__(self, token: str, server_id: str):
        self.token = token
        self.server_id = server_id
        self.audio_messages = []
        
        self.audio_extensions = ['.wav', '.mp3', '.ogg', '.m4a', '.webm', '.opus']
    
    async def fetch_audio_messages(self, after_message_id: str = "0", lookback_hours: int = 24) -> List[Dict]:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        
        client = discord.Client(intents=intents)
        self.audio_messages = []
        
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
                            self.audio_messages.extend(audio_data)
                            
                except discord.errors.Forbidden:
                    continue
                except Exception:
                    continue
            
            await client.close()
        
        await client.start(self.token)
        return sorted(self.audio_messages, key=lambda x: x["message_id"])
    
    def _extract_audio_data(self, message: discord.Message) -> List[Dict]:
        audio_list = []
        
        for attachment in message.attachments:
            if self._is_audio_file(attachment.filename):
                reactions = self._extract_reactions(message)
                
                audio_list.append({
                    "message_id": str(message.id),
                    "author": str(message.author),
                    "channel_id": str(message.channel.id),
                    "channel_name": message.channel.name,
                    "filename": attachment.filename,
                    "audio_url": attachment.url,
                    "reactions": reactions,
                    "total_reactions": sum(reactions.values()),
                    "posted_at": message.created_at
                })
        
        return audio_list
    
    def _is_audio_file(self, filename: str) -> bool:
        return any(filename.lower().endswith(ext) for ext in self.audio_extensions)
    
    def _extract_reactions(self, message: discord.Message) -> Dict[str, int]:
        reactions = {}
        for reaction in message.reactions:
            reactions[str(reaction.emoji)] = reaction.count
        return reactions