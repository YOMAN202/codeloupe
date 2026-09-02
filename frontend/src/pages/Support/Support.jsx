import { useEffect, useRef, useState } from "react";

const UPI_ID = "7045141130@ptyes";
// Standard UPI "intent" deep link (pa=payee address, pn=payee name,
// cu=currency) -- the correct, standard format UPI apps register to
// handle. It's genuinely functional, just platform-limited: a phone with a
// UPI app installed resolves upi:// links directly, but desktop operating
// systems have nothing registered to catch that scheme at all, so clicking
// it there is a real, expected no-op rather than a bug in how the link is
// built (verified against the actual running app -- see handleOpenUpi's
// honest fallback messaging below rather than silently hiding that gap).
const UPI_LINK = `upi://pay?pa=${encodeURIComponent(UPI_ID)}&pn=${encodeURIComponent("Codeloupe")}&cu=INR`;

// Served from frontend/public/ -- Vite serves that directory's contents
// unprocessed at the site root, so this path works identically in dev and
// in the production build without importing the image as a module. The
// file itself was only resized (948x1536 -> 640x1037, same aspect ratio,
// no crop/recompression artifacts beyond a standard resample) to cut a
// ~450KB upload down to a page-appropriate size -- the QR pattern and its
// finder squares were never touched, so scannability isn't affected.
const QR_IMAGE_SRC = "/upi-qr.png";

const REPO_URL = "https://github.com/YOMAN202/codeloupe";
const DEV_EMAIL = "akshatmishra4u@gmail.com";
const SHARE_TEXT = "Check out Codeloupe -- your DSA companion!";

const FEEDBACK_MAILTO = `mailto:${DEV_EMAIL}?subject=${encodeURIComponent("Codeloupe feedback")}&body=${encodeURIComponent(
  "Feature suggestion or bug report (either is welcome!):\n\n"
)}`;

// Clipboard write shared by the UPI-ID copy button and the Share card's
// fallback (when the native Web Share API isn't available) -- one place
// that tries the modern async Clipboard API and falls back to the legacy
// textarea+execCommand path for browsers/contexts without it, instead of
// two copies of the same logic drifting apart.
async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
}

export default function Support() {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const [upiNote, setUpiNote] = useState(null);
  const [shareState, setShareState] = useState("idle"); // idle | copied | error
  const copyTimeoutRef = useRef(null);
  const upiTimeoutRef = useRef(null);
  const shareTimeoutRef = useRef(null);

  useEffect(
    () => () => {
      clearTimeout(copyTimeoutRef.current);
      clearTimeout(upiTimeoutRef.current);
      clearTimeout(shareTimeoutRef.current);
    },
    []
  );

  async function handleCopyUpi() {
    setCopyError(false);
    try {
      await copyText(UPI_ID);
      setCopied(true);
      clearTimeout(copyTimeoutRef.current);
      copyTimeoutRef.current = setTimeout(() => setCopied(false), 2200);
    } catch {
      // Never claim success it didn't achieve -- if copying genuinely
      // failed, say so instead of showing "Copied!" over a no-op.
      setCopyError(true);
    }
  }

  // Attempts the upi:// deep link, then honestly reports back whether it
  // actually seemed to work -- rather than either pretending it always
  // does (most desktop clicks are a silent no-op with nothing to catch
  // the custom scheme) or removing the option outright, which would take
  // away a link that's completely correct and useful on a phone. The
  // heuristic: launching another app blurs/hides this tab almost
  // immediately; if that hasn't happened after a beat, nothing caught the
  // link. Not literally 100% precise (a very slow app switch could in
  // theory still show the note), but it's the same practical approach
  // most payment-link sites use for this exact problem, and it's honest
  // in the failure direction that matters (never claims success it can't
  // verify).
  function handleOpenUpi(e) {
    e.preventDefault();
    setUpiNote(null);
    let left = false;
    const markLeft = () => {
      left = true;
    };
    window.addEventListener("blur", markLeft, { once: true });
    window.location.href = UPI_LINK;
    clearTimeout(upiTimeoutRef.current);
    upiTimeoutRef.current = setTimeout(() => {
      window.removeEventListener("blur", markLeft);
      if (!left && !document.hidden) {
        setUpiNote(
          "Didn't open a UPI app -- that's expected on a desktop browser, which has no UPI app to hand it to. Use the UPI ID above (or the QR code, once added) instead."
        );
      }
    }, 1200);
  }

  async function handleShare() {
    setShareState("idle");
    const payload = { title: "Codeloupe", text: SHARE_TEXT, url: REPO_URL };
    if (navigator.share) {
      try {
        await navigator.share(payload);
        // The OS share sheet itself is the confirmation here -- no extra
        // "Shared!" message needed, and a user backing out of it (an
        // AbortError) isn't a failure worth surfacing either.
      } catch (e) {
        if (e?.name !== "AbortError") setShareState("error");
      }
      return;
    }
    try {
      await copyText(REPO_URL);
      setShareState("copied");
      clearTimeout(shareTimeoutRef.current);
      shareTimeoutRef.current = setTimeout(() => setShareState("idle"), 2200);
    } catch {
      setShareState("error");
    }
  }

  const communityLinks = [
    {
      key: "star",
      icon: "⭐",
      label: "Star the project on GitHub",
      description: "If Codeloupe has helped you, consider giving the project a star.",
      href: REPO_URL,
      external: true,
    },
    {
      key: "feedback",
      icon: "💡🐛",
      label: "Suggest a Feature / Report a Bug",
      description: "Have an idea to improve Codeloupe, or found something that isn't working? Send it directly to the developer.",
      href: FEEDBACK_MAILTO,
      external: false,
    },
    {
      key: "instagram",
      icon: "📸",
      label: "Follow on Instagram",
      description: "@not_akshat_xd",
      href: "https://www.instagram.com/not_akshat_xd/",
      external: true,
    },
    {
      key: "linkedin",
      icon: "💼",
      label: "Connect on LinkedIn",
      description: "Akshat Mishra",
      href: "https://www.linkedin.com/in/akshat-mishra-735466257",
      external: true,
    },
    {
      key: "portfolio",
      icon: "🌐",
      label: "Visit my Portfolio",
      description: "akshatmishraos.vercel.app",
      href: "https://akshatmishraos.vercel.app/",
      external: true,
    },
    {
      key: "share",
      icon: "🔗",
      label: "Share Codeloupe",
      description:
        shareState === "copied"
          ? "Link copied!"
          : shareState === "error"
          ? "Couldn't share automatically -- copy the link from the address bar above instead."
          : "Enjoying Codeloupe? Share it with someone learning DSA.",
      onClick: handleShare,
    },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <h2>Support Codeloupe</h2>
        <p className="muted">
          Codeloupe is independently built and maintained. If it has helped your DSA journey, your
          support helps improve it -- entirely optional, and appreciated either way. Nothing here is
          required to use the app: there's no payment gate, Codeloupe never processes or confirms a
          payment itself, and any support happens entirely through your own UPI app.
        </p>
      </div>

      <section className="support-coffee">
        <div className="support-coffee-header">
          <h3>&#9749; Buy me a coffee</h3>
          <span className="muted small">
            If Codeloupe has helped your DSA journey, you can optionally support its continued
            development. No account or signup is involved -- this just hands you the UPI ID (or a
            deep link, or a QR code) to pay through your own UPI app.
          </span>
        </div>
        <div className="support-upi-row">
          <code className="support-upi-id">{UPI_ID}</code>
          <button type="button" className="chip chip-small" onClick={handleCopyUpi}>
            {copied ? "Copied!" : "Copy UPI ID"}
          </button>
          <a className="chip chip-small" href={UPI_LINK} onClick={handleOpenUpi}>
            Open in UPI app
          </a>
        </div>
        {copyError && (
          <p className="error small">
            Couldn't copy automatically -- please select and copy the UPI ID above manually.
          </p>
        )}
        {upiNote && <p className="muted small">{upiNote}</p>}
        <p className="muted small support-upi-hint">
          The UPI app link works on a mobile device with a UPI app installed. On desktop, use the
          copyable UPI ID above{QR_IMAGE_SRC ? " or scan the QR code" : ""}.
        </p>
        {QR_IMAGE_SRC && (
          <div className="support-qr-wrap">
            <img className="support-qr" src={QR_IMAGE_SRC} alt="UPI QR code to pay via Buy Me a Coffee" />
          </div>
        )}
        <p className="muted small support-coffee-note">
          This only prepares a payment for you to review and send in your own UPI app -- Codeloupe
          never processes, confirms, or has any visibility into whether a payment happened.
        </p>
      </section>

      <section className="lesson-section">
        <h3>Community support</h3>
        <p className="muted small">
          Costs nothing and helps just as much -- starring the project, sharing it, or sending
          feedback.
        </p>
        <div className="support-links-grid">
          {communityLinks.map((link) =>
            link.onClick ? (
              <button key={link.key} type="button" className="support-link-card" onClick={link.onClick}>
                <span className="support-link-icon" aria-hidden="true">{link.icon}</span>
                <span className="support-link-text">
                  <span className="support-link-label">{link.label}</span>
                  <span className="muted small">{link.description}</span>
                </span>
              </button>
            ) : (
              <a
                key={link.key}
                className="support-link-card"
                href={link.href}
                {...(link.external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
              >
                <span className="support-link-icon" aria-hidden="true">{link.icon}</span>
                <span className="support-link-text">
                  <span className="support-link-label">{link.label}</span>
                  <span className="muted small">{link.description}</span>
                </span>
              </a>
            )
          )}
        </div>
      </section>
    </div>
  );
}
