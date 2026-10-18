// Fixture and acceptance test for Task 5: Setup-uv #1028
const assert = require('assert');

// Simulates esbuild class output
var ReserveCacheError = class _ReserveCacheError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ReserveCacheError';
    Object.setPrototypeOf(this, _ReserveCacheError.prototype);
  }
};

var ValidationError = class _ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, _ValidationError.prototype);
  }
};

function unpatchedHandleCacheError(error, logger) {
  if (error.name === ValidationError.name) {
    throw error;
  } else if (error.name === ReserveCacheError.name) {
    logger.info(`Failed to save: ${error.message}`);
  } else {
    logger.warning(`Failed to save: ${error.message}`);
  }
}

function safeHandleCacheError(error, logger) {
  // Patched to check instanceof or string literal identity
  if (error instanceof ValidationError || error.name === 'ValidationError') {
    throw error;
  } else if (error instanceof ReserveCacheError || error.name === 'ReserveCacheError') {
    logger.info(`Failed to save: ${error.message}`);
  } else {
    logger.warning(`Failed to save: ${error.message}`);
  }
}

// Tests
function runTests() {
  const loggerMock = {
    infoLogs: [],
    warnLogs: [],
    info(msg) { this.infoLogs.push(msg); },
    warning(msg) { this.warnLogs.push(msg); }
  };

  const err = new ReserveCacheError('Unable to reserve cache');

  // Test 1: Confirm unpatched handler produces false-alarm warning
  const logger1 = Object.create(loggerMock);
  logger1.infoLogs = [];
  logger1.warnLogs = [];
  unpatchedHandleCacheError(err, logger1);
  assert.strictEqual(logger1.warnLogs.length, 1, 'Unpatched handler should emit a warning');
  assert.strictEqual(logger1.infoLogs.length, 0, 'Unpatched handler failed to route to info');

  // Test 2: Confirm patched handler correctly routes to info
  const logger2 = Object.create(loggerMock);
  logger2.infoLogs = [];
  logger2.warnLogs = [];
  safeHandleCacheError(err, logger2);
  assert.strictEqual(logger2.infoLogs.length, 1, 'Patched handler must route to info');
  assert.strictEqual(logger2.warnLogs.length, 0, 'Patched handler must not emit warning');

  // Test 3: Regression safety for unexpected errors
  const genericErr = new Error('Disk full');
  const logger3 = Object.create(loggerMock);
  logger3.infoLogs = [];
  logger3.warnLogs = [];
  safeHandleCacheError(genericErr, logger3);
  assert.strictEqual(logger3.warnLogs.length, 1, 'Unexpected errors must still warn');

  console.log('All Task 5 tests passed successfully.');
}

runTests();
