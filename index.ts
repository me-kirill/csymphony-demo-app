import index from "./index.html";

const server = Bun.serve({
  port: 3000,
  routes: {
    "/": index,
    "/api/health": new Response(JSON.stringify({ status: "ok" }), {
      headers: { "Content-Type": "application/json" },
    }),
  },
  development: {
    hmr: true,
    console: true,
  },
});

console.log(`Server running at http://localhost:${server.port}`);
