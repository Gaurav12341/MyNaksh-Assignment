import React, { useState } from "react";
import {
  Bug,
  Database,
  Eye,
  EyeOff,
  Gem,
  Layers,
  Palette,
  RefreshCw,
  Send,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Wand2,
} from "lucide-react";
import { createRoot } from "react-dom/client";

import { getCached, setCached } from "./cache";
import { createCheckout, getLogs, getUsers, login, postDebug, postPersonalize, register } from "./api";
import "./styles.css";

const STYLE_GALLERY = [
  { name: "Astral Ink", tone: "high contrast", color: "#22d3ee", colorTwo: "#0f766e" },
  { name: "Neon Yantra", tone: "ritual geometry", color: "#ec4899", colorTwo: "#7c3aed" },
  { name: "Solar Grain", tone: "warm halftone", color: "#f59e0b", colorTwo: "#e11d48" },
  { name: "Moon Glass", tone: "soft refraction", color: "#a78bfa", colorTwo: "#38bdf8" },
];

const CREATOR_TOOLS = [
  { icon: Database, title: "Context Router", text: "Fetch mock or Mongo-backed profile, kundli, horoscope, and panchang data." },
  { icon: SlidersHorizontal, title: "Personalization Engine", text: "Detect intent, select only relevant context, and tune tone, language, and length." },
  { icon: Layers, title: "Prompt Optimizer", text: "Send compact selected context to the active LLM provider." },
  { icon: ShieldCheck, title: "RBAC Console", text: "Admin can inspect any user; normal users stay scoped to their own profile." },
];

function getStoredSession() {
  const raw = localStorage.getItem("mynaksh:session");
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch {
    localStorage.removeItem("mynaksh:token");
    localStorage.removeItem("mynaksh:session");
    return null;
  }
}

function App() {
  const [session, setSession] = useState(getStoredSession);
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState({
    usernameOrEmail: "",
    password: "",
    name: "",
    username: "",
    email: "",
    subscription: "free",
    billingPeriod: "monthly",
  });
  const [users, setUsers] = useState([]);
  const [showPassword, setShowPassword] = useState(false);
  const [userId, setUserId] = useState("user_101");
  const [question, setQuestion] = useState("Should I consider changing my job in the next few months?");
  const [answer, setAnswer] = useState(null);
  const [debug, setDebug] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState("");
  const [useCache, setUseCache] = useState(true);
  const [dataSource, setDataSource] = useState("mock");
  const [llmProvider, setLlmProvider] = useState("mock");
  const [llmModel, setLlmModel] = useState("openai/gpt-oss-120b");
  const [selectedStyle, setSelectedStyle] = useState(STYLE_GALLERY[0]);
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [featurePanelMode, setFeaturePanelMode] = useState("features");

  const payload = {
    userId,
    question,
    dataSource,
    llmProvider,
    llmModel: llmProvider === "openrouter" ? llmModel : undefined,
  };

  async function submitAuth(event) {
    event.preventDefault();
    setError("");
    try {
      const data =
        authMode === "login"
          ? await login({ usernameOrEmail: authForm.usernameOrEmail, password: authForm.password })
          : await register({
              name: authForm.name,
              username: authForm.username,
              email: authForm.email,
              password: authForm.password,
              subscription: authForm.subscription,
              billingPeriod: authForm.subscription === "premium" ? authForm.billingPeriod : null,
            });
      localStorage.setItem("mynaksh:token", data.token);
      localStorage.setItem("mynaksh:session", JSON.stringify(data.user));
      setSession(data.user);
      setUserId(data.user.role === "admin" ? "user_101" : data.user.id);
      if (data.user.role === "admin") await loadUsers();
      if (authMode === "register" && authForm.subscription === "premium") {
        const checkout = await createCheckout({ billingPeriod: authForm.billingPeriod });
        if (checkout.provider === "stripe") window.location.href = checkout.checkoutUrl;
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadUsers() {
    const data = await getUsers();
    setUsers(data);
  }

  function logout() {
    localStorage.removeItem("mynaksh:token");
    localStorage.removeItem("mynaksh:session");
    localStorage.removeItem("mynaksh:lastSelectedUser");
    setSession(null);
    setUsers([]);
    setAnswer(null);
    setDebug(null);
    setError("");
    window.history.replaceState(null, "", "/");
  }

  async function startCheckout() {
    setError("");
    try {
      const data = await createCheckout({ billingPeriod: authForm.billingPeriod });
      if (data.provider === "mock") {
        const updated = { ...session, subscription: "premium", billingPeriod: authForm.billingPeriod };
        localStorage.setItem("mynaksh:session", JSON.stringify(updated));
        setSession(updated);
        return;
      }
      window.location.href = data.checkoutUrl;
    } catch (err) {
      setError(err.message);
    }
  }

  React.useEffect(() => {
    if (session?.role === "admin") {
      loadUsers().catch((err) => setError(err.message));
    }
  }, [session?.role]);

  async function runPersonalize(forceRefresh = false) {
    setError("");
    setLoading("answer");
    try {
      const cached = !forceRefresh && useCache ? getCached("personalize", payload) : null;
      if (cached) {
        setAnswer({ ...cached.value, fromCache: true });
        return;
      }
      const data = await postPersonalize(payload);
      setCached("personalize", payload, data);
      setAnswer({ ...data, fromCache: false });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function runDebug(forceRefresh = false) {
    setError("");
    setLoading("debug");
    try {
      const cached = !forceRefresh && useCache ? getCached("debug", payload) : null;
      if (cached) {
        setDebug({ ...cached.value, fromCache: true });
        return;
      }
      const data = await postDebug(payload);
      setCached("debug", payload, data);
      setDebug({ ...data, fromCache: false });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function refreshLogs() {
    if (session?.role !== "admin") return;
    setLogsLoading(true);
    setError("");
    try {
      const data = await getLogs(120);
      setLogs(data.lines || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLogsLoading(false);
    }
  }

  const pageStyle = {
    "--accent": selectedStyle.color,
    "--accent-two": selectedStyle.colorTwo,
  };

  if (!session) {
    return (
      <main className="page artPage" style={pageStyle}>
        <Scribbles />
        <nav className="topNav">
          <div className="brandMark">
            <Sparkles size={18} />
            <span>MyNaksh Studio</span>
          </div>
          <div className="navPills">
            <span>Generate</span>
            <span>Debug</span>
            <span>Ground</span>
          </div>
        </nav>

        <section className="landingHero">
          <div className="heroCopy">
            <p className="eyebrow">AI context engine for personalized guidance</p>
            <h1>Build grounded prompts from astrological context.</h1>
            <p className="heroText">
              Fetch user, kundli, horoscope, and panchang data; select only relevant sources; tune tone and length; then generate a structured response.
            </p>
            <div className="heroStats">
              <span><strong>10</strong> seeded profiles</span>
              <span><strong>4</strong> context services</span>
              <span><strong>1</strong> optimized prompt</span>
            </div>
          </div>

          <div className="previewCard heroPreview" aria-label="Nakshatra constellation preview">
            <div className="previewToolbar">
              <span>Nakshatra canvas</span>
              <span>{selectedStyle.name}</span>
            </div>
            <ConstellationPreview selectedStyle={selectedStyle} />
            <div className="previewPrompt">
              <Wand2 size={16} />
              <span>{selectedStyle.name} constellation style maps the selected prompt mood.</span>
            </div>
            <LivePromptDemo />
          </div>

          <AuthPanel
            authMode={authMode}
            setAuthMode={setAuthMode}
            authForm={authForm}
            setAuthForm={setAuthForm}
            showPassword={showPassword}
            setShowPassword={setShowPassword}
            submitAuth={submitAuth}
            error={error}
          />
        </section>

        <section className="landingBand">
          <StyleGallery styles={STYLE_GALLERY} selectedStyle={selectedStyle} onSelect={setSelectedStyle} />
          <CreatorTools tools={CREATOR_TOOLS} />
        </section>
      </main>
    );
  }

  return (
    <main className="page artPage" style={pageStyle}>
      <Scribbles />
      <section className="workspace">
        <div className="header">
          <div>
            <p className="eyebrow">Creator console</p>
            <h1>MyNaksh Context Studio</h1>
            <p>Generate grounded answers from selected context, inspect personalization decisions, and keep LLM prompts intentionally compact.</p>
          </div>
          <div className="sessionBox">
            <strong>{session.name}</strong>
            <span>{session.role} · {session.subscription}</span>
            <button className="secondary" onClick={logout}>Logout</button>
          </div>
        </div>

        <section className="studioHero">
          <div className="previewCard">
            <div className="previewToolbar">
              <span>Nakshatra constellation preview</span>
              <span>{selectedStyle.name}</span>
            </div>
            <ConstellationPreview selectedStyle={selectedStyle} />
            <div className="previewPrompt">
              <Wand2 size={16} />
              <span>{question}</span>
            </div>
            <LivePromptDemo />
          </div>
          <div className="showcaseStack">
            <StyleGallery styles={STYLE_GALLERY} selectedStyle={selectedStyle} onSelect={setSelectedStyle} compact />
            <FeatureLogPanel
              tools={CREATOR_TOOLS}
              isAdmin={session.role === "admin"}
              mode={featurePanelMode}
              onModeChange={setFeaturePanelMode}
              logs={logs}
              loading={logsLoading}
              onRefresh={refreshLogs}
            />
          </div>
        </section>

        <div className="formGrid">
          <label>
            User ID
            {session.role === "admin" ? (
              <select value={userId} onChange={(event) => setUserId(event.target.value)}>
                {users.map((user) => (
                  <option value={user.id} key={user.guid}>{user.name} ({user.id})</option>
                ))}
              </select>
            ) : (
              <input value={userId} disabled />
            )}
          </label>
          <label>
            Data source
            <select value={dataSource} onChange={(event) => setDataSource(event.target.value)}>
              <option value="mock">Mock data</option>
              <option value="mongodb">MongoDB data</option>
            </select>
          </label>
          <label>
            LLM provider
            <select value={llmProvider} onChange={(event) => setLlmProvider(event.target.value)}>
              <option value="mock">Mock LLM</option>
              <option value="openrouter">OpenRouter</option>
              <option value="lmstudio" disabled>LM Studio - coming soon</option>
              <option value="openai_compatible" disabled>OpenAI-compatible - coming soon</option>
            </select>
          </label>
          <label>
            Model
            <input
              value={llmModel}
              onChange={(event) => setLlmModel(event.target.value)}
              disabled={llmProvider === "mock"}
              placeholder="openai/gpt-oss-120b"
            />
          </label>
          <label>
            Prompt
            <textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={4} />
          </label>
        </div>

        <div className="actions">
          <button onClick={() => runPersonalize(false)} disabled={loading !== ""}>
            <Send size={16} />
            Generate
          </button>
          <button onClick={() => runDebug(false)} disabled={loading !== ""}>
            <Bug size={16} />
            Debug
          </button>
          <button className="secondary" onClick={() => Promise.all([runPersonalize(true), runDebug(true)])} disabled={loading !== ""}>
            <RefreshCw size={16} />
            Refresh
          </button>
          <label className="cacheToggle">
            <input type="checkbox" checked={useCache} onChange={(event) => setUseCache(event.target.checked)} />
            Browser cache
          </label>
          {session.subscription !== "premium" && (
            <>
              <select className="inlineSelect" value={authForm.billingPeriod} onChange={(event) => setAuthForm({ ...authForm, billingPeriod: event.target.value })}>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
              <button className="secondary" onClick={startCheckout}>Upgrade</button>
            </>
          )}
        </div>

        {error && <div className="error">{error}</div>}

        <div className="results">
          <section className="panel">
            <h2>Generation Output</h2>
            {loading === "answer" && <GeneratingTrace />}
            {answer ? (
              <>
                <p className="answer">{answer.answer}</p>
                <div className="meta">
                  <span>Confidence: {answer.confidence}</span>
                  {answer.fromCache && <span>Cached</span>}
                </div>
                <SourceList sources={answer.sourcesUsed} />
              </>
            ) : (
              <p className="muted">No answer yet.</p>
            )}
          </section>

          <section className="panel">
            <h2>Debug Plan</h2>
            {loading === "debug" && <p className="muted">Analyzing...</p>}
            {debug ? (
              <div className="debugGrid">
                <KeyValue label="Intent" value={debug.intent} />
                <KeyValue label="Data source" value={dataSource} />
                <KeyValue label="LLM provider" value={llmProvider} />
                <KeyValue label="Language" value={debug.language} />
                <KeyValue label="Tone" value={debug.tone} />
                <KeyValue label="Max words" value={debug.maxWords} />
                <KeyValue label="Confidence" value={debug.confidence} />
                {debug.fromCache && <KeyValue label="Cache" value="Browser" />}
                <SourceList title="Selected" sources={debug.selectedContext} />
                <SourceList title="Excluded" sources={debug.excludedContext} />
                <SourceList title="Failed services" sources={debug.failedSources} />
              </div>
            ) : (
              <p className="muted">No debug output yet.</p>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}

function AuthPanel({ authMode, setAuthMode, authForm, setAuthForm, showPassword, setShowPassword, submitAuth, error }) {
  return (
    <section className="authShell">
      <div className="authHeader">
        <h2>{authMode === "login" ? "Enter Studio" : "Create Studio Pass"}</h2>
        <p>Sign in to access the personalization workspace.</p>
      </div>
      <div className="tabs">
        <button className={authMode === "login" ? "" : "secondary"} onClick={() => setAuthMode("login")}>Login</button>
        <button className={authMode === "register" ? "" : "secondary"} onClick={() => setAuthMode("register")}>Register</button>
      </div>
      <form className="authForm" onSubmit={submitAuth}>
        {authMode === "register" && (
          <>
            <label>Name<input value={authForm.name} onChange={(event) => setAuthForm({ ...authForm, name: event.target.value })} /></label>
            <label>Username<input value={authForm.username} onChange={(event) => setAuthForm({ ...authForm, username: event.target.value })} /></label>
            <label>Email<input value={authForm.email} onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })} /></label>
          </>
        )}
        {authMode === "login" && (
          <label>Username or email<input value={authForm.usernameOrEmail} onChange={(event) => setAuthForm({ ...authForm, usernameOrEmail: event.target.value })} /></label>
        )}
        <label>
          Password
          <span className="passwordField">
            <input
              type={showPassword ? "text" : "password"}
              value={authForm.password}
              onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
            />
            <button
              type="button"
              className="iconButton"
              aria-label={showPassword ? "Hide password" : "Show password"}
              title={showPassword ? "Hide password" : "Show password"}
              onClick={() => setShowPassword((value) => !value)}
            >
              {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </span>
        </label>
        {authMode === "register" && (
          <>
            <label>
              Subscription
              <select value={authForm.subscription} onChange={(event) => setAuthForm({ ...authForm, subscription: event.target.value })}>
                <option value="free">Free</option>
                <option value="premium">Premium</option>
              </select>
            </label>
            {authForm.subscription === "premium" && (
              <label>
                Billing
                <select value={authForm.billingPeriod} onChange={(event) => setAuthForm({ ...authForm, billingPeriod: event.target.value })}>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </label>
            )}
          </>
        )}
        <button type="submit"><ShieldCheck size={16} />{authMode === "login" ? "Login" : "Create Account"}</button>
      </form>
      {error && <div className="error">{error}</div>}
    </section>
  );
}

function KeyValue({ label, value }) {
  return (
    <div className="keyValue">
      <span>{label}</span>
      <strong>{String(value)}</strong>
    </div>
  );
}

function SourceList({ title = "Sources", sources = [] }) {
  return (
    <div className="sourceBlock">
      <h3>{title}</h3>
      {sources.length ? (
        <div className="chips">
          {sources.map((source) => (
            <span className="chip" key={source}>
              {source}
            </span>
          ))}
        </div>
      ) : (
        <p className="muted small">None</p>
      )}
    </div>
  );
}

function GeneratingTrace() {
  return (
    <div className="generatingTrace" aria-label="Generating response">
      <div className="traceHeader">
        <span className="tracePulse" />
        <strong>Generating grounded response</strong>
      </div>
      <div className="traceSteps">
        <span>Detecting intent</span>
        <span>Selecting context</span>
        <span>Building compact prompt</span>
        <span>Streaming answer</span>
      </div>
      <div className="traceLines">
        <i />
        <i />
        <i />
      </div>
    </div>
  );
}

function ConstellationPreview({ selectedStyle }) {
  const stars = [
    [70, 270],
    [142, 330],
    [210, 176],
    [302, 126],
    [370, 210],
    [392, 250],
    [484, 180],
    [560, 300],
    [648, 196],
    [700, 132],
  ];

  return (
    <div className="generatedCanvas">
      <svg className="constellationSvg" viewBox="0 0 760 420" role="img" aria-label="Nakshatra constellation preview">
        <path className="astroPath pathOne" d="M70 270 C150 130 280 110 370 210 S560 300 700 132" />
        <path className="astroPath pathTwo" d="M98 120 C240 220 348 70 484 180 S610 360 720 260" />
        <path className="astroPath pathThree" d="M142 330 C250 272 298 324 392 250 S544 96 648 196" />
        {stars.map(([cx, cy], index) => (
          <g key={`${cx}-${cy}`}>
            <circle className="starHalo" cx={cx} cy={cy} r={index % 3 === 0 ? 18 : 12} />
            <circle className="starPoint" cx={cx} cy={cy} r={index % 3 === 0 ? 4.5 : 3.4} />
          </g>
        ))}
        <text x="42" y="58">Rohini</text>
        <text x="590" y="374">Siddhi Yoga</text>
      </svg>
      <div className="nakshatraBadge">
        <Sparkles size={17} />
        <span>{selectedStyle.name}</span>
      </div>
      <div className="canvasGrid" />
    </div>
  );
}

function LivePromptDemo() {
  return (
    <div className="liveDemo" aria-label="Looping prompt response preview">
      <div className="liveDemoHeader">
        <span>Live prompt trace</span>
        <span>looping demo</span>
      </div>
      <div className="liveTimeline">
        <div className="sampleRun runOne">
          <p className="sampleQuestion">Should I consider changing my job this year?</p>
          <p className="sampleStatus">Selecting Career Horoscope, 10th House, Current Dasha...</p>
          <p className="sampleAnswer">Focus on networking and compare opportunities carefully before making a move.</p>
        </div>
        <div className="sampleRun runTwo">
          <p className="sampleQuestion">How does this month look for my relationship?</p>
          <p className="sampleStatus">Selecting 7th House, Relationship Horoscope, Moon Sign...</p>
          <p className="sampleAnswer">Prioritize patient communication and give emotional clarity room to build.</p>
        </div>
        <div className="sampleRun runThree">
          <p className="sampleQuestion">What should I focus on for my health?</p>
          <p className="sampleStatus">Selecting 6th House, Health Horoscope, Panchang...</p>
          <p className="sampleAnswer">Keep the guidance practical: steady rest, consistent meals, and lower stress.</p>
        </div>
        <div className="sampleRun runFour">
          <p className="sampleQuestion">Can you summarize today's guidance?</p>
          <p className="sampleStatus">Selecting Panchang, General Horoscope, Moon Sign...</p>
          <p className="sampleAnswer">Use the day for reflection, planning, and one clear priority.</p>
        </div>
      </div>
    </div>
  );
}

function CreatorTools({ tools }) {
  return (
    <section className="featurePanel">
      <div className="sectionTitle">
        <Gem size={17} />
        <h2>Core Features</h2>
      </div>
      <div className="toolGrid">
        {tools.map((tool) => {
          const Icon = tool.icon;
          return (
            <article className="toolCard" key={tool.title}>
              <Icon size={18} />
              <strong>{tool.title}</strong>
              <p>{tool.text}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function StyleGallery({ styles, selectedStyle, onSelect, compact = false }) {
  return (
    <section className={compact ? "miniSection" : "featurePanel"}>
      <div className="sectionTitle">
        <Palette size={17} />
        <h2>Style Gallery</h2>
      </div>
      <div className="styleGrid">
        {styles.map((style) => (
          <button
            className={`styleTile ${selectedStyle.name === style.name ? "active" : ""}`}
            key={style.name}
            onClick={() => onSelect(style)}
            type="button"
          >
            <span className="styleSwatch" style={{ "--accent": style.color, "--accent-two": style.colorTwo }} />
            <strong>{style.name}</strong>
            <small>{style.tone}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

function FeatureLogPanel({ tools, isAdmin, mode, onModeChange, logs, loading, onRefresh }) {
  const showingLogs = isAdmin && mode === "logs";

  return (
    <section className="miniSection featureLogPanel">
      <div className="sectionTitle featureLogHeader">
        <div className="titleCluster">
          {showingLogs ? <Database size={17} /> : <Gem size={17} />}
          <h2>{showingLogs ? "Live Logs" : "Core Features"}</h2>
        </div>
        {isAdmin && (
          <div className="featureHeaderActions">
            <div className="segmentedToggle" aria-label="Feature panel mode">
              <button className={mode === "features" ? "active" : ""} onClick={() => onModeChange("features")} type="button">
                Core Features
              </button>
              <button className={mode === "logs" ? "active" : ""} onClick={() => onModeChange("logs")} type="button">
                Logs
              </button>
            </div>
          </div>
        )}
      </div>

      {showingLogs ? (
        <>
          <pre className="logConsole">
            {logs.length ? logs.join("\n") : "No log lines loaded. Click Refresh to pull the latest backend logs."}
          </pre>
          <div className="logFooter">
            <button className="secondary logRefreshButton" onClick={onRefresh} disabled={loading}>
              <RefreshCw size={14} />
              {loading ? "Loading" : "Refresh"}
            </button>
          </div>
        </>
      ) : (
        <div className="toolGrid">
          {tools.map((tool) => {
            const Icon = tool.icon;
            return (
              <article className="toolCard" key={tool.title}>
                <Icon size={18} />
                <strong>{tool.title}</strong>
                <p>{tool.text}</p>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function Scribbles() {
  return (
    <div className="astralScribbles" aria-hidden="true">
      <svg className="scribbleLeft" viewBox="0 0 260 720">
        <path d="M34 92 C108 24 182 66 124 148 S38 292 148 332 S228 474 86 604" />
        <circle cx="126" cy="150" r="4" />
        <circle cx="148" cy="332" r="5" />
        <circle cx="86" cy="604" r="3" />
      </svg>
      <svg className="scribbleRight" viewBox="0 0 260 720">
        <path d="M220 74 C116 128 226 214 132 294 S64 446 188 512 S120 650 54 684" />
        <circle cx="132" cy="294" r="4" />
        <circle cx="188" cy="512" r="5" />
        <circle cx="54" cy="684" r="3" />
      </svg>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
