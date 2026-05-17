from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import psycopg2
import psycopg2.extras
import os

# ============================================================
# CONFIG
# Railway geeft automatisch DATABASE_URL als je PostgreSQL
# toevoegt aan je project.
# ============================================================
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ============================================================
# DATABASE SETUP
# ============================================================
def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bedrijven (
            id SERIAL PRIMARY KEY,
            naam TEXT NOT NULL,
            sector TEXT,
            type TEXT DEFAULT 'Onbekend',
            niveau TEXT,
            regio TEXT,
            km INTEGER DEFAULT 20,
            vergoeding TEXT DEFAULT 'onbekend',
            bedrag NUMERIC DEFAULT 0,
            verg_per TEXT,
            erkend BOOLEAN DEFAULT FALSE,
            crebo INTEGER,
            contact_naam TEXT,
            contact_mail TEXT,
            notitie TEXT,
            toegevoegd_door TEXT DEFAULT 'systeem',
            aangemaakt_op TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS beoordelingen (
            id SERIAL PRIMARY KEY,
            bedrijf_id INTEGER REFERENCES bedrijven(id) ON DELETE CASCADE,
            ster NUMERIC NOT NULL CHECK (ster >= 0.5 AND ster <= 5),
            begeleiding NUMERIC DEFAULT 0,
            sfeer NUMERIC DEFAULT 0,
            leer NUMERIC DEFAULT 0,
            afgerond BOOLEAN DEFAULT TRUE,
            tekst TEXT,
            datum TEXT,
            aangemaakt_op TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("SELECT COUNT(*) FROM bedrijven;")
    if cur.fetchone()[0] == 0:
        seed_data(cur)

    conn.commit()
    cur.close()
    conn.close()
    print("Database klaar!")

def seed_data(cur):
    bedrijven = [
        ("Albert Heijn DC","Logistiek & Transport","BOL","mbo 3","Utrecht",8,"ja",400,None,True,None,"Dhr. de Vries","stage@ah.nl",None),
        ("ASML","Techniek & Elektro","BBL","mbo 4","Eindhoven",45,"ja",750,None,True,None,"Mevr. Smit","stages@asml.com",None),
        ("Gemeente Amsterdam","Veiligheid & Overheid","BOL","mbo 3","Amsterdam",30,"nee",0,None,False,None,"Dhr. Bakker","stage@amsterdam.nl",None),
        ("Carglass Nederland","Automotive","BBL","mbo 2","Rotterdam",35,"ja",600,None,True,None,"Mevr. Jansen","stage@carglass.nl",None),
        ("UMC Utrecht","Zorg & Welzijn","BOL","mbo 4","Utrecht",5,"nee",0,None,True,None,"Dhr. Hendriks","stage@umcutrecht.nl",None),
        ("Shell Nederland","Techniek & Proces","BBL","mbo 4","Den Haag",55,"ja",800,None,True,None,"Mevr. de Groot","stage@shell.nl",None),
        ("Jumbo Supermarkten","Retail & Handel","BOL","mbo 2","Arnhem",12,"ja",350,None,True,None,"Dhr. Visser","stage@jumbo.com",None),
        ("Eneco Groep","Techniek & Elektro","BBL","mbo 4","Rotterdam",28,"ja",700,None,True,None,"Mevr. van Dam","stage@eneco.nl",None),
        ("Recroot","Zakelijke dienstverlening","BBL","mbo 2","Bunschoten-Spakenburg",15,"onbekend",0,None,True,None,"Sandra van Barneveld","info@recroot.nl",None),
        ("De Zuurstok","Retail & Handel","BOL","hbo","Bunschoten-Spakenburg",15,"onbekend",0,None,True,None,None,None,None),
        ("Spakenburgse Zeevishandel Harry van Goor","Voedingsindustrie","BBL","mbo 2","Bunschoten-Spakenburg",15,"onbekend",0,None,False,None,None,None,None),
        ("Gemeente Amersfoort","Veiligheid & Overheid","BBL","mbo 3","Amersfoort",10,"onbekend",0,None,True,None,"Stagebureau","stage@amersfoort.nl",None),
        ("Pon","Automotive","BOL","mbo 4","Nijkerk",20,"onbekend",0,None,True,None,None,None,None),
        ("Karwei","Bouw & Afwerking","BBL","mbo 2","Landelijk",20,"onbekend",0,None,True,None,None,None,None),
        ("Voestalpine","Techniek & Metaal","BBL","mbo 3","Landelijk",20,"onbekend",0,None,False,None,None,None,None),
        ("Zwaan en van den Bor","Bouw & Infra","BBL","mbo 2","Bunschoten-Spakenburg",15,"onbekend",0,None,True,None,None,None,None),
        ("Bzzzonder KVB Vathorst","Onderwijs & Pedagogiek","BOL","mbo 4","Amersfoort",10,"onbekend",0,None,True,None,None,None,None),
        ("Van den Hoogen Engineering","Techniek & Elektro","BBL","mbo 2","Bunschoten-Spakenburg",15,"onbekend",0,None,True,None,None,None,None),
        ("Boetech MEPS","Techniek & Mechatronica","BOL","mbo 4","Almere",30,"onbekend",0,None,True,None,None,None,None),
        ("Groenkreatief","Groen & Natuur","BOL","mbo 4","Achterveld",15,"onbekend",0,None,True,None,None,None,None),
        ("ICT Netherlands B.V.","ICT & Media","BOL","mbo 4","Landelijk",50,"ja",0,None,True,27016,"Erwin Orriens","info@ict.nl","Erkend leerbedrijf crebo 27016."),
        ("Goflex Amsterdam","Techniek & Elektro","BBL","mbo 2-4","Amsterdam",35,"ja",0,None,True,27092,None,None,"Erkend BBL-leerbedrijf Amsterdam."),
        ("Ridderflex","Techniek & Metaal","BOL","mbo 2-4","Ridderkerk",45,"ja",0,None,True,25161,"Stagebureau","jobs@ridderflex.nl",None),
        ("Lerenlassen.nl","Techniek & Metaal","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,25163,None,None,"Lassen en metaalbewerking."),
        ("Amsta","Zorg & Welzijn","BBL","mbo 3-4","Amsterdam",35,"ja",0,None,True,25480,"Stagebureau",None,"Groot erkend zorgbedrijf Amsterdam."),
        ("Equipe Zorgbedrijven Amsterdam","Zorg & Welzijn","Onbekend","mbo 3-4","Amsterdam",35,"onbekend",0,None,True,25480,None,None,None),
        ("Horecacentrum Amsterdam","Horeca & Voeding","Onbekend","mbo 1-4","Amsterdam",35,"onbekend",0,None,True,25180,None,None,None),
        ("Bam Boa Amsterdam","Horeca & Voeding","BOL","mbo 3","Amsterdam",35,"ja",0,None,True,25180,None,None,"Restaurant in Amsterdam."),
        ("Logistics United","Logistiek & Transport","Onbekend","mbo 2-4","Landelijk",30,"ja",0,None,True,25340,None,None,None),
        ("Logistiek Holland B.V.","Logistiek & Transport","Onbekend","mbo 2-4","Landelijk",30,"ja",0,None,True,25341,None,None,None),
        ("Schiphol Logistics Park","Logistiek & Transport","Onbekend","mbo 2-4","Amsterdam",35,"ja",0,None,True,25342,None,None,None),
        ("MBO Utrecht","Zorg & Welzijn","Onbekend","mbo 1-4","Utrecht",10,"onbekend",0,None,True,None,"Stagebureau","stage@mbo-utrecht.nl","Zorg, ICT, Techniek en Horeca."),
        ("Tio","Toerisme & Recreatie","Onbekend","mbo 3-4","Utrecht",10,"onbekend",0,None,True,None,None,None,"Toerisme, Hotel en Events."),
        ("Herman Brood Academie","ICT & Media","BOL","mbo 3-4","Utrecht",10,"onbekend",0,None,True,None,None,None,"Muziek en media opleidingen."),
        ("Buurtteam MBO","Zorg & Welzijn","BOL","mbo 3-4","Utrecht",10,"onbekend",0,None,True,None,None,None,"Sociaal werk stages."),
        ("Dutch HealthTec Academy","Zorg & Welzijn","Onbekend","mbo 3-4","Utrecht",10,"onbekend",0,None,True,None,None,None,"Zorgtechniek opleidingen."),
        ("Polar ICT","ICT & Media","Onbekend","mbo 3-4","Landelijk",20,"onbekend",0,None,True,None,None,None,None),
        ("VBVB ICT","ICT & Media","Onbekend","mbo 3-4","Landelijk",20,"onbekend",0,None,True,None,None,None,None),
        ("Kalf ICT","ICT & Media","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,None,None,None,None),
        ("Maandag Engineering","Techniek & Elektro","Onbekend","mbo 3-4","Landelijk",20,"ja",0,None,True,None,None,None,"Techniek en Engineering."),
        ("TechniekMatch","Techniek & Metaal","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,None,None,None,None),
        ("NL-Techniek","Techniek & Installatie","Onbekend","mbo 2-4","Landelijk",20,"ja",0,None,True,None,None,None,None),
        ("Tetrix Techniekopleidingen Amsterdam","Techniek & Mechatronica","Onbekend","mbo 1-4","Amsterdam",35,"onbekend",0,None,True,None,None,None,None),
        ("TechniekFabriek Amsterdam","Techniek & Metaal","Onbekend","mbo 2-4","Amsterdam",35,"ja",0,None,True,None,None,None,"Treintechniek specialisatie."),
        ("Emile Thuiszorg","Zorg & Welzijn","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,25270,None,None,None),
        ("Top Zorg Nederland B.V.","Zorg & Welzijn","Onbekend","mbo 3-4","Landelijk",20,"ja",0,None,True,25480,None,None,None),
        ("Leergroep Zorg en Verpleging B.V.","Zorg & Welzijn","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,25480,None,None,None),
        ("Leer Zorg","Zorg & Welzijn","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,25270,None,None,None),
        ("Sara Thuiszorg","Zorg & Welzijn","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,None,None,None,None),
        ("Horeca Stichting Nederland","Horeca & Voeding","Onbekend","mbo 1-4","Landelijk",30,"onbekend",0,None,True,25180,None,None,None),
        ("De Horeca Academie Amsterdam","Horeca & Voeding","Onbekend","mbo 1-4","Amsterdam",35,"onbekend",0,None,True,25180,None,None,None),
        ("Zorgplein Holland","Zorg & Welzijn","Onbekend","mbo 2-4","Landelijk",20,"onbekend",0,None,True,None,None,None,"Thuiszorg organisatie."),
        ("Amsta Karaad Dagbesteding Overtoom","Zorg & Welzijn","Onbekend","mbo 2-4","Amsterdam",35,"ja",0,None,True,None,None,None,"Ouderenzorg en dagbesteding."),
    ]

    for b in bedrijven:
        cur.execute("""
            INSERT INTO bedrijven
            (naam,sector,type,niveau,regio,km,vergoeding,bedrag,verg_per,
             erkend,crebo,contact_naam,contact_mail,notitie,toegevoegd_door)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'systeem')
        """, b)

    # Reviews voor bekende bedrijven
    cur.execute("SELECT id,naam FROM bedrijven WHERE naam IN ('Albert Heijn DC','ASML','Gemeente Amsterdam','Carglass Nederland','UMC Utrecht')")
    ids = {r[1]: r[0] for r in cur.fetchall()}

    reviews = [
        (ids.get("Albert Heijn DC"),4,4,3.5,4,True,"Goede begeleiding, druk maar leerzaam.","mrt 2025"),
        (ids.get("Albert Heijn DC"),3.5,3,4,3.5,True,"Fysiek zwaar werk maar je leert veel.","jan 2025"),
        (ids.get("ASML"),5,5,5,5,True,"Topbedrijf, uitstekende begeleiders!","apr 2025"),
        (ids.get("ASML"),4.5,4,5,4.5,True,"Veel verantwoordelijkheid, echt gaaf.","feb 2025"),
        (ids.get("Gemeente Amsterdam"),3,2.5,3,3,False,"Rustige omgeving, weinig uitdaging.","mrt 2025"),
        (ids.get("Carglass Nederland"),4,4,4,4,True,"Fijne werksfeer en goed leertraject.","apr 2025"),
        (ids.get("Carglass Nederland"),4.5,4.5,4,4.5,True,"Super leerzaam!","mrt 2025"),
        (ids.get("UMC Utrecht"),4.5,5,4,4.5,True,"Geweldige stagebegeleiding!","jan 2025"),
        (ids.get("UMC Utrecht"),5,5,5,5,True,"Enorm veel geleerd, aanrader.","nov 2024"),
    ]
    for r in reviews:
        if r[0]:
            cur.execute("""
                INSERT INTO beoordelingen
                (bedrijf_id,ster,begeleiding,sfeer,leer,afgerond,tekst,datum)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, r)

    print(f"{len(bedrijven)} bedrijven en reviews toegevoegd!")

# ============================================================
# APP
# ============================================================
app = FastAPI(title="StagePlek API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

class BedrijfIn(BaseModel):
    naam: str
    sector: Optional[str] = None
    type: Optional[str] = "Onbekend"
    niveau: Optional[str] = None
    regio: Optional[str] = None
    km: Optional[int] = 20
    vergoeding: Optional[str] = "onbekend"
    bedrag: Optional[float] = 0
    verg_per: Optional[str] = None
    erkend: Optional[bool] = False
    crebo: Optional[int] = None
    contact_naam: Optional[str] = None
    contact_mail: Optional[str] = None
    notitie: Optional[str] = None

class BeoordelingIn(BaseModel):
    bedrijf_id: int
    ster: float
    begeleiding: Optional[float] = 0
    sfeer: Optional[float] = 0
    leer: Optional[float] = 0
    afgerond: Optional[bool] = True
    tekst: Optional[str] = None
    datum: Optional[str] = None

def row_to_dict(cur, row):
    return {desc[0]: val for desc, val in zip(cur.description, row)}

def rows_to_list(cur, rows):
    return [row_to_dict(cur, r) for r in rows]

@app.get("/")
def root():
    return {"status": "StagePlek API werkt!", "versie": "2.0"}

@app.get("/bedrijven")
def get_bedrijven():
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT b.*,
                COUNT(r.id) AS aantal_reviews,
                ROUND(AVG(r.ster)::numeric,1) AS gem_ster,
                ROUND(AVG(r.begeleiding)::numeric,1) AS gem_begeleiding,
                ROUND(AVG(r.sfeer)::numeric,1) AS gem_sfeer,
                ROUND(AVG(r.leer)::numeric,1) AS gem_leer
            FROM bedrijven b
            LEFT JOIN beoordelingen r ON r.bedrijf_id = b.id
            GROUP BY b.id ORDER BY b.naam
        """)
        return {"bedrijven": rows_to_list(cur, cur.fetchall())}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        cur.close(); conn.close()

@app.post("/bedrijven")
def add_bedrijf(b: BedrijfIn):
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO bedrijven
            (naam,sector,type,niveau,regio,km,vergoeding,bedrag,verg_per,
             erkend,crebo,contact_naam,contact_mail,notitie,toegevoegd_door)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'leerling')
            RETURNING *
        """, (b.naam,b.sector,b.type,b.niveau,b.regio,b.km,b.vergoeding,
              b.bedrag,b.verg_per,b.erkend,b.crebo,b.contact_naam,b.contact_mail,b.notitie))
        nieuw = row_to_dict(cur, cur.fetchone())
        conn.commit()
        return {"success": True, "bedrijf": nieuw}
    except Exception as e:
        conn.rollback(); raise HTTPException(500, str(e))
    finally:
        cur.close(); conn.close()

@app.get("/beoordelingen/{bedrijf_id}")
def get_beoordelingen(bedrijf_id: int):
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM beoordelingen WHERE bedrijf_id=%s ORDER BY aangemaakt_op DESC", (bedrijf_id,))
        return {"beoordelingen": rows_to_list(cur, cur.fetchall())}
    finally:
        cur.close(); conn.close()

@app.post("/beoordelingen")
def add_beoordeling(r: BeoordelingIn):
    if not 0.5 <= r.ster <= 5:
        raise HTTPException(400, "Ster moet tussen 0.5 en 5 zijn")
    if not r.tekst or len(r.tekst.strip()) < 5:
        raise HTTPException(400, "Beoordeling tekst te kort")
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO beoordelingen
            (bedrijf_id,ster,begeleiding,sfeer,leer,afgerond,tekst,datum)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *
        """, (r.bedrijf_id,r.ster,r.begeleiding,r.sfeer,r.leer,r.afgerond,r.tekst,r.datum))
        nieuw = row_to_dict(cur, cur.fetchone())
        conn.commit()
        return {"success": True, "beoordeling": nieuw}
    except Exception as e:
        conn.rollback(); raise HTTPException(500, str(e))
    finally:
        cur.close(); conn.close()

@app.get("/stats")
def get_stats():
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM bedrijven")
        b = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM beoordelingen")
        r = cur.fetchone()[0]
        return {"aantal_bedrijven": b, "aantal_beoordelingen": r}
    finally:
        cur.close(); conn.close()
