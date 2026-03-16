import { describe, expect, test, afterAll } from "bun:test";
import index from "./index.html";

const server = Bun.serve({
  port: 0,
  routes: {
    "/": index,
    "/api/health": new Response(JSON.stringify({ status: "ok" }), {
      headers: { "Content-Type": "application/json" },
    }),
    "/api/version": new Response(JSON.stringify({ version: "1.0.0" }), {
      headers: { "Content-Type": "application/json" },
    }),
  },
});

afterAll(() => {
  server.stop();
});

describe("Hello World server", () => {
  test("/ returns HTML with Hello World", async () => {
    const response = await fetch(`http://localhost:${server.port}`);
    const text = await response.text();
    expect(response.status).toBe(200);
    expect(text).toContain("Hello, World!");
  });

  test("/api/health returns ok", async () => {
    const response = await fetch(`http://localhost:${server.port}/api/health`);
    const json = await response.json();
    expect(response.status).toBe(200);
    expect(json).toEqual({ status: "ok" });
  });

  test("/api/version returns version 1.0.0", async () => {
    const response = await fetch(`http://localhost:${server.port}/api/version`);
    const json = await response.json();
    expect(response.status).toBe(200);
    expect(json).toEqual({ version: "1.0.0" });
  });
});
