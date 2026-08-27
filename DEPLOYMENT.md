# Deploy MicroscopyAI to Vercel

This guide deploys the **React frontend** to Vercel. The UI runs in **Demo Mode** with bundled precomputed analysis (28 synthetic cells). Full **Cellpose live inference** requires a separate Python server (not Vercel serverless).

## What runs on Vercel

| Component | On Vercel? |
| --- | --- |
| React + Vite UI | Yes |
| Demo sample image + precomputed results | Yes |
| CSV export, charts, overlays from demo data | Yes |
| Cellpose / PyTorch live inference | No — deploy `backend/` separately |

## Option A — Deploy from GitHub (recommended)

### 1. Merge or use the MicroscopyAI branch

Ensure `main` contains the MicroscopyAI code (branch `cursor/microscopyai-pipeline-85a8`).

### 2. Create a Vercel project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `vc-dhanush/Aganitha_cognitive_solutions`
3. **Root Directory:** leave as repository root (`.`)
4. Vercel will read `vercel.json` at the repo root

### 3. Environment variables (Project → Settings → Environment Variables)

Add these for **Production**, **Preview**, and **Development**:

| Name | Value | Required |
| --- | --- | --- |
| `VITE_DEMO_MODE` | `true` | Yes |
| `VITE_API_URL` | *(leave empty for demo-only)* | No |

To connect a deployed Python API later, set:

```text
VITE_API_URL=https://your-api.example.com
```

Do **not** include a trailing slash.

### 4. Deploy

Click **Deploy**. Build should run:

```text
cd frontend && npm ci
cd frontend && npm run build
```

Output: `frontend/dist`

### 5. Verify

1. Open your Vercel URL
2. Click **Sample Dataset** or **RUN ANALYSIS**
3. UI should show **DEMO DATA** (not live inference)
4. Results: ~28 cells, charts, CSV export

---

## Option B — Deploy with Vercel CLI

```bash
git clone https://github.com/vc-dhanush/Aganitha_cognitive_solutions.git
cd Aganitha_cognitive_solutions
npm i -g vercel

# From repo root
vercel

# Set env vars (first deploy)
vercel env add VITE_DEMO_MODE production
# Enter: true

vercel --prod
```

---

## Option C — Root directory = `frontend`

If you set **Root Directory** to `frontend` in Vercel:

1. Remove or ignore root `vercel.json` for that project
2. Use this `frontend/vercel.json`:

```json
{
  "framework": "vite",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

3. Environment variables are the same (`VITE_DEMO_MODE`, `VITE_API_URL`)

---

## Live analysis (optional, separate host)

Deploy the Python API on Railway, Fly.io, Render, or a VM:

```bash
pip install -r backend/requirements.txt
# Optional: pip install cellpose torch
PYTHONPATH=. uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then in Vercel, set:

```text
VITE_API_URL=https://your-backend-url.com
VITE_DEMO_MODE=true
```

Redeploy the frontend. Upload + **RUN ANALYSIS** will use live mode when the API is reachable.

---

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `npm run dev` ENOENT | Run commands from `frontend/`, not your user home folder |
| Build fails on Vercel | Check build logs; run `cd frontend && npm ci && npm run build` locally |
| Blank page after deploy | Confirm `outputDirectory` is `frontend/dist` |
| Demo doesn't load | Set `VITE_DEMO_MODE=true` and redeploy (Vite embeds env at build time) |
| "Live" but no cells | Backend unreachable; demo fallback runs if `VITE_DEMO_MODE=true` |

---

## Custom domain

Vercel → Project → Settings → Domains → add your domain.
