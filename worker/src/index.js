// Serves datalidy.com from the GitHub Pages build at amne51ac.github.io/datalidy.
// The site uses relative links, so it renders identically at the domain root.

const ORIGIN = "https://amne51ac.github.io/datalidy";
const CANONICAL_HOST = "datalidy.com";

const SECURITY_HEADERS = {
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Frame-Options": "SAMEORIGIN",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.hostname !== CANONICAL_HOST) {
      url.hostname = CANONICAL_HOST;
      return Response.redirect(url.toString(), 301);
    }
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
    }

    const upstream = await fetch(ORIGIN + url.pathname + url.search, {
      method: request.method,
      redirect: "manual",
      cf: { cacheEverything: true, cacheTtl: 300 },
    });

    const headers = new Headers(upstream.headers);
    const location = headers.get("Location");
    if (location) {
      headers.set("Location", location.replace(/^https?:\/\/amne51ac\.github\.io\/datalidy/, `https://${CANONICAL_HOST}`));
    }
    for (const [k, v] of Object.entries(SECURITY_HEADERS)) headers.set(k, v);
    headers.delete("x-github-request-id");
    headers.delete("via");

    return new Response(upstream.body, { status: upstream.status, statusText: upstream.statusText, headers });
  },
};
