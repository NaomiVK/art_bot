import os
import base64
import json
import aiohttp
import discord
from discord.ext import commands

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen2.5-vl-72b-instruct:free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Your style-only system prompt
ARTSTYLE_SYSTEM_PROMPT = (
    "ArtStyle Muse provides precise, subject-neutral descriptions of an artwork's stylistic elements, "
    "strictly avoiding any mention of subject matter, objects, or specific scenes within the artwork. "
    "Descriptions focus exclusively on general stylistic attributes such as color choices, brushwork, "
    "texture, composition, line work, shading techniques, and other technical elements of style. Each "
    "response begins with the recognized art style in lowercase, when applicable (e.g., impressionist painting, "
    "cyberpunk illustration, impasto oil painting), followed by a sentence that distills only the artistic techniques "
    "and visual qualities without reference to narrative or objects. For example: 'cyberpunk illustration, bold black "
    "linework with intense neon accents and stark, high-contrast shading.' Known styles such as Impressionism, "
    "Post-Impressionism, Anime, Manga, Oil Painting, and Impasto are identified when relevant and are listed at the start of the description."
)

class ArtStyle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not OPENROUTER_API_KEY:
            # Don't crash the bot, but warn loudly in logs.
            print("[ArtStyle] WARNING: OPENROUTER_API_KEY is not set. The /style command will fail.")

    @discord.slash_command(description="Describe the art style of an image (no subject matter)")
    async def style(
        self,
        ctx: discord.ApplicationContext,
        image: discord.Attachment,
        private: discord.Option(bool, "Send as base64 (avoid external fetch)", required=False, default=True),
    ):
        await ctx.defer()  # give us some breathing room

        try:
            # Build multimodal content
            if private:
                # Download and embed as base64 data URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(image.url) as resp:
                        resp.raise_for_status()
                        data = await resp.read()
                b64 = base64.b64encode(data).decode("utf-8")
                data_url = f"data:{image.content_type or 'image/png'};base64,{b64}"
                image_part = {"type": "image_url", "image_url": {"url": data_url}}
            else:
                # Pass the Discord CDN URL directly
                image_part = {"type": "image_url", "image_url": {"url": image.url}}

            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": ARTSTYLE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe only the style. Do not mention any objects or subject matter."},
                            image_part,
                        ],
                    },
                ],
                "temperature": 0.2,
                "max_tokens": 200,
            }

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                # Optional but nice to have for OpenRouter analytics/attribution
                "HTTP-Referer": "https://railway.app/",
                "X-Title": "ArtStyle Muse Discord Bot",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=120) as r:
                    if r.status != 200:
                        text = await r.text()
                        return await ctx.respond(f"OpenRouter error {r.status}: {text[:500]}")
                    data = await r.json()

            output = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not output:
                return await ctx.respond("No style description returned. Try again or use a different image.")

            # Enforce a short, one-line result for Discord niceness
            cleaned = " ".join(output.strip().split())[:700]
            await ctx.respond(cleaned)

        except Exception as e:
            await ctx.respond(f"Failed to analyze style: {e}")

def setup(bot):
    bot.add_cog(ArtStyle(bot))
