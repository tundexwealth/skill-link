window.CONFIG = (() => {
    const configured = (window.__APP_CONFIG__ && window.__APP_CONFIG__.API_URL) || "";
    const host = (window.location.hostname || "").toLowerCase();
    const isLocalDevelopment = ["localhost", "127.0.0.1", "::1"].includes(host) || host.endsWith(".local");

    // Preferred: explicitly set API_URL in hosting/build config.
    // Fallback: same-origin on local dev, otherwise a production API domain.
    const apiUrl = configured || (isLocalDevelopment ? window.location.origin : "https://api.skilllink.example.com");

    return {
        API_URL: apiUrl
    };
})();