const express = require("express");
const Log = require("./models/Log");

const router = express.Router(); // ✅ Use router instead of app

// Fetch all logs
router.get("/", async (req, res) => {
    const logs = await Log.find().sort({ timestamp: -1 });
    res.json(logs);
});

// Add new log (for Discord bot)
router.post("/", async (req, res) => {
    const { user, message, action } = req.body;
    const newLog = new Log({ user, message, action });
    await newLog.save();
    res.status(201).json({ success: true });
});

module.exports = router; // ✅ Make sure to export router
