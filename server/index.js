const express = require('express');
const colors = require('colors');
const port = process.env.PORT || 5001;
const cors = require('cors');
require('dotenv').config();
const { graphqlHTTP } = require('express-graphql');
const schema = require('./schema/schema');
const connectDB = require('./config/db');
const RetryInfo = require('./models/RetryInfo');
const app = express();

let isFaulty = false;

// connect to database here
connectDB();
app.use(cors());
app.use(express.json());

// Middleware to block /graphql when in fault state
app.use('/graphql', (req, res, next) => {
  if (isFaulty) {
    return res.status(503).send('Service Unavailable');
  }
  next();
});

// To test out queries -> http://localhost:5001/graphql -> kinda like postman when working with an API
app.use('/graphql',
  graphqlHTTP({
    schema,
    graphiql: process.env.NODE_ENV === 'development', // This graphiql tool sets the process in development kinda like true
  })
);

app.get('/demo', (req, res) => {
  res.send('Hello World');
});

app.get('/fault/:seconds', (req, res) => {
  const seconds = parseInt(req.params.seconds, 10);
  if (isNaN(seconds)) {
    return res.status(400).send('Invalid number of seconds');
  }

  isFaulty = true;
  res.send(`GraphQL API will be down for ${seconds} seconds`);

  setTimeout(() => {
    isFaulty = false;
  }, seconds * 1000);
});

app.post('/save-retry-info', async (req, res) => {
  const { traceId, retries, duration, typeOfRetry } = req.body;

  if (!traceId || retries === undefined || duration === undefined) {
    return res.status(400).send('Missing required fields');
  }

  try {
    const retryInfo = new RetryInfo({
      traceId,
      retries,
      duration,
      typeOfRetry,
    });

    await retryInfo.save();
    res.status(201).send('Retry information saved successfully');
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

app.get('/retry-info', async (req, res) => {
  try {
    const retryInfos = await RetryInfo.find();
    res.status(200).json(retryInfos);
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

app.listen(port, console.log(`Server running on port ${port}`));
