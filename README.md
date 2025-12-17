# Physics Wallah Survey — Animated Dashboard

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Made with](https://img.shields.io/badge/Chart.js-visualizations-ff6384?logo=chartdotjs&logoColor=white)
![Static](https://img.shields.io/badge/Static-Site-0ea5e9)
[![Live Demo](https://img.shields.io/badge/Live-Demo-00C7B7?logo=netlify&logoColor=white)](https://physics-wallah-survey.netlify.app/)
[![Hosted on Netlify](https://img.shields.io/badge/Hosted%20on-Netlify-00ad9f?logo=netlify&logoColor=white)](https://physics-wallah-survey.netlify.app/)

A polished single‑page dashboard (Chart.js + vanilla JS) for the Physics Wallah survey of 100 students. It autoloads `assets/data.json` generated from your Google Form responses and provides animated KPIs, filters, two rich charts, export to PNG, and an insights panel.

Live site: https://physics-wallah-survey.netlify.app/

## Quick start

```powershell
cd "e:\Internships and Projects\ML Projects\Physics Wallah Survey"
".venv\Scripts\python.exe" -m http.server 5500
# Open http://localhost:5500
```

## Data refresh

Regenerate `assets/data.json` if the Excel file changes:

```powershell
".venv\Scripts\python.exe" - <<'PY'
import os, json, pandas as pd, numpy as np
root = r"e:/Internships and Projects/ML Projects/Physics Wallah Survey"
xf = os.path.join(root, "Physics Wallah Survey  (Responses).xlsx")
df = pd.read_excel(xf)
drop = [c for c in df.columns if str(c).lower().startswith('unnamed') and df[c].isna().all()]
df = df.drop(columns=drop) if drop else df
for c in df.columns:
  if pd.api.types.is_datetime64_any_dtype(df[c]):
    df[c] = df[c].dt.strftime('%Y-%m-%d %H:%M:%S').astype(object)
df = df.replace({np.nan: None})
rows = df.to_dict(orient='records')
os.makedirs(os.path.join(root,'assets'), exist_ok=True)
with open(os.path.join(root,'assets','data.json'),'w',encoding='utf-8') as f:
  json.dump({'rows': rows}, f, ensure_ascii=False)
print('Updated assets/data.json', len(rows), 'rows')
PY
```

## Features

- Animated KPIs and chart reveal
- Auto-detection of numeric/categorical/time + Likert mapping
- Export PNG for each chart
- Key Insights sentences
- Works 100% static (no backend)

## Deploy to Netlify

This is a static site. Two easy ways:

1) Netlify Drop (UI)
- Zip or select the project folder and drag onto: https://app.netlify.com/drop

2) Netlify CLI
```bash
npm i -g netlify-cli
netlify login
netlify deploy --dir .          # preview URL
netlify deploy --prod --dir .   # production URL
```

Caching of `assets/data.json` is disabled via `netlify.toml` so updates reflect immediately.

## Push to GitHub

```powershell
git init
git add .
git commit -m "feat: initial dashboard"
git branch -M main
git remote add origin https://github.com/Mandar123454/Physics-Wallah-Survey.git
git push -u origin main
```

## License & Security

- License: MIT (see [LICENSE](LICENSE))
- Security: See [SECURITY.md](SECURITY.md) for reporting guidelines

---
Built with HTML + CSS + Chart.js. Smooth, professional, and shareable.
