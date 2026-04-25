const express = require("express");
const { createClient } = require("redis");

const app = express();
const PORT = 3000;
const TTL = parseInt(process.env.CACHE_TTL || "30", 10);

const redis = createClient({ url: process.env.REDIS_URL || "redis://localhost:6379" });
redis.on("error", (err) => console.error("Redis error:", err));

async function fetchData() {
  // Simulate an expensive operation (e.g., DB query, external API)
  await new Promise((r) => setTimeout(r, 500));
  return { message: "Hello from the data source", timestamp: new Date().toISOString() };
}

app.get("/health", (req, res) => res.json({ status: "ok" }));

app.get("/data", async (req, res) => {
  const key = "cached:data";
  const cached = await redis.get(key);

  if (cached) {
    return res.json({ source: "cache", data: JSON.parse(cached) });
  }

  const data = await fetchData();
  await redis.setEx(key, TTL, JSON.stringify(data));
  res.json({ source: "origin", data });
});

app.delete("/cache/flush", async (req, res) => {
  await redis.flushDb();
  res.json({ message: "Cache flushed" });
});

(async () => {
  await redis.connect();
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
})();
