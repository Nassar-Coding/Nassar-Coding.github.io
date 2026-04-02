import { useState, useEffect, useRef } from "react";

const C = {
  bg: "#080c14",
  bgAlt: "#0d1320",
  card: "#0f1724",
  cardHover: "#131d2e",
  green: "#2d9c6f",
  greenGlow: "rgba(45,156,111,0.12)",
  greenBorder: "rgba(45,156,111,0.25)",
  greenBright: "#3dbd84",
  gold: "#c8a84e",
  text: "#dfe6ed",
  textMuted: "#8b98a8",
  textDim: "#5a6776",
  white: "#f0f4f8",
  border: "#172033",
  borderLight: "#1e2d45",
};

const ff = `'Outfit', sans-serif`;
const mono = `'JetBrains Mono', monospace`;

function useInView(t = 0.12) {
  const r = useRef(null);
  const [v, setV] = useState(false);
  useEffect(() => {
    const el = r.current;
    if (!el) return;
    const o = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setV(true); o.unobserve(el); } }, { threshold: t });
    o.observe(el);
    return () => o.disconnect();
  }, [t]);
  return [r, v];
}

function Fade({ children, delay = 0, style = {} }) {
  const [r, v] = useInView();
  return (<div ref={r} style={{ opacity: v ? 1 : 0, transform: v ? "translateY(0)" : "translateY(28px)", transition: `opacity 0.75s cubic-bezier(.22,1,.36,1) ${delay}s, transform 0.75s cubic-bezier(.22,1,.36,1) ${delay}s`, ...style }}>{children}</div>);
}

function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);
  const links = ["About", "Experience", "Projects", "Skills", "Contact"];
  return (
    <>
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 200,
        background: scrolled ? "rgba(8,12,20,0.95)" : "transparent",
        backdropFilter: scrolled ? "blur(16px)" : "none",
        borderBottom: scrolled ? `1px solid ${C.border}` : "1px solid transparent",
        transition: "all 0.4s ease", padding: "18px 36px",
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <span style={{ fontFamily: ff, fontWeight: 700, fontSize: 17, color: C.white, letterSpacing: 0.5 }}>
          NASSAR<span style={{ color: C.green }}>.</span>
        </span>
        <div className="nav-links" style={{ display: "flex", gap: 32 }}>
          {links.map(l => (
            <a key={l} href={`#${l.toLowerCase()}`}
              style={{ fontFamily: mono, fontSize: 12, color: C.textDim, textDecoration: "none", transition: "color 0.25s", letterSpacing: 0.8, textTransform: "uppercase" }}
              onMouseEnter={e => e.target.style.color = C.green}
              onMouseLeave={e => e.target.style.color = C.textDim}>
              {l}
            </a>
          ))}
        </div>
        <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)} style={{
          display: "none", background: "none", border: "none", cursor: "pointer", padding: 8,
          flexDirection: "column", gap: 5, alignItems: "center",
        }}>
          <span style={{ display: "block", width: 22, height: 2, background: C.textMuted, borderRadius: 2, transition: "all 0.3s", transform: menuOpen ? "rotate(45deg) translate(3.5px, 3.5px)" : "none" }} />
          <span style={{ display: "block", width: 22, height: 2, background: C.textMuted, borderRadius: 2, transition: "all 0.3s", opacity: menuOpen ? 0 : 1 }} />
          <span style={{ display: "block", width: 22, height: 2, background: C.textMuted, borderRadius: 2, transition: "all 0.3s", transform: menuOpen ? "rotate(-45deg) translate(3.5px, -3.5px)" : "none" }} />
        </button>
      </nav>
      <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0, zIndex: 190,
        background: "rgba(8,12,20,0.97)", backdropFilter: "blur(20px)",
        display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 36,
        opacity: menuOpen ? 1 : 0, pointerEvents: menuOpen ? "all" : "none",
        transition: "opacity 0.35s ease",
      }}>
        {links.map((l, i) => (
          <a key={l} href={`#${l.toLowerCase()}`} onClick={() => setMenuOpen(false)}
            style={{ fontFamily: ff, fontSize: 28, fontWeight: 600, color: C.white, textDecoration: "none", opacity: menuOpen ? 1 : 0, transform: menuOpen ? "translateY(0)" : "translateY(20px)", transition: `all 0.4s ease ${i * 0.06}s` }}>
            <span style={{ color: C.green, fontFamily: mono, fontSize: 14, marginRight: 12 }}>0{i + 1}</span>{l}
          </a>
        ))}
      </div>
    </>
  );
}

function Hero() {
  const [loaded, setLoaded] = useState(false);
  useEffect(() => { setTimeout(() => setLoaded(true), 150); }, []);
  return (
    <section style={{ minHeight: "100vh", display: "flex", alignItems: "center", padding: "0 36px", position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
        <div style={{ position: "absolute", top: "-20%", right: "-10%", width: 700, height: 700, borderRadius: "50%", background: `radial-gradient(circle, rgba(45,156,111,0.06) 0%, transparent 70%)` }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: `radial-gradient(circle at 1px 1px, rgba(45,156,111,0.04) 1px, transparent 0)`, backgroundSize: "52px 52px" }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 120px, rgba(45,156,111,0.015) 120px, rgba(45,156,111,0.015) 121px)` }} />
        <div style={{ position: "absolute", top: "15%", bottom: "15%", right: "38%", width: 1, background: `linear-gradient(to bottom, transparent, ${C.greenBorder}, transparent)`, opacity: 0.4 }} />
      </div>
      <div style={{ maxWidth: 900, margin: "0 auto", width: "100%", position: "relative" }}>
        <div style={{ opacity: loaded ? 1 : 0, transform: loaded ? "translateY(0)" : "translateY(36px)", transition: "all 1s cubic-bezier(.22,1,.36,1)" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 16px", borderRadius: 20, background: C.greenGlow, border: `1px solid ${C.greenBorder}`, marginBottom: 28 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.green, boxShadow: `0 0 8px ${C.green}` }} />
            <span style={{ fontFamily: mono, fontSize: 11, color: C.green, letterSpacing: 1.2, textTransform: "uppercase" }}>Available for Opportunities</span>
          </div>
          <h1 style={{ fontFamily: ff, fontSize: 58, fontWeight: 800, color: C.white, margin: "0 0 20px 0", lineHeight: 1.08, letterSpacing: -1 }}>
            Building AI Systems<br />for <span style={{ color: C.green }}>Real-World</span><br />Operations
          </h1>
          <p style={{ fontFamily: ff, fontSize: 18, color: C.textMuted, maxWidth: 540, lineHeight: 1.7, margin: "0 0 20px 0" }}>
            AI-driven command centers. Operational intelligence at national scale. Digital twin platforms for critical infrastructure.
          </p>
          <p style={{ fontFamily: mono, fontSize: 13, color: C.textDim, letterSpacing: 0.5, margin: "0 0 36px 0" }}>
            Nassar Naif Alsharif — Makkah, Saudi Arabia
          </p>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
            <a href="#experience" style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "13px 28px", borderRadius: 8, background: C.green, color: "#fff", fontFamily: ff, fontWeight: 600, fontSize: 14, textDecoration: "none", transition: "all 0.3s", boxShadow: `0 0 20px rgba(45,156,111,0.2)` }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = `0 0 32px rgba(45,156,111,0.35)`; e.currentTarget.style.transform = "translateY(-2px)"; }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = `0 0 20px rgba(45,156,111,0.2)`; e.currentTarget.style.transform = "translateY(0)"; }}>
              View Experience
            </a>
            <a href="#contact" style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "13px 28px", borderRadius: 8, border: `1px solid ${C.borderLight}`, color: C.text, fontFamily: ff, fontWeight: 600, fontSize: 14, textDecoration: "none", transition: "all 0.3s" }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = C.green; e.currentTarget.style.color = C.green; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = C.borderLight; e.currentTarget.style.color = C.text; }}>
              Contact Me
            </a>
          </div>
        </div>
        <div style={{ position: "absolute", top: "50%", right: -40, transform: "translateY(-50%)", width: 200, opacity: loaded ? 0.25 : 0, transition: "opacity 1.5s ease 0.5s", pointerEvents: "none" }}>
          {[0, 1, 2, 3, 4].map(i => (
            <div key={i} style={{ height: 2, borderRadius: 1, marginBottom: 14, background: `linear-gradient(to right, ${C.green}, transparent)`, width: `${100 - i * 18}%`, opacity: 0.5 + i * 0.1 }} />
          ))}
          <div style={{ fontFamily: mono, fontSize: 9, color: C.textDim, marginTop: 8, letterSpacing: 2 }}>SYS.OPERATIONAL</div>
        </div>
      </div>
    </section>
  );
}

function Sec({ id, children, alt = false }) {
  return (
    <section id={id} style={{ padding: "110px 36px", background: alt ? C.bgAlt : "transparent", position: "relative" }}>
      <div style={{ maxWidth: 900, margin: "0 auto" }}>{children}</div>
    </section>
  );
}

function SecTitle({ num, title, sub }) {
  return (
    <Fade>
      <div style={{ marginBottom: 56 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
          <span style={{ fontFamily: mono, fontSize: 12, color: C.green, letterSpacing: 1.5 }}>{num}</span>
          <span style={{ width: 32, height: 1, background: C.green, opacity: 0.5 }} />
        </div>
        <h2 style={{ fontFamily: ff, fontSize: 34, fontWeight: 700, color: C.white, margin: 0, lineHeight: 1.15, letterSpacing: -0.5 }}>{title}</h2>
        {sub && <p style={{ fontFamily: ff, fontSize: 15, color: C.textDim, marginTop: 10, lineHeight: 1.6 }}>{sub}</p>}
      </div>
    </Fade>
  );
}

function About() {
  const metrics = [
    { value: "M.Sc. AI", label: "University of Technology Sydney", sub: "WAM 82.44 · GPA 6.13" },
    { value: "B.Eng.", label: "Computer Engineering", sub: "Umm Al-Qura University" },
    { value: "National Scale", label: "AI Co-Innovation Program", sub: "Aramco · IBM · CNTXT" },
    { value: "Operations", label: "Two Holy Mosques", sub: "Command Center · Digital Twin" },
  ];
  return (
    <Sec id="about" alt>
      <SecTitle num="01" title="Profile" sub="AI engineer and operational intelligence specialist working at the intersection of technology and critical infrastructure." />
      <div className="about-grid" style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 48, alignItems: "start" }}>
        <Fade delay={0.1}>
          <div>
            <p style={{ fontFamily: ff, fontSize: 15, color: C.text, lineHeight: 1.85, margin: "0 0 16px 0" }}>
              I hold a Master's in Artificial Intelligence from the University of Technology Sydney and a Bachelor's in Computer Engineering from Umm Al-Qura University. My work sits at the intersection of AI, data operations, and large-scale infrastructure systems.
            </p>
            <p style={{ fontFamily: ff, fontSize: 15, color: C.textMuted, lineHeight: 1.85, margin: "0 0 16px 0" }}>
              Currently, I'm part of the operations team at Ascend Solutions, working directly on AI-driven command centers, digital twin platforms, and operational intelligence systems deployed for the General Authority for the Care of the Two Holy Mosques — bridging client operations with data and digital engineering teams to ensure systems deliver at scale.
            </p>
            <p style={{ fontFamily: ff, fontSize: 15, color: C.textMuted, lineHeight: 1.85, margin: 0 }}>
              I was selected for Saudi Arabia's AI Co-Innovation Program, where I built production-grade AI pipelines with Aramco, IBM, and CNTXT — from clustering algorithms for subsurface characterization to production APIs with full MLOps workflows.
            </p>
          </div>
        </Fade>
        <Fade delay={0.25}>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {metrics.map((m, i) => (
              <div key={i} style={{ padding: "18px 22px", borderRadius: 10, background: C.card, border: `1px solid ${C.border}`, borderLeft: `3px solid ${i === 3 ? C.green : C.border}`, transition: "border-color 0.3s" }}>
                <div style={{ fontFamily: ff, fontSize: 15, fontWeight: 700, color: i === 3 ? C.green : C.white }}>{m.value}</div>
                <div style={{ fontFamily: ff, fontSize: 13, color: C.textMuted, marginTop: 2 }}>{m.label}</div>
                <div style={{ fontFamily: mono, fontSize: 11, color: C.textDim, marginTop: 2 }}>{m.sub}</div>
              </div>
            ))}
          </div>
        </Fade>
      </div>
    </Sec>
  );
}

function Experience() {
  const jobs = [
    {
      title: "Project Specialist — Operations", company: "Ascend Solutions", meta: "Makkah, Saudi Arabia · 2025 – Present", highlight: true,
      scope: "AI-driven command centers · Digital twin platforms · Operational intelligence",
      points: [
        "Embedded within a national-scale program delivering AI-driven command centers, digital twin platforms, and operational intelligence systems for the General Authority for the Care of the Two Holy Mosques.",
        "Primary bridge between client operations stakeholders and data/digital engineering teams — translating operational requirements into technical specifications, dashboards, and system configurations.",
        "Driving KPI digitization across 34 operational assets, converting manually tracked metrics into Power BI dashboards with defined data sources, ownership, and automated refresh pipelines.",
        "Supporting the rollout of an AI-powered automated ticketing system — defining ticket trigger thresholds, mapping SOPs per asset, and conducting user acceptance testing with the operations team.",
        "Contributing to the digital twin platform initiative from the operations side — validating asset data, providing operational context, and connecting live dashboard feeds to the twin layer.",
      ],
    },
    {
      title: "AI Research Engineer", company: "Saudi AI Co-Innovation Program (RDI & Aramco)", meta: "Saudi Arabia · Jul – Oct 2025", highlight: false,
      scope: "Seismic AI · MLOps · Production deployment",
      points: [
        "Built an AI clustering pipeline transforming seismic data into hierarchical facies maps — enabling coarse-to-fine subsurface characterization with deterministic reproducibility.",
        "Designed a three-tier validation framework (statistical tests, cluster quality, spatial continuity) ensuring geological credibility across multiple basins.",
        "Delivered a production-ready API and interactive 3D visualization dashboard with automated reporting and enterprise-scale deployment via GPU-accelerated cloud infrastructure.",
        "Reduced geological interpretation time significantly by automating clustering and validation workflows — accelerating exploration decision-making.",
      ],
    },
    {
      title: "Content & Review Specialist", company: "CJEL Imaging Technology Education Solution", meta: "Sydney, Australia · Feb 2024 – Feb 2025", highlight: false,
      scope: "AI/ML educational content",
      points: ["Developed and reviewed technical educational content covering machine learning, data science, and applied AI for diverse audiences."],
    },
  ];
  return (
    <Sec id="experience">
      <SecTitle num="02" title="Experience" sub="From national-scale command centers to production AI systems." />
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {jobs.map((job, i) => (
          <Fade key={i} delay={i * 0.1}>
            <div style={{ padding: "30px 32px", borderRadius: 12, background: job.highlight ? C.card : "transparent", border: `1px solid ${job.highlight ? C.greenBorder : C.border}`, position: "relative", transition: "border-color 0.3s" }}>
              {job.highlight && <div style={{ position: "absolute", top: 16, right: 20, fontFamily: mono, fontSize: 10, color: C.green, letterSpacing: 1.5, textTransform: "uppercase", padding: "3px 10px", background: C.greenGlow, borderRadius: 4, border: `1px solid ${C.greenBorder}` }}>Current</div>}
              <h3 style={{ fontFamily: ff, fontSize: 18, fontWeight: 700, color: C.white, margin: 0 }}>{job.title}</h3>
              <p style={{ fontFamily: ff, fontSize: 14, color: job.highlight ? C.green : C.textMuted, margin: "4px 0 0 0" }}>{job.company}</p>
              <p style={{ fontFamily: mono, fontSize: 11, color: C.textDim, margin: "4px 0 0 0", letterSpacing: 0.5 }}>{job.meta}</p>
              <div style={{ fontFamily: mono, fontSize: 11, color: C.textDim, marginTop: 8, paddingTop: 8, borderTop: `1px solid ${C.border}`, letterSpacing: 0.3 }}>{job.scope}</div>
              <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 8 }}>
                {job.points.map((p, j) => (
                  <div key={j} style={{ display: "flex", gap: 10 }}>
                    <span style={{ color: C.green, fontSize: 8, marginTop: 7, flexShrink: 0 }}>●</span>
                    <p style={{ fontFamily: ff, fontSize: 13.5, color: C.textMuted, lineHeight: 1.7, margin: 0 }}>{p}</p>
                  </div>
                ))}
              </div>
            </div>
          </Fade>
        ))}
      </div>
    </Sec>
  );
}

function Projects() {
  const projects = [
    { featured: true, title: "Forecasting Natural Disasters", type: "Research — University of Technology Sydney",
      challenge: "Early disaster detection systems struggle with low accuracy and slow response times, especially across rare event categories with severe class imbalance.",
      solution: "Developed and benchmarked LSTM networks against traditional ML models (SVM, Random Forest, XGBoost). Applied Gaussian noise augmentation to overcome imbalance and improve robustness across all disaster categories.",
      result: "92% detection accuracy with 20% faster response time over baseline.", tags: ["Python", "TensorFlow", "Scikit-learn", "Pandas"] },
    { featured: false, title: "Drowsee — Real-Time Drowsiness Detection", type: "Capstone — University of Technology Sydney",
      challenge: "Driver drowsiness contributes to a significant share of road accidents. Existing detection systems suffer from high latency in real-world conditions.",
      solution: "Built a real-time computer vision pipeline from data augmentation through model optimization, with end-to-end experiment tracking via ClearML for full reproducibility.",
      result: "95% accuracy · 30% latency reduction.", tags: ["Python", "TensorFlow", "OpenCV", "ClearML"] },
    { featured: false, title: "Autonomous Navigation with RL", type: "Research — University of Technology Sydney",
      challenge: "RL-based autonomous driving agents face inefficient exploration and poor transfer from simulation to resource-constrained edge hardware.",
      solution: "Compared DDQN and TQC agents with optimized autoencoder state representations. Explored reward shaping and sim-to-real strategies for generalization.",
      result: "30% navigation efficiency improvement.", tags: ["PyTorch", "Stable-Baselines3", "OpenAI Gym"] },
  ];
  return (
    <Sec id="projects" alt>
      <SecTitle num="03" title="Projects" sub="Applied research in deep learning, computer vision, and reinforcement learning." />
      <Fade delay={0.1}>
        <div style={{ padding: 36, borderRadius: 14, background: C.card, border: `1px solid ${C.greenBorder}`, marginBottom: 20, position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: 0, right: 0, width: 200, height: 200, background: `radial-gradient(circle at top right, ${C.greenGlow}, transparent 70%)`, pointerEvents: "none" }} />
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <span style={{ fontFamily: mono, fontSize: 10, color: C.green, letterSpacing: 1.5, textTransform: "uppercase", padding: "3px 10px", background: C.greenGlow, borderRadius: 4, border: `1px solid ${C.greenBorder}` }}>Featured</span>
          </div>
          <h3 style={{ fontFamily: ff, fontSize: 22, fontWeight: 700, color: C.white, margin: "0 0 4px 0" }}>{projects[0].title}</h3>
          <p style={{ fontFamily: mono, fontSize: 12, color: C.textDim, margin: "0 0 24px 0" }}>{projects[0].type}</p>
          <div className="project-cols" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24 }}>
            {[{ label: "Challenge", text: projects[0].challenge }, { label: "Solution", text: projects[0].solution }, { label: "Result", text: projects[0].result }].map((col, i) => (
              <div key={i}>
                <p style={{ fontFamily: mono, fontSize: 10, color: C.green, letterSpacing: 1.5, textTransform: "uppercase", margin: "0 0 8px 0" }}>{col.label}</p>
                <p style={{ fontFamily: ff, fontSize: 13.5, color: i === 2 ? C.white : C.textMuted, lineHeight: 1.7, margin: 0, fontWeight: i === 2 ? 600 : 400 }}>{col.text}</p>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 20, display: "flex", gap: 6, flexWrap: "wrap" }}>
            {projects[0].tags.map(t => (<span key={t} style={{ fontFamily: mono, fontSize: 11, padding: "4px 12px", borderRadius: 4, background: C.greenGlow, color: C.green, border: `1px solid ${C.greenBorder}` }}>{t}</span>))}
          </div>
        </div>
      </Fade>
      <div className="projects-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {projects.slice(1).map((p, i) => (
          <Fade key={i} delay={0.15 + i * 0.1}>
            <div style={{ padding: 28, borderRadius: 12, background: C.card, border: `1px solid ${C.border}`, height: "100%", display: "flex", flexDirection: "column", transition: "border-color 0.3s" }}
              onMouseEnter={e => e.currentTarget.style.borderColor = C.greenBorder}
              onMouseLeave={e => e.currentTarget.style.borderColor = C.border}>
              <h3 style={{ fontFamily: ff, fontSize: 17, fontWeight: 700, color: C.white, margin: "0 0 4px 0" }}>{p.title}</h3>
              <p style={{ fontFamily: mono, fontSize: 11, color: C.textDim, margin: "0 0 16px 0" }}>{p.type}</p>
              <div style={{ marginBottom: 12 }}>
                <p style={{ fontFamily: mono, fontSize: 10, color: C.green, letterSpacing: 1, textTransform: "uppercase", margin: "0 0 4px 0" }}>Challenge</p>
                <p style={{ fontFamily: ff, fontSize: 13, color: C.textMuted, lineHeight: 1.7, margin: 0 }}>{p.challenge}</p>
              </div>
              <div style={{ marginBottom: 12 }}>
                <p style={{ fontFamily: mono, fontSize: 10, color: C.green, letterSpacing: 1, textTransform: "uppercase", margin: "0 0 4px 0" }}>Solution</p>
                <p style={{ fontFamily: ff, fontSize: 13, color: C.textMuted, lineHeight: 1.7, margin: 0 }}>{p.solution}</p>
              </div>
              <div style={{ marginBottom: 16 }}>
                <p style={{ fontFamily: mono, fontSize: 10, color: C.green, letterSpacing: 1, textTransform: "uppercase", margin: "0 0 4px 0" }}>Result</p>
                <p style={{ fontFamily: ff, fontSize: 14, color: C.white, fontWeight: 600, margin: 0 }}>{p.result}</p>
              </div>
              <div style={{ marginTop: "auto", display: "flex", gap: 6, flexWrap: "wrap" }}>
                {p.tags.map(t => (<span key={t} style={{ fontFamily: mono, fontSize: 11, padding: "3px 10px", borderRadius: 4, background: "rgba(255,255,255,0.03)", color: C.textDim, border: `1px solid ${C.border}` }}>{t}</span>))}
              </div>
            </div>
          </Fade>
        ))}
      </div>
    </Sec>
  );
}

function Skills() {
  const groups = [
    { title: "AI & Machine Learning", items: ["PyTorch", "TensorFlow", "Scikit-learn", "Hugging Face", "Stable-Baselines3", "Deep Learning", "Reinforcement Learning", "Computer Vision", "NLP", "LLM Fine-Tuning"], highlight: false },
    { title: "Operations & Systems", items: ["Command Center Operations", "Operational Intelligence", "AI Decision Systems", "KPI Frameworks", "Digital Twin Support", "Power BI", "Data Visualization"], highlight: true },
    { title: "Engineering & Deployment", items: ["Python", "C++", "JavaScript", "SQL", "Docker", "FastAPI", "ClearML", "GPU Computing", "Cloud Deployment", "Git", "Linux"], highlight: false },
  ];
  return (
    <Sec id="skills">
      <SecTitle num="04" title="Capabilities" sub="Across AI research, operational systems, and production engineering." />
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {groups.map((g, i) => (
          <Fade key={i} delay={i * 0.1}>
            <div style={{ padding: "24px 28px", borderRadius: 12, background: g.highlight ? C.card : "transparent", border: `1px solid ${g.highlight ? C.greenBorder : C.border}` }}>
              <h4 style={{ fontFamily: mono, fontSize: 11, color: g.highlight ? C.green : C.textDim, margin: "0 0 16px 0", letterSpacing: 1.5, textTransform: "uppercase" }}>{g.title}</h4>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {g.items.map(item => (
                  <span key={item} style={{ fontFamily: ff, fontSize: 13, color: C.text, padding: "6px 14px", borderRadius: 6, background: "rgba(255,255,255,0.03)", border: `1px solid ${C.border}`, transition: "all 0.25s", cursor: "default" }}
                    onMouseEnter={e => { e.target.style.borderColor = C.greenBorder; e.target.style.color = C.green; }}
                    onMouseLeave={e => { e.target.style.borderColor = C.border; e.target.style.color = C.text; }}>
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </Fade>
        ))}
      </div>
      <Fade delay={0.3}>
        <div style={{ marginTop: 36, padding: "20px 28px", borderRadius: 10, border: `1px solid ${C.border}` }}>
          <h4 style={{ fontFamily: mono, fontSize: 11, color: C.textDim, margin: "0 0 12px 0", letterSpacing: 1.5, textTransform: "uppercase" }}>Certifications</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {["Applied AI Bootcamp — CNTXT Academy & RDI (LLMs, RAG, MLOps, FastAPI, Docker)", "Data Classification & Summarization Using IBM Granite — IBM", "IELTS Academic — Overall Band Score 6.5"].map((c, i) => (
              <p key={i} style={{ fontFamily: ff, fontSize: 13, color: C.textMuted, margin: 0, lineHeight: 1.6, paddingLeft: 16, borderLeft: `2px solid ${i === 0 ? C.green : C.border}` }}>{c}</p>
            ))}
          </div>
        </div>
      </Fade>
    </Sec>
  );
}

function Contact() {
  const links = [
    { label: "Email", value: "Nassaralsharif0@gmail.com", href: "mailto:Nassaralsharif0@gmail.com", icon: "✉" },
    { label: "LinkedIn", value: "nassar-alsharif", href: "https://linkedin.com/in/nassar-alsharif", icon: "in" },
    { label: "GitHub", value: "Nassar1414", href: "https://github.com/Nassar1414", icon: "⌨" },
  ];
  return (
    <Sec id="contact" alt>
      <SecTitle num="05" title="Get in Touch" sub="Open to opportunities in AI engineering, operational intelligence, and strategic digital transformation." />
      <Fade delay={0.1}>
        <div className="contact-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
          {links.map((l, i) => (
            <a key={i} href={l.href} target="_blank" rel="noopener noreferrer" style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "28px 20px", borderRadius: 12, background: C.card, border: `1px solid ${C.border}`, textDecoration: "none", transition: "all 0.3s" }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = C.green; e.currentTarget.style.boxShadow = `0 0 24px ${C.greenGlow}`; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.boxShadow = "none"; }}>
              <span style={{ fontSize: 18, marginBottom: 10, opacity: 0.6 }}>{l.icon}</span>
              <span style={{ fontFamily: mono, fontSize: 10, color: C.textDim, letterSpacing: 1.2, textTransform: "uppercase", marginBottom: 6 }}>{l.label}</span>
              <span style={{ fontFamily: ff, fontSize: 14, color: C.green }}>{l.value}</span>
            </a>
          ))}
        </div>
        <p style={{ fontFamily: mono, fontSize: 12, color: C.textDim, textAlign: "center", marginTop: 24, letterSpacing: 0.5 }}>+966 597 980 913 · Makkah, Saudi Arabia</p>
      </Fade>
    </Sec>
  );
}

export default function Portfolio() {
  return (
    <div style={{ background: C.bg, minHeight: "100vh", color: C.text }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body { background: ${C.bg}; }
        ::selection { background: ${C.green}; color: #fff; }
        @media (max-width: 820px) {
          h1 { font-size: 36px !important; }
          h2 { font-size: 26px !important; }
          section { padding: 70px 20px !important; }
          .nav-links { display: none !important; }
          .mobile-menu-btn { display: flex !important; }
          .about-grid { grid-template-columns: 1fr !important; }
          .project-cols { grid-template-columns: 1fr !important; }
          .projects-grid { grid-template-columns: 1fr !important; }
          .contact-grid { grid-template-columns: 1fr !important; }
        }
        @media (min-width: 821px) {
          .mobile-menu-btn { display: none !important; }
        }
      `}</style>
      <Nav />
      <Hero />
      <About />
      <Experience />
      <Projects />
      <Skills />
      <Contact />
      <footer style={{ textAlign: "center", padding: "28px 24px", borderTop: `1px solid ${C.border}` }}>
        <p style={{ fontFamily: mono, fontSize: 11, color: C.textDim, letterSpacing: 0.8 }}>© 2026 Nassar Naif Alsharif · Makkah, Saudi Arabia</p>
      </footer>
    </div>
  );
}
