const express = require("express");
const passport = require("passport");
const jwt = require("jsonwebtoken"); // ✅ Import JWT
const DiscordStrategy = require("passport-discord").Strategy;
const User = require("./models/User");
require("dotenv").config();

const router = express.Router();

passport.use(
    new DiscordStrategy(
        {
            clientID: process.env.DISCORD_CLIENT_ID,
            clientSecret: process.env.DISCORD_CLIENT_SECRET,
            callbackURL: process.env.DISCORD_REDIRECT_URI,
            scope: ["identify", "email"],
        },
        async (accessToken, refreshToken, profile, done) => {
            try {
                let user = await User.findOne({ discordId: profile.id });
                if (!user) {
                    user = new User({
                        discordId: profile.id,
                        username: profile.username,
                        avatar: profile.avatar,
                        accessToken,
                    });
                    await user.save();
                }

                // ✅ Generate JWT Token
                const token = jwt.sign(
                    { id: profile.id, username: profile.username },
                    process.env.JWT_SECRET, // Secret key
                    { expiresIn: "1h" } // Token expires in 1 hour
                );

                user.token = token; // Save token to user object (optional)
                return done(null, user);
            } catch (error) {
                return done(error, null);
            }
        }
    )
);

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser(async (id, done) => {
    try {
        const user = await User.findById(id);
        done(null, user);
    } catch (error) {
        done(error, null);
    }
});

router.get("/discord", passport.authenticate("discord"));

router.get(
    "/discord/callback",
    passport.authenticate("discord", { failureRedirect: "/" }),
    (req, res) => {
        res.redirect("http://localhost:5500/dashboard.html");
    }
);

module.exports = router;
