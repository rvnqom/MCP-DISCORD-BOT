from datetime import datetime, timedelta
import discord
from collections import defaultdict

# In-memory warning tracker: { (guild_id, user_id): [(timestamp, reason), ...] }
warnings = defaultdict(list)

# Configurable thresholds
WARNING_RESET_HOURS = 24

# Replace with your actual Muted role ID
MUTED_ROLE_ID = 1353766518349107321  # Replace this with your actual Muted role ID
# Replace with your actual Admin role ID
ADMIN_ROLE_ID = 1353632125810905129  # Replace this with your actual Admin role ID

async def issue_warning(bot, user, guild, reason="Policy Violation", message=None):
    now = datetime.utcnow()
    key = (guild.id, user.id)

    # Clean expired warnings (>24 hours)
    warnings[key] = [w for w in warnings[key] if (now - w[0]).total_seconds() < WARNING_RESET_HOURS * 3600]
    warnings[key].append((now, reason))
    count = len(warnings[key])

    # Try to get member object (not just user)
    member = guild.get_member(user.id)
    if not member:
        try:
            member = await guild.fetch_member(user.id)
        except discord.NotFound:
            return {"count": count, "action": "Failed to find user"}

    # Debug: Print the available roles in the guild
    print([role.name for role in guild.roles])

    # Take action based on warning count
    if count == 1:
        try:
            until = discord.utils.utcnow() + timedelta(seconds=60)
            await member.timeout(until, reason=reason)
            return {"count": count, "action": "Timeout for 60 seconds"}
        except Exception as e:
            return {"count": count, "action": f"Failed to timeout: {e}"}

    elif count == 2:
        try:
            # Fetch admin role by ID
            admin_role = guild.get_role(ADMIN_ROLE_ID)  # Fetch role by ID

            if admin_role:
                log_channel = discord.utils.get(guild.text_channels, name="mod-logs")  # Optional log channel
                if log_channel:
                    await log_channel.send(
                        f"🚨 Admin Alert: {member.mention} has {count} warnings.\nReason: {reason}"
                    )
                
                # Send a message mentioning the admin role
                if message:
                    await message.channel.send(
                        f"{admin_role.mention} {member.mention} has {count} warnings for {reason}."
                    )
                
                return {"count": count, "action": "Admin role notified"}
            else:
                return {"count": count, "action": "Admin role not found"}
        except Exception as e:
            return {"count": count, "action": f"Failed to notify admin role: {e}"}

    return {"count": count, "action": "Warning recorded"}

# Get current warning count
async def get_warning_count(bot, user, guild):
    now = datetime.utcnow()
    key = (guild.id, user.id)

    # Remove expired warnings
    warnings[key] = [w for w in warnings[key] if (now - w[0]).total_seconds() < WARNING_RESET_HOURS * 3600]
    return len(warnings[key])

