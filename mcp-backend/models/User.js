const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
    discordId: String,
    username: String,
    avatar: String,
    accessToken: String
});

module.exports = mongoose.model("User", UserSchema);
