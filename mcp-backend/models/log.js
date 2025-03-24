const mongoose = require("mongoose");

const LogSchema = new mongoose.Schema({
    user: String,
    message: String,
    action: String,
    timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model("Log", LogSchema);
