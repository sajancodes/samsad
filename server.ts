import express, { Request, Response } from 'express';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = Number(process.env.PORT) || 3000;
const UPSTREAM_BASE = 'https://fightkaro.com';

app.use(express.json({ limit: '2mb' }));

// Room code alphabet from rooms-CRfnBsqC.js: `ABCDEFGHJKMNPQRSTUVWXYZ23456789`
const CODE_ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
const ROOM_TTL_MS = 15 * 60 * 1000; // 15 minutes

interface SignalWaiter {
  resolve: (desc: unknown) => void;
  timer: NodeJS.Timeout;
}

interface RoomSession {
  code: string;
  secret: string;
  offer: unknown;
  answer: unknown | null;
  answerWaiters: Array<{ resolve: (ans: unknown) => void; timer: NodeJS.Timeout }>;
  signals: Map<string, unknown>;
  signalWaiters: Map<string, SignalWaiter[]>;
  createdAt: number;
  expiresAt: number;
}

const roomsByCode = new Map<string, RoomSession>();
const roomsBySecret = new Map<string, RoomSession>();

function generateRoomCode(): string {
  for (let attempt = 0; attempt < 50; attempt++) {
    let code = '';
    for (let i = 0; i < 4; i++) {
      const idx = crypto.randomInt(0, CODE_ALPHABET.length);
      code += CODE_ALPHABET[idx];
    }
    if (!roomsByCode.has(code)) {
      return code;
    }
  }
  return 'KRS2';
}

function cleanupExpiredRooms() {
  const now = Date.now();
  for (const [code, room] of roomsByCode.entries()) {
    if (now > room.expiresAt) {
      roomsByCode.delete(code);
      roomsBySecret.delete(room.secret);
    }
  }
}

setInterval(cleanupExpiredRooms, 60_000).unref();

// Default STUN/TURN fallback + live upstream ICE fetch
const FALLBACK_ICE = {
  iceServers: [
    {
      urls: [
        'stun:stun.cloudflare.com:3478',
        'stun:stun.l.google.com:19302',
      ],
    },
  ],
  relay: false,
};

async function getIceConfig() {
  try {
    const res = await fetch(`${UPSTREAM_BASE}/api/ice`, {
      signal: AbortSignal.timeout(3500),
    });
    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.iceServers)) {
        return data;
      }
    }
  } catch {
    // Fallback to STUN servers
  }
  return FALLBACK_ICE;
}

// Feature flags endpoint (`/api/flags`)
app.get('/api/flags', (_req: Request, res: Response) => {
  res.json({ support: true });
});

// ICE servers endpoint (`/api/ice`)
app.get('/api/ice', async (_req: Request, res: Response) => {
  const ice = await getIceConfig();
  res.json(ice);
});

// WebRTC Room & Signaling endpoint (`/api/room`)
app.all('/api/room', async (req: Request, res: Response) => {
  cleanupExpiredRooms();

  const action = typeof req.query.action === 'string' ? req.query.action : '';
  const codeParam = typeof req.query.code === 'string' ? req.query.code.toUpperCase().trim() : '';
  const secretParam = typeof req.query.secret === 'string' ? req.query.secret.trim() : '';
  const sidParam = typeof req.query.sid === 'string' ? req.query.sid.trim() : '';

  // 1. ICE Restart Signaling: /api/room?action=signal&sid=...&kind=offer|answer&n=1
  if (action === 'signal') {
    const room = roomsBySecret.get(sidParam);
    if (!room) {
      res.status(404).json({ error: 'Room session expired or not found.' });
      return;
    }
    room.expiresAt = Date.now() + ROOM_TTL_MS;
    const kind = typeof req.query.kind === 'string' ? req.query.kind : 'offer';
    const n = typeof req.query.n === 'string' ? req.query.n : '1';
    const key = `${kind}:${n}`;

    if (req.method === 'POST') {
      const desc = req.body?.desc;
      if (!desc) {
        res.status(400).json({ error: 'Missing signal description.' });
        return;
      }
      room.signals.set(key, desc);
      const waiters = room.signalWaiters.get(key);
      if (waiters && waiters.length > 0) {
        room.signalWaiters.delete(key);
        for (const w of waiters) {
          clearTimeout(w.timer);
          w.resolve(desc);
        }
      }
      res.json({ ok: true });
      return;
    }

    if (req.method === 'GET') {
      if (room.signals.has(key)) {
        res.json({ desc: room.signals.get(key) });
        return;
      }
      const waitSec = Math.min(30, Math.max(1, Number(req.query.wait) || 12));
      const desc = await new Promise<unknown>((resolve) => {
        const timer = setTimeout(() => resolve(null), waitSec * 1000);
        const list = room.signalWaiters.get(key) || [];
        list.push({ resolve, timer });
        room.signalWaiters.set(key, list);

        req.on('close', () => {
          clearTimeout(timer);
        });
      });
      res.json({ desc });
      return;
    }
  }

  // 2. Guest posts WebRTC answer: POST /api/room?code=XXXX&action=answer
  if (req.method === 'POST' && action === 'answer') {
    const room = roomsByCode.get(codeParam);
    if (!room) {
      res.status(404).json({ error: 'Room not found or expired.' });
      return;
    }
    const answer = req.body?.answer;
    if (!answer) {
      res.status(400).json({ error: 'Missing WebRTC answer.' });
      return;
    }
    room.answer = answer;
    room.expiresAt = Date.now() + ROOM_TTL_MS;

    const waiters = room.answerWaiters.splice(0, room.answerWaiters.length);
    for (const w of waiters) {
      clearTimeout(w.timer);
      w.resolve(answer);
    }

    res.json({ ok: true });
    return;
  }

  // 3. Host creates a room: POST /api/room
  if (req.method === 'POST' && !action) {
    const offer = req.body?.offer;
    if (!offer) {
      res.status(400).json({ error: 'Missing WebRTC offer.' });
      return;
    }
    const code = generateRoomCode();
    const secret = crypto.randomBytes(16).toString('hex');
    const now = Date.now();
    const room: RoomSession = {
      code,
      secret,
      offer,
      answer: null,
      answerWaiters: [],
      signals: new Map(),
      signalWaiters: new Map(),
      createdAt: now,
      expiresAt: now + ROOM_TTL_MS,
    };
    roomsByCode.set(code, room);
    roomsBySecret.set(secret, room);
    res.json({ code, secret });
    return;
  }

  // 4. Host polls for answer OR Guest joins room by code: GET /api/room
  if (req.method === 'GET') {
    const room = roomsByCode.get(codeParam);
    if (!room) {
      res.status(404).json({ error: 'Room code not found. Check the code and try again.' });
      return;
    }

    // Host long-polling with secret: GET /api/room?code=XXXX&secret=YYYY&wait=25
    if (secretParam) {
      if (room.secret !== secretParam) {
        res.status(403).json({ error: 'Invalid room secret.' });
        return;
      }
      if (room.answer) {
        res.json({ answer: room.answer });
        return;
      }
      const waitSec = Math.min(30, Math.max(1, Number(req.query.wait) || 25));
      const answer = await new Promise<unknown>((resolve) => {
        const timer = setTimeout(() => resolve(null), waitSec * 1000);
        room.answerWaiters.push({ resolve, timer });
        req.on('close', () => {
          clearTimeout(timer);
        });
      });
      res.json({ answer });
      return;
    }

    // Guest joining room: GET /api/room?code=XXXX
    const ice = await getIceConfig();
    res.json({
      offer: room.offer,
      ice,
    });
    return;
  }

  // 5. Host closes room after connection: DELETE /api/room?code=XXXX&secret=YYYY
  if (req.method === 'DELETE') {
    const room = roomsByCode.get(codeParam);
    if (room && (!secretParam || room.secret === secretParam)) {
      roomsByCode.delete(codeParam);
      // Keep roomsBySecret alive until TTL so WebRTC ICE restart (`sid`) continues to work during the match!
    }
    res.json({ ok: true });
    return;
  }

  res.status(405).json({ error: 'Method not allowed' });
});

// Serve all locally mirrored static files from /public
const publicDir = path.join(__dirname, 'public');
app.use(
  express.static(publicDir, {
    maxAge: '1h',
    setHeaders: (res, filePath) => {
      if (filePath.endsWith('.wasm')) {
        res.setHeader('Content-Type', 'application/wasm');
      } else if (filePath.endsWith('.glb')) {
        res.setHeader('Content-Type', 'model/gltf-binary');
      } else if (filePath.endsWith('.webmanifest')) {
        res.setHeader('Content-Type', 'application/manifest+json');
      }
    },
  })
);

// Transparent upstream proxy & local cache fallback for any dynamic asset path
app.get('*', async (req: Request, res: Response) => {
  const reqPath = req.path === '/' ? '/index.html' : req.path;
  const localFile = path.join(publicDir, reqPath);

  if (fs.existsSync(localFile) && fs.statSync(localFile).isFile()) {
    res.sendFile(localFile);
    return;
  }

  // If an asset wasn't found locally, fetch from upstream fightkaro.com and cache it locally
  try {
    const upstreamUrl = `${UPSTREAM_BASE}${req.originalUrl}`;
    const upstreamRes = await fetch(upstreamUrl);
    if (!upstreamRes.ok) {
      res.status(upstreamRes.status).end();
      return;
    }
    const contentType = upstreamRes.headers.get('content-type');
    if (contentType) {
      res.setHeader('Content-Type', contentType);
    }
    const buf = Buffer.from(await upstreamRes.arrayBuffer());
    try {
      fs.mkdirSync(path.dirname(localFile), { recursive: true });
      fs.writeFileSync(localFile, buf);
    } catch {
      // Ignore write error if path is invalid
    }
    res.send(buf);
  } catch {
    res.status(404).send('Not found');
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Sansad Showdown server running on http://0.0.0.0:${PORT}`);
});
