const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const User = require('../models/User'); // Import the User model

// @route   POST /api/register
// @desc    Register a new user
router.post('/register', async (req, res) => {
    const { fullName, email, phoneNumber, password } = req.body;

    try {
        // 1. Check if user already exists
        let user = await User.findOne({ email });
        if (user) {
            return res.status(400).json({ message: 'User with this email already exists.' });
        }

        // 2. Create a new user instance
        user = new User({
            fullName,
            email,
            phoneNumber,
            password,
        });

        // 3. Hash the password before saving
        const salt = await bcrypt.genSalt(10);
        user.password = await bcrypt.hash(password, salt);

        // 4. Save the user to the database
        await user.save();

        // 5. Send a success response
        res.status(201).json({ message: 'User registered successfully!' });

    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
});

module.exports = router;