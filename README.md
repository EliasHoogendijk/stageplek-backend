# StagePlek Backend

## Deployment op Railway (gratis)

### Stap 1 — GitHub
1. Ga naar github.com en maak een gratis account
2. Maak een nieuw repository aan genaamd `stageplek-backend`
3. Upload deze 3 bestanden: `main.py`, `requirements.txt`, `Procfile`

### Stap 2 — Railway
1. Ga naar railway.app en log in met je GitHub account
2. Klik op **New Project → Deploy from GitHub repo**
3. Kies je `stageplek-backend` repository
4. Railway detecteert automatisch dat het een Python app is

### Stap 3 — PostgreSQL database toevoegen
1. In je Railway project, klik op **New** → **Database** → **PostgreSQL**
2. Railway koppelt automatisch `DATABASE_URL` aan je app
3. Je hoeft verder niets in te stellen — de database wordt automatisch aangemaakt!

### Stap 4 — Je URL kopiëren
1. Klik op je app in Railway
2. Ga naar **Settings** → **Domains**
3. Klik **Generate Domain**
4. Kopieer de URL (bijv. `https://stageplek-backend.up.railway.app`)

### Stap 5 — Frontend koppelen
1. Open `stageplek.html` in je browser
2. Vul je Railway URL in het verbindingsscherm
3. Klaar!

## Lokaal testen (optioneel)
```bash
pip install -r requirements.txt
DATABASE_URL="postgresql://user:pass@localhost/stageplek" uvicorn main:app --reload
```

## API endpoints
- `GET /` — status check
- `GET /bedrijven` — alle bedrijven ophalen
- `POST /bedrijven` — bedrijf toevoegen
- `GET /beoordelingen/{id}` — reviews voor een bedrijf
- `POST /beoordelingen` — review toevoegen
- `GET /stats` — statistieken
