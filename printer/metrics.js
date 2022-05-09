const express = require('express');
const app = express();

const util = require('./util.js');
const { inkLevel } = util;
const config = require('../config/config.json');
const { RIGHT_PRINTER_IP, LEFT_PRINTER_IP } = config;

const client = require('prom-client');

let register = new client.Registry();

const inkLevelRight = new client.Gauge({
  name: 'ink_level_right',
  help: 'metric_help',
  async collect() {
    const currentValue = await inkLevel(RIGHT_PRINTER_IP);
    this.set(currentValue);
  },
});

register.registerMetric(inkLevelRight);

register.setDefaultLabels({
  app: 'sce-printer',
});

client.collectDefaultMetrics({ register });

app.get('/metrics', async (request, response) => {
  response.setHeader('Content-type', register.contentType);
  response.end(await register.metrics());
});

app.listen(5000, () => {});
