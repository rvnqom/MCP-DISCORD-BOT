import logging

logger = logging.getLogger("mcp")

async def apply_actions(message, rule):
    actions = rule["actions"]
    
    if "delete" in actions:
        await message.delete()
    
    if "dm_warning" in actions:
        await message.author.send(f"⚠️ Your message was blocked by rule: {rule['name']}")
    
    if "log" in actions:
        logger.info(f"Rule Triggered: {rule['name']} by {message.author} in #{message.channel} - {message.content}")
    
    if "reply_faq" in actions:
        await message.channel.send("Here’s our FAQ: https://yourserver.com/faq")
