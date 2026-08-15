from __future__ import annotations

from typing import Optional, Dict, Any
from app.models.models import StyleProfile
from app.schemas.schemas import StyleProfileResponse

DEFAULT_STYLE_PROFILE: Dict[str, Any] = {
    "tone": "casual",
    "length": "short",
    "emoji_usage": "medium",
    "humor": "high",
    "formality": "low",
    "language_mix": "english",
    "response_directness": "direct",
}

class StyleService:
    def __init__(self, db):
        self.db = db

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        from sqlalchemy import select
        result = await self.db.execute(select(StyleProfile).where(StyleProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        if profile:
            return profile.profile_data
        return DEFAULT_STYLE_PROFILE.copy()

    async def save_profile(self, user_id: str, profile_data: Dict[str, Any]) -> StyleProfile:
        from sqlalchemy import select
        result = await self.db.execute(select(StyleProfile).where(StyleProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        if profile:
            profile.profile_data = profile_data
        else:
            profile = StyleProfile(user_id=user_id, profile_data=profile_data)
            self.db.add(profile)
        await self.db.flush()
        return profile

    def build_prompt_fragment(self, profile: Dict[str, Any]) -> str:
        return (
            f"Style: tone={profile.get('tone')}, length={profile.get('length')}, "
            f"emoji={profile.get('emoji_usage')}, humor={profile.get('humor')}, "
            f"formality={profile.get('formality')}, directness={profile.get('response_directness')}."
        )
