import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import WebSocket from 'ws';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const CORE_WS_URL = process.env.CORE_WS_URL || 'ws://core:8000/ws/agent';

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('message', (payload) => {
    console.log('Proxying request to core:', payload);

    const coreWs = new WebSocket(CORE_WS_URL);

    coreWs.on('open', () => {
      coreWs.send(JSON.stringify(payload));
    });

    coreWs.on('message', (data) => {
      const event = JSON.parse(data.toString());
      socket.emit(event.type, event);
    });

    coreWs.on('error', (err) => {
      console.error('Core WebSocket error:', err);
      socket.emit('error', { content: 'Failed to connect to AI core' });
    });

    coreWs.on('close', () => {
      console.log('Core connection closed');
    });

    socket.on('disconnect', () => {
      if (coreWs.readyState === WebSocket.OPEN) {
        coreWs.close();
      }
    });
  });
});

const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`Gateway listening on port ${PORT}`);
});
