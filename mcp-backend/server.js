require("dotenv").config(); // Load environment variables
const express = require("express");
const cors = require("cors");
const connectDB = require("./config/database"); // Import database connection function
const authRoutes = require("./auth"); // Import authentication routes
const logRoutes = require("./logs"); // Import logs API

const app = express();
app.use(cors()); // Enable Cross-Origin Resource Sharing
app.use(express.json()); // Parse incoming JSON data

// Connect to MongoDB
connectDB();

// Routes
app.use("/auth", authRoutes);
app.use("/logs", logRoutes);

app.listen(process.env.PORT, () => {
    console.log(`🚀 Server running on port ${process.env.PORT}`);
});
