const mongoose = require("mongoose");
const User = require("./models/User"); // Ensure this matches your model
require("dotenv").config();

mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(async () => {
        console.log("✅ Connected to MongoDB");

        // Insert sample user
        await User.create({
            discordId: "123456789012345678",
            username: "TestUser",
            email: "testuser@example.com",
            avatar: "https://example.com/avatar.png",
            createdAt: new Date()
        });

        console.log("✅ Sample user added!");
        mongoose.connection.close();
    })
    .catch(err => console.error("❌ MongoDB Error:", err));
