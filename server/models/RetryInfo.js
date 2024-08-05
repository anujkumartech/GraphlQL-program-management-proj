const mongoose = require('mongoose');

const RetryInfoSchema = new mongoose.Schema({
  traceId: {
    type: String,
    required: true,
  },
  retries: {
    type: Number,
    required: true,
  },
  duration: {
    type: Number,
    required: true,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  typeOfRetry: {
    type: String,
    required: true,
  },
});

module.exports = mongoose.model('RetryInfo', RetryInfoSchema);
