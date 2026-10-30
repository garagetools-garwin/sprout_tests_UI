"""
Замер скорости sprout-store.ru (прод) и new.sprout-store.ru (будущий прод) напрямую и через прокси.

Две метрики:
  * curl  — сетевой уровень для HTML главной: DNS, TCP, TLS, TTFB, total (PERF_RUNS*2 повторов);
  * browser (Playwright, холодный кэш на каждый прогон) — TTFB, DOMContentLoaded, load, LCP,
    время до networkidle, число запросов и объем.
Результат — медианы, печатаются в лог и в Job Summary.

Basic Auth превью для new.* добавляется заголовком через context.route только для его origin
(http_credentials в Chromium не работает вместе с прокси с авторизацией). Для прода ставится
такой же no-op route, чтобы накладные расходы перехвата были одинаковыми.
"""
import base64
import os
import statistics
import subprocess
import time
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

try:  # локальный запуск: подхватываем PREVIEW_*/PROXY_* из .env проекта
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SITES = {
    "prod sprout-store.ru": "https://sprout-store.ru",
    "new.sprout-store.ru": "https://new.sprout-store.ru",
}
PAGES = ["/", "/login"]
RUNS = int(os.getenv("PERF_RUNS") or "5")
NAV_TIMEOUT_MS = 90_000

PREVIEW_USER = os.getenv("PREVIEW_USER")
PREVIEW_PASS = os.getenv("PREVIEW_PASS")
PROXY_HOST, PROXY_PORT = os.getenv("PROXY_HOST"), os.getenv("PROXY_PORT")
PROXY_USER, PROXY_PASS = os.getenv("PROXY_USER"), os.getenv("PROXY_PASS")

# PERF_NO_PROXY=1 — только прямой режим (например, при локальном запуске из РФ)
MODES = {"direct": None}
if PROXY_HOST and not os.getenv("PERF_NO_PROXY"):
    MODES["proxy (RU)"] = {
        "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
        "username": PROXY_USER,
        "password": PROXY_PASS,
    }


def needs_auth(base: str) -> bool:
    return "new.sprout-store" in base and bool(PREVIEW_USER)


def med(values):
    values = [v for v in values if v is not None]
    return round(statistics.median(values)) if values else None


def curl_runs(base: str, proxy):
    cmd = [
        "curl", "-s", "-o", os.devnull, "--max-time", "60",
        "-w", "%{time_namelookup} %{time_connect} %{time_appconnect} "
              "%{time_starttransfer} %{time_total} %{http_code}",
    ]
    if needs_auth(base):
        cmd += ["-u", f"{PREVIEW_USER}:{PREVIEW_PASS}"]
    if proxy:
        cmd += ["-x", proxy["server"], "--proxy-user", f"{proxy['username']}:{proxy['password']}"]
    cmd.append(base + "/")
    rows, errors = [], 0
    for _ in range(RUNS * 2):
        out = subprocess.run(cmd, capture_output=True, text=True).stdout.split()
        if len(out) != 6 or not out[5].startswith(("2", "3")):
            errors += 1
            continue
        dns, tcp, tls, ttfb, total = (float(x) * 1000 for x in out[:5])
        rows.append((dns, tcp, tls, ttfb, total))
    cols = list(zip(*rows)) if rows else [[]] * 5
    return {
        "dns": med(cols[0]), "tcp": med(cols[1]), "tls": med(cols[2]),
        "ttfb": med(cols[3]), "total": med(cols[4]), "errors": errors,
    }


def curl_get(url: str, base: str, head_only=False):
    cmd = ["curl", "-s", "--max-time", "60", "-H", "Accept-Encoding: zstd, br, gzip",
           "-o", os.devnull if head_only else "-", "-D", "-" if head_only else os.devnull,
           "-w", "%{http_code} %{size_download}" if head_only else ""]
    if not head_only:
        cmd.append("--compressed")  # HTML нужен распакованным
    if needs_auth(base):
        cmd += ["-u", f"{PREVIEW_USER}:{PREVIEW_PASS}"]
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout


def asset_report(base: str):
    """Файлы сборки со страницы /login: размер по сети, сжатие; ключи window.env (без значений)."""
    import re
    html = curl_get(base + "/login", base)
    print(f"--- {base}/login: {len(html)} bytes; script/link/env lines:")
    for line in html.splitlines():
        if re.search(r"<script|<link|env", line):
            print("   ", line.strip()[:200])
    env_block = re.search(r"window\.env\s*=\s*\{(.*?)\}", html, re.S)
    env_keys = []
    if env_block:
        for k, val in re.findall(r"(\w+)\s*:\s*'([^']*)'", env_block.group(1)):
            env_keys.append(f"{k}={'set' if val else 'EMPTY'}")
    rows = []
    for src in re.findall(r'(?:src|href)="(/assets/[^"]+)"', html):
        out = curl_get(base + src, base, head_only=True)
        enc = re.search(r"(?im)^content-encoding:\s*(\S+)", out)
        tail = out.strip().splitlines()[-1].split() if out.strip() else []
        code, size = (tail[-2], tail[-1]) if len(tail) >= 2 else ("?", "0")
        rows.append(f"| {src} | {code} | {enc.group(1) if enc else 'нет'} | {round(int(size) / 1024)} |")
    return env_keys, rows


LCP_JS = """() => new Promise(resolve => {
  let v = null;
  try {
    new PerformanceObserver(l => { for (const e of l.getEntries()) v = e.startTime; })
      .observe({type: 'largest-contentful-paint', buffered: true});
  } catch (e) {}
  setTimeout(() => resolve(v), 300);
})"""

NAV_JS = """() => {
  const n = performance.getEntriesByType('navigation')[0];
  const res = performance.getEntriesByType('resource');
  return {
    ttfb: n ? n.responseStart : null,
    dcl: n ? n.domContentLoadedEventEnd : null,
    load: n ? n.loadEventEnd : null,
    requests: res.length + 1,
    kb: Math.round((res.reduce((s, r) => s + (r.transferSize || 0), 0) + (n ? n.transferSize : 0)) / 1024),
  };
}"""


def browser_runs(pw, base: str, path: str, proxy):
    origin = f"{urlparse(base).scheme}://{urlparse(base).netloc}"
    auth_header = None
    if needs_auth(base):
        auth_header = "Basic " + base64.b64encode(f"{PREVIEW_USER}:{PREVIEW_PASS}".encode()).decode()

    def handler(route):
        if auth_header:
            route.continue_(headers={**route.request.headers, "authorization": auth_header})
        else:
            route.continue_()

    launch = {"proxy": proxy} if proxy else {}
    browser = pw.chromium.launch(**launch)
    samples, errors = [], 0
    try:
        for _ in range(RUNS):
            ctx = browser.new_context()
            ctx.route(f"{origin}/**", handler)
            page = ctx.new_page()
            try:
                t0 = time.monotonic()
                resp = page.goto(base + path, wait_until="load", timeout=NAV_TIMEOUT_MS)
                if not resp or resp.status >= 400:
                    errors += 1
                    continue
                try:
                    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
                except Exception:
                    pass
                idle = (time.monotonic() - t0) * 1000
                m = page.evaluate(NAV_JS)
                m["lcp"] = page.evaluate(LCP_JS)
                m["idle"] = idle
                samples.append(m)
            except Exception:
                errors += 1
            finally:
                ctx.close()
    finally:
        browser.close()
    pick = lambda k: med([s[k] for s in samples])
    return {k: pick(k) for k in ("ttfb", "dcl", "load", "lcp", "idle", "requests", "kb")} | {"errors": errors}


def fmt(v):
    return "—" if v is None else str(v)


def main():
    curl_table = [
        "| Сайт | Режим | DNS | TCP | TLS | TTFB | Total | ошибок |",
        "|---|---|---|---|---|---|---|---|",
    ]
    br_table = [
        "| Сайт | Режим | Страница | TTFB | DCL | load | LCP | networkidle | запросов | КБ | ошибок |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    with sync_playwright() as pw:
        for site, base in SITES.items():
            for mode, proxy in MODES.items():
                c = curl_runs(base, proxy)
                curl_table.append(
                    f"| {site} | {mode} | {fmt(c['dns'])} | {fmt(c['tcp'])} | {fmt(c['tls'])} | "
                    f"{fmt(c['ttfb'])} | {fmt(c['total'])} | {c['errors']}/{RUNS * 2} |"
                )
                print(curl_table[-1], flush=True)
                for path in PAGES:
                    b = browser_runs(pw, base, path, proxy)
                    br_table.append(
                        f"| {site} | {mode} | {path} | {fmt(b['ttfb'])} | {fmt(b['dcl'])} | {fmt(b['load'])} | "
                        f"{fmt(b['lcp'])} | {fmt(b['idle'])} | {fmt(b['requests'])} | {fmt(b['kb'])} | "
                        f"{b['errors']}/{RUNS} |"
                    )
                    print(br_table[-1], flush=True)

    assets = []
    for site, base in SITES.items():
        keys, rows = asset_report(base)
        assets += ["", f"#### {site}", f"window.env: {', '.join(keys) or 'не найден'}", "",
                   "| Файл | HTTP | Сжатие | КБ по сети |", "|---|---|---|---|", *rows]

    report = "\n".join([
        f"## Скорость сайтов (медианы, мс; повторов: curl {RUNS * 2}, браузер {RUNS}, холодный кэш)",
        "", "### curl — HTML главной", *curl_table,
        "", "### Браузер (Playwright Chromium)", *br_table,
        "", "### Файлы сборки /login (curl, Accept-Encoding: zstd, br, gzip)", *assets,
        "", "_Раннер GitHub Actions находится вне РФ: «direct» — зарубежный клиент, «proxy (RU)» — через прокси в РФ._",
    ])
    print(report)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")


if __name__ == "__main__":
    main()
