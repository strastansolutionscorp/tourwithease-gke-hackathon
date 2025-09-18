import compression from "compression";
import cors from "cors";
import express from "express";
import "express-async-errors";
import rateLimit from "express-rate-limit";
import helmet from "helmet";
import { createServer } from "http";
import { Server as SocketIOServer } from "socket.io";
import { initializeAgents } from "./agents/manager";
import { authMiddleware } from "./middleware/auth";
import { errorHandler } from "./middleware/errorHandler";
import agentsRoutes from "./routes/agents";
import chatRoutes from "./routes/chat";
import { logger } from "./utils/logger";
import { connectRedis } from "./utils/redis";
import { setupWebSocket } from "./websocket/handler";

const app = express();
const server = createServer(app);
const io = new SocketIOServer(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"],
  },
});

// Security middleware
app.use(helmet());
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: "Too many requests from this IP",
});

app.use(limiter);

// CORS
app.use(
  cors({
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    credentials: true,
  })
);

// Body parsing
app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true }));

// Logging middleware
app.use((req: any, res: any, next: any) => {
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get("User-Agent"),
  });
  next();
});

app.get("/health", (req: any, res: any) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// Routes
app.use("/api/chat", authMiddleware, chatRoutes);
app.use("/api/agents", authMiddleware, agentsRoutes);

// WebSocket setup
setupWebSocket(io);

// Error handling
app.use(errorHandler);

// 404 handler
app.use("*", (req: any, res: any) => {
  res.status(404).json({ error: "Route not found" });
});

const PORT = process.env.PORT || 8000;

async function startServer() {
  try {
    // Initialize Redis connection
    await connectRedis();

    logger.info("Redis connected successfully");

    // Initialize AI agents
    await initializeAgents();

    logger.info("AI agents initialized successfully");

    server.listen(PORT, () => {
      logger.info(`🚀 Server running on port ${PORT}`);
      logger.info(`📊 Health check: http://localhost:${PORT}/health`);
      logger.info(`🤖 API Gateway ready for ADK agents`);
    });
  } catch (error) {
    logger.error("Failed to start server:", error);
    process.exit(1);
  }
}

startServer();

// Graceful shutdown
process.on("SIGTERM", () => {
  logger.info("SIGTERM received, shutting down gracefully");
  server.close(() => {
    logger.info("Process terminated");
    process.exit(0);
  });
});
