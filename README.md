# Economic Tripwires Dashboard (Extended)

Daily-updating dashboard with 10-year history and configurable tripwires.

**Preconfigured indicators** (all via FRED unless noted):
- IG OAS (`BAMLC0A0CM`), HY OAS (`BAMLH0A0HYM2`), DSR (`TDSP`)
- Unemployment Rate (`UNRATE`)
- 10Y Treasury (`DGS10`), 2Y Treasury (`DGS2`), **10Y–2Y spread** (derived)
- CPI **YoY%** (derived from `CPIAUCSL`)
- Industrial Production (`INDPRO`) and **YoY%** (derived)
- BAA – 10Y spread (`BAA10Y`)
- ACM 10Y Term Premium (NY Fed CSV)

---

## Quick start (no coding required)

1. **Download this repo ZIP** (from the chat link), unzip it.
2. Create a new GitHub repository and upload the whole folder (drag‑and‑drop in the web UI).
3. Add a repo secret: **Settings → Secrets and variables → Actions → New repository secret**  
   - Name: `FRED_API_KEY` • Value: your key from https://fred.stlouisfed.org/docs/api/api_key.html
4. **Settings → Pages** → set **Build and deployment = GitHub Actions**.
5. **Actions** tab → run **Fetch data daily** once (seeds data).
6. Build & Deploy runs automatically; open the published **GitHub Pages** site.

**Daily schedule:** 02:15 UTC (`.github/workflows/fetch-and-commit.yml`).

## Configure thresholds
Edit `data-pipeline/indicators.yaml` → adjust `tripwires:` or add series.

## Local dev (optional)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r data-pipeline/requirements.txt
export FRED_API_KEY=YOUR_KEY
python data-pipeline/fetch_data.py

cd frontend
npm ci
npm run dev
```
