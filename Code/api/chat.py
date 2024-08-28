import logging

from DMBotNetwork import Client

logger = logging.getLogger("Chat")

class ChatModule(Client):
    async def net_ooc_chat(self, sender: str, msg: str):
        logger.info(f"[OOC] {sender}: {msg}")
        return
    
    @staticmethod
    async def send_ooc(msg: str):
        await Client.request_method("ooc_chat", msg=msg)
        return
