require("dotenv").config();
const express = require("express");
const cors = require("cors");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const mongoose = require("mongoose");

// Database Connection
const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI);
        console.log("✅ MongoDB connected");
    } catch (error) {
        console.error("❌ MongoDB connection error:", error);
        process.exit(1);
    }
};
connectDB();

// User Model
const UserSchema = new mongoose.Schema({
    name: String,
    email: { type: String, unique: true },
    password: String,
});
const User = mongoose.model("User", UserSchema);

const app = express();
app.use(cors());
app.use(express.json());

// ✅ Default Route
app.get("/", (req, res) => {
    res.send("✅ Server is running!");
});

// 📌 Registration Route
app.post("/register", async (req, res) => {
    try {
        console.log("🔹 Register request received:", req.body);

        const { name, email, password } = req.body;
        if (!name || !email || !password) {
            console.log("❌ Missing fields");
            return res.status(400).json({ message: "All fields are required" });
        }

        let user = await User.findOne({ email });
        if (user) {
            console.log("❌ User already exists");
            return res.status(400).json({ message: "User already exists" });
        }

        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);
        user = new User({ name, email, password: hashedPassword });

        await user.save();
        console.log("✅ User registered:", user);

        res.status(201).json({ message: "User registered successfully!" });
    } catch (error) {
        console.error("❌ Error registering user:", error);
        res.status(500).json({ message: "Server error" });
    }
});

// 📌 Login Route
app.post("/login", async (req, res) => {
    try {
        console.log("🔹 Login request received:", req.body);

        const { email, password } = req.body;
        if (!email || !password) {
            console.log("❌ Missing fields");
            return res.status(400).json({ message: "All fields are required" });
        }

        const user = await User.findOne({ email });
        if (!user) {
            console.log("❌ User not found");
            return res.status(400).json({ message: "Invalid credentials" });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            console.log("❌ Incorrect password");
            return res.status(400).json({ message: "Invalid credentials" });
        }

        const token = jwt.sign({ id: user._id, email: user.email }, process.env.JWT_SECRET, { expiresIn: "1h" });
        console.log("✅ Login successful, token:", token);

        res.json({ message: "Login successful!", token });
    } catch (error) {
        console.error("❌ Error logging in:", error);
        res.status(500).json({ message: "Server error" });
    }
});

// ✅ Server Port
const PORT = process.env.PORT || 5000;
const HOST = "http://localhost";

// ✅ Start the Server
app.listen(PORT, () => {
    console.log(`\n🚀 Server is running at: \x1b[36m${HOST}:${PORT}\x1b[0m`);
});
