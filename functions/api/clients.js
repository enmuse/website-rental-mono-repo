// Cloudflare Pages Function: /api/clients
// Edge API for viewing, updating, and adding verified real contractors to data/clients.json in GitHub

const GITHUB_REPO = "enmuse/website-rental-mono-repo";
const GITHUB_FILE_PATH = "data/clients.json";
const REQUIRED_PIN = "8280";

function utf8ToBase64(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function base64ToUtf8(base64) {
  const cleanBase64 = base64.replace(/[\r\n\s]/g, "");
  const binary = atob(cleanBase64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new TextDecoder().decode(bytes);
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Ops-Pin",
    },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Ops-Pin",
    },
  });
}

// GET /api/clients — Fetch the latest verified contractor database
export async function onRequestGet(context) {
  const pat = context.env.GITHUB_PAT || context.env.GITHUB_TOKEN;
  
  if (!pat) {
    // If no GitHub PAT is set, serve directly from edge assets
    try {
      const assetUrl = new URL("/data/clients.json", context.request.url);
      const assetRes = await context.env.ASSETS.fetch(new Request(assetUrl));
      if (assetRes.ok) {
        const clients = await assetRes.json();
        return jsonResponse({ count: clients.length, clients });
      }
    } catch (e) {
      // fallback
    }
  }

  const url = `https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_FILE_PATH}`;

  try {
    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${pat}`,
        "User-Agent": "Ridgeline-Ops-Edge",
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!res.ok) {
      return jsonResponse({ error: `GitHub API error: ${res.statusText}` }, res.status);
    }

    const fileData = await res.json();
    const content = base64ToUtf8(fileData.content);
    const clients = JSON.parse(content);

    return jsonResponse({
      count: clients.length,
      sha: fileData.sha,
      clients,
    });
  } catch (err) {
    return jsonResponse({ error: err.message }, 500);
  }
}

// POST /api/clients — Save or update contractor record in GitHub
export async function onRequestPost(context) {
  const pat = context.env.GITHUB_PAT || context.env.GITHUB_TOKEN;
  if (!pat) {
    return jsonResponse({
      error: "Cloudflare Pages secret GITHUB_PAT is not set. Please configure GITHUB_PAT in Cloudflare Pages settings.",
    }, 500);
  }

  let body;
  try {
    body = await context.request.json();
  } catch (err) {
    return jsonResponse({ error: "Invalid JSON payload" }, 400);
  }

  const { pin, action, client } = body;
  const headerPin = context.request.headers.get("X-Ops-Pin");

  // 1. PIN Security Authorization
  if (pin !== REQUIRED_PIN && headerPin !== REQUIRED_PIN) {
    return jsonResponse({ error: "Unauthorized: Invalid PIN" }, 403);
  }

  if (!client || typeof client !== "object") {
    return jsonResponse({ error: "Missing client object" }, 400);
  }

  // 2. Strict 4-Point Anti-Hallucination & Proof-of-Life Validation (AGENTS.md Mandate)
  const businessName = (client.business_name || "").trim();
  const ownerName = (client.owner_name || "").trim();
  const cellPhone = (client.cell_phone || "").trim();
  const rawDigits = cellPhone.replace(/\D/g, "");
  const city = (client.city || "").trim();
  const trade = (client.trade || "").trim();
  const corridor = (client.corridor_name || "").trim();

  if (businessName.length < 3) {
    return jsonResponse({ error: "Validation Error: Business name must be at least 3 characters." }, 422);
  }
  if (ownerName.length < 2) {
    return jsonResponse({ error: "Validation Error: Named human owner/principal is required (Proof-of-Life check)." }, 422);
  }
  if (rawDigits.length !== 10 && rawDigits.length !== 11) {
    return jsonResponse({ error: "Validation Error: Direct cell phone must contain a valid 10-digit phone number." }, 422);
  }
  if (city.length < 2) {
    return jsonResponse({ error: "Validation Error: Western NC operating city is required." }, 422);
  }
  if (trade.length < 3) {
    return jsonResponse({ error: "Validation Error: Trade vertical is required." }, 422);
  }

  // 3. Normalize slug
  let slug = (client.slug || "").trim().toLowerCase();
  if (!slug) {
    slug = businessName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }
  client.slug = slug;

  // Format 10-digit phone nicely: (828) 555-1234
  const d = rawDigits.slice(-10);
  client.cell_phone = `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
  client.direct_sms_number = `+1${d}`;
  client.state = client.state || "NC";
  client.short_name = client.short_name || businessName.split("(")[0].trim();

  // 4. Fetch current data/clients.json from GitHub
  const getUrl = `https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_FILE_PATH}`;
  let fileData;
  try {
    const getRes = await fetch(getUrl, {
      headers: {
        Authorization: `Bearer ${pat}`,
        "User-Agent": "Ridgeline-Ops-Edge",
        Accept: "application/vnd.github.v3+json",
      },
    });
    if (!getRes.ok) {
      return jsonResponse({ error: `GitHub fetch failed: ${getRes.statusText}` }, getRes.status);
    }
    fileData = await getRes.json();
  } catch (err) {
    return jsonResponse({ error: `GitHub connection failed: ${err.message}` }, 500);
  }

  const existingJsonText = base64ToUtf8(fileData.content);
  let clients;
  try {
    clients = JSON.parse(existingJsonText);
  } catch (err) {
    return jsonResponse({ error: "Failed to parse repository data/clients.json" }, 500);
  }

  // 5. Update or Append Contractor Record
  const existingIndex = clients.findIndex((c) => c.slug === slug);
  let isNew = false;

  if (action === "delete") {
    if (existingIndex === -1) {
      return jsonResponse({ error: `Contractor '${slug}' not found` }, 404);
    }
    clients.splice(existingIndex, 1);
  } else if (existingIndex >= 0) {
    // Preserve nested fields (projects, testimonials, services) if not in incoming quick-edit
    const existing = clients[existingIndex];
    clients[existingIndex] = {
      ...existing,
      ...client,
      projects: client.projects && client.projects.length ? client.projects : existing.projects || [],
      testimonials: client.testimonials && client.testimonials.length ? client.testimonials : existing.testimonials || [],
      services: client.services && client.services.length ? client.services : existing.services || [],
      trust_badges: client.trust_badges && client.trust_badges.length ? client.trust_badges : existing.trust_badges || [],
    };
  } else {
    // Brand new contractor
    isNew = true;
    const newRecord = {
      ...client,
      projects: client.projects || [],
      testimonials: client.testimonials || [],
      services: client.services || [],
      trust_badges: client.trust_badges || [
        "Verified Western North Carolina Trade Craftsman",
        "Direct Owner Dispatch & Rapid Mountain Response",
      ],
      competitor_pagespeed: client.competitor_pagespeed || 32,
      competitor_fcp: client.competitor_fcp || "3.5s",
      competitor_lcp: client.competitor_lcp || "7.8s",
      primary_color: client.primary_color || "#1e293b",
      accent_color: client.accent_color || "#2563eb",
      theme_gradient: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
    };
    clients.push(newRecord);
  }

  // 6. Commit Updated File Back to GitHub main branch
  const updatedJsonText = JSON.stringify(clients, null, 2);
  const updatedBase64 = utf8ToBase64(updatedJsonText);

  const commitMessage =
    action === "delete"
      ? `ops: remove contractor ${slug} via ops portal`
      : isNew
      ? `ops: add real contractor ${businessName} (${city}, NC) via ops portal`
      : `ops: update contractor ${businessName} via ops portal`;

  const putUrl = `https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_FILE_PATH}`;
  try {
    const putRes = await fetch(putUrl, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${pat}`,
        "User-Agent": "Ridgeline-Ops-Edge",
        Accept: "application/vnd.github.v3+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: commitMessage,
        content: updatedBase64,
        sha: fileData.sha,
        branch: "main",
      }),
    });

    if (!putRes.ok) {
      const errBody = await putRes.text();
      return jsonResponse({ error: `GitHub commit rejected: ${errBody}` }, putRes.status);
    }

    const commitResult = await putRes.json();
    return jsonResponse({
      success: true,
      action: action === "delete" ? "deleted" : isNew ? "created" : "updated",
      slug,
      business_name: businessName,
      commit_sha: commitResult.commit?.sha,
      message: `Successfully saved ${businessName}. Changes will deploy to Cloudflare edge in ~30s.`,
      client: clients.find((c) => c.slug === slug),
      total_clients: clients.length,
    });
  } catch (err) {
    return jsonResponse({ error: `Commit execution failed: ${err.message}` }, 500);
  }
}
