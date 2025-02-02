const express = require("express");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const WebSocket = require("ws");
const mongoose = require("mongoose");
const session = require("express-session");
const { TelegramClient } = require("telegram");
const { StringSession } = require("telegram/sessions");

const app = express();
const port = 3000;
const apiId = 13873014;
const apiHash = "4f77fd424d8c9e5661e365498724c2ad";
const sessionString = "1BQANOTEuMTA4LjU2LjE4MgG7l9NZrz5M6HnbYleDSaTUUtxrGcJ3hgX/yQHV00IKiXvdtw/jZwgRPeTjkvmtNK2L6LXVz/TQHe0TdQ0Np53aqEkjxSA72XbjAMRtU2IGeGSzqWp1AF5zLFh0BMPAM5s7WnC7aBQtW/iCpOFuRHeUfY3PG6nk1hsKm43lptmvN0sbTRTtXxjrEsdsEMLkWT7hTySMjQM7rrpFBG+sz+hb7VCoMeSxG6oJ8XubJnm4JpbMNh9Q+emZqOUgXm3GxV4iNuOWsYfWqBhZty486EZJBvkU+izY37OcCIdlMCz07KtuP8zqwfK/uFSlyesy8TFWmmOoX6Z6kxs+Y+yViFp3hA==";

(async () => {
  const client = await new TelegramClient(new StringSession(sessionString), apiId, apiHash, {
    connectionRetries: 5,
  });
  await client.connect();
  console.log("Connected to Telegram!");

  // MongoDB connection
  const mongoUri = "mongodb+srv://anshprajjwal:damdamdam@botdb.ppc3ixq.mongodb.net/test?retryWrites=true&w=majority";
  mongoose.connect(mongoUri, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log("Connected to MongoDB"))
    .catch((err) => console.error("MongoDB connection error:", err));

  const userCybroxesSchema = new mongoose.Schema({
    _id: { type: Number, required: true, unique: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
  });
  const UserCybrox = mongoose.model("userclutches", userCybroxesSchema);

  // Use sessions for login tracking
  app.use(session({
    secret: 'secret-key', // change to a secure random string
    resave: false,
    saveUninitialized: true,
  }));

  // Middleware to serve static files
  app.use(express.static('public'));
  app.use(express.json()); // To handle JSON bodies
  app.use(express.urlencoded({ extended: true })); // For URL-encoded data (form submissions)

  // Multer setup for file uploads
  const upload = multer({ dest: 'uploads/' });

  // Login Route
  app.post("/login", async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "Email and password are required." });
    }

    try {
      const user = await UserCybrox.findOne({ email });
      if (!user) {
        return res.status(401).json({ message: "Invalid email or password." });
      }

      // Check password (plaintext, no bcrypt used)
      if (user.password !== password) {
        return res.status(401).json({ message: "Invalid email or password." });
      }

      // Store user info in session
      req.session.userId = user._id; 
      console.log(user)// Store the user id in session
      res.status(200).json({ message: "Login successful!" });
    } catch (err) {
      console.error("Error during login:", err);
      res.status(500).json({ message: "Internal server error." });
    }
  });

  // Check if user is logged in before uploading
  const isLoggedIn = (req, res, next) => {
    if (!req.session.userId) {
      return res.redirect("/");
    }
    next();
  };

  // Upload Route
  app.get("/upload", isLoggedIn, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'upload.html'));
  });

  app.post("/upload", isLoggedIn, upload.single('file'), async (req, res) => {
    const filePath = req.file.path;
    const originalFileName = req.file.originalname;
    const newFilePath = path.join('uploads', originalFileName);

    const uploadDir = path.join(__dirname, 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }

    fs.rename(filePath, newFilePath, async (err) => {
      if (err) {
        console.error("Error renaming file:", err);
        return res.status(500).send("Error renaming file.");
      }

      try {
        const botUsername = 'Clusterxbot'; // Replace with your bot username

        // Send the renamed file to the bot
        await client.sendFile(botUsername, {
          file: newFilePath,
          caption: `${req.session.userId}`,
        });

        console.log("File sent to bot successfully!");
        res.status(200).send("File uploaded and sent to bot successfully!");

      } catch (error) {
        console.error("Error sending file to bot:", error);
        res.status(500).send("Error sending file to bot.");
      }
    });
  });

  // WebSocket setup
  const server = app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
  });

  const wss = new WebSocket.Server({ server });

  wss.on('connection', (ws) => {
    console.log('New WebSocket connection established');
    ws.send("Connected to server. Waiting for messages...");
  });

  // Telegram event handling
  client.addEventHandler(async (event) => {
    const message = event.message;
    if (event.className === "UpdateNewMessage") {
      const json = JSON.parse(message.message);
      if(json.uploader === req.session.userId){
      wss.clients.forEach(a => {
        if (a.readyState === WebSocket.OPEN) {
          a.send(message.message);
        }
      });
    }
    }
  });

})();
