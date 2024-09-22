from typing import Optional

from pypresence import AioPresence


class DiscordRPC:
    RPC = None

    def __init__(self) -> None:
        try:
            DiscordRPC.RPC = AioPresence(1227926138400276561)

        except Exception:
            DiscordRPC.RPC = None

    @classmethod
    async def connect(cls) -> None:
        if cls.RPC is None:
            return
        
        try:
            await cls.RPC.connect()
        
        except Exception:
            cls.RPC = None
            
    @classmethod
    async def update(
        cls,
        state: Optional[str] = None,
        detals: Optional[str] = None,
        start: Optional[int] = None,
    ) -> None:
        if cls.RPC is None:
            return
        
        await cls.RPC.update(state=state, details=detals, start=start)  # type: ignore - Cain: bruh. Good RPC lib
