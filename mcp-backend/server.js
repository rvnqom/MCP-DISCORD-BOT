require("dotenv").config(); // Load environment variables
const express = require("express");
const cors = require("cors");
const session = require("express-session");
const passport = require("passport");

const connectDB = require("./config/database"); // Import database connection function
const authRoutes = require("./auth"); // Import authentication routes
const logRoutes = require("./logs"); // Import logs API

const app = express();

// ✅ Middleware setup
app.use(cors()); // Enable Cross-Origin Resource Sharing
app.use(express.json()); // Parse incoming JSON data

// ✅ Session and Passport setup (added this part)
app.use(session({ secret: "supersecret", resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// ✅ Connect to MongoDB
connectDB();

// ✅ Routes
app.use("/auth", authRoutes);
app.use("/logs", logRoutes);

// ✅ Start the server
const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});

console.log("server.js is loaded successfully");


