const MAX_ITEMS = 10;

export function getCached(kind, payload) {
  const key = makeKey(kind, payload);
  const raw = localStorage.getItem(key);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(key);
    return null;
  }
}

export function setCached(kind, payload, value) {
  const key = makeKey(kind, payload);
  localStorage.setItem(key, JSON.stringify({ value, cachedAt: new Date().toISOString() }));
  trimCache(kind);
}

function makeKey(kind, payload) {
  const dataSource = payload.dataSource || "mock";
  const llmProvider = payload.llmProvider || "default";
  const llmModel = payload.llmModel || "default";
  return `mynaksh:${kind}:${dataSource}:${llmProvider}:${llmModel}:${payload.userId}:${payload.question.trim().toLowerCase()}`;
}

function trimCache(kind) {
  const prefix = `mynaksh:${kind}:`;
  const items = [];
  for (let index = 0; index < localStorage.length; index += 1) {
    const key = localStorage.key(index);
    if (key?.startsWith(prefix)) {
      const raw = localStorage.getItem(key);
      try {
        items.push({ key, cachedAt: JSON.parse(raw).cachedAt || "" });
      } catch {
        localStorage.removeItem(key);
      }
    }
  }
  items
    .sort((a, b) => b.cachedAt.localeCompare(a.cachedAt))
    .slice(MAX_ITEMS)
    .forEach((item) => localStorage.removeItem(item.key));
}
