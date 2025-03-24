const express = require("express");
const passport = require("passport");
const session = require("express-session");
const DiscordStrategy = require("passport-discord").Strategy;
const User = require("./models/User");
require("dotenv").config();

const router = express.Router(); // ✅ Use router instead of app

// Session setup
router.use(session({ secret: "supersecret", resave: false, saveUninitialized: false }));

// Passport setup
passport.use(new DiscordStrategy(
    {
        clientID: process.env.DISCORD_CLIENT_ID,
        clientSecret: process.env.DISCORD_CLIENT_SECRET,
        callbackURL: process.env.DISCORD_REDIRECT_URI,
        scope: ["identify"],
    },
    async (accessToken, refreshToken, profile, done) => {
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
        return done(null, user);
    }
));

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser(async (id, done) => {
    const user = await User.findById(id);
    done(null, user);
});

// Discord Auth Route
router.get("/discord", passport.authenticate("discord"));
router.get(
    "/discord/callback",
    passport.authenticate("discord", { failureRedirect: "/" }),
    (req, res) => {
        res.redirect("http://localhost:5500/dashboard.html");
    }
);

module.exports = router; // ✅ Make sure to export router
