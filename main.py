from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

conn = sqlite3.connect('/tmp/treasure.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS teams
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              leader TEXT,
              color TEXT,
              current_step INTEGER DEFAULT 1,
              completed BOOLEAN DEFAULT FALSE)''')

c.execute('''CREATE TABLE IF NOT EXISTS routes
             (color TEXT,
              step INTEGER,
              expected_flag TEXT,
              clue TEXT,
              image TEXT)''')

routes = {
    'Red': [  # Order: 1-3-5-6-7-4-2-8
        (1, 'welcometotarangctf', 'no more rats in this place :/', 'images/red/step1.jpg'),          # C Block
        (2, 'ratsarestinky', 'What now bruh', 'images/red/step2.jpg'),                               # MM Foods
        (3, 'doulovedoingtasks', '1v1', 'images/red/step3a.jpg,images/red/step3b.jpg'),              # Big Mingos
        (4, 'pleasetellmeustillluvme', '2/4 personnes jouent...', 'images/red/step4.jpg'),           # Library
        (5, 'ilikekatwilliams', 'place for cnade actrpteic', 'images/red/step5.jpg'),                # A Block
        (6, 'uaresoclose', 'Biotech clue', 'images/red/step6.jpg'),                                  # BioTech
        (7, 'goodbyemyfriendbacktothelobby', 'We end where we begin.', 'images/red/step7.jpg'),      # Mini Mingos
        (8, '1RUA23CSE182', 'Final Clue: USN of volunteer wearing a different colored shirt...', 'images/red/final.jpg')               # Final C Block
    ],
    'Green': [  # Order: 1-2-7-4-6-3-5-8
        (1, 'welcometotarangctf', 'https://maps.app.goo.gl/UvFQXfnksFB75C5SA', 'images/green/step1.jpg'),  # C Block
        (2, 'goodbyemyfriendbacktothelobby', 'Stretch your body not your mind...', 'images/green/step2.jpg'), # Mini Mingos
        (3, 'ilikekatwilliams', 'The Oscorp of RVCE', 'images/green/step3.jpg'),                          # A Block
        (4, 'uaresoclose', 'I love this foundation', 'images/green/step4.jpg'),                           # BioTech
        (5, 'pleasetellmeustillluvme', "Let's see what's new here", 'images/green/step5.jpg'),             # Library
        (6, 'ratsarestinky', 'First floor is off limits', 'images/green/step6.jpg'),                       # MM Foods
        (7, 'doulovedoingtasks', 'The first conjoined twin of RVU', 'images/green/step7.jpg'),             # Big Mingos
        (8, '1RUA23CSE182', 'Final Clue: USN of volunteer wearing a different colored shirt...', 'images/green/final.jpg')                   # Final C Block
    ],
    'Purple': [  # Order: 1-4-2-7-3-6-5-8
        (1, 'welcometotarangctf', 'Purana Blood Donation Camp', 'images/purple/step1.jpg'),               # C Block
        (2, 'uaresoclose', 'WE love dogs https://www.amazon.com/tarangctf', 'images/purple/step2.jpg'),    # BioTech
        (3, 'goodbyemyfriendbacktothelobby', 'Manika Batra', 'images/purple/step3.jpg'),                   # Mini Mingos
        (4, 'ilikekatwilliams', 'Mural', 'images/purple/step4.jpg'),                                       # A Block
        (5, 'ratsarestinky', 'Google this', 'images/purple/step5.jpg'),                                    # MM Foods
        (6, 'pleasetellmeustillluvme', 'Library clue', 'images/purple/step6.jpg'),                         # Library
        (7, 'doulovedoingtasks', '<– 2 square 1', 'images/purple/step7.jpg'),                              # Big Mingos
        (8, '1RUA23CSE182', 'Final Clue: USN of volunteer wearing a different colored shirt...', 'images/purple/final.jpg')                  # Final C Block
    ],
    'Yellow': [  # Order: 1-6-2-4-5-3-7-8
        (1, 'welcometotarangctf', 'Library image clue', 'images/yellow/step1.jpg'),                        # C Block
        (2, 'pleasetellmeustillluvme', '... .... . -.- .... .- .-. -... .... .- .. -.-- .-', 'images/yellow/step2.jpg'), # Library
        (3, 'goodbyemyfriendbacktothelobby', 'Decode this: Elrwhfk Txdgudqjoh', 'images/yellow/step3.jpg'), # Mini Mingos
        (4, 'uaresoclose', 'I make twins/copies...', 'images/yellow/step4.jpg'),                           # BioTech
        (5, 'doulovedoingtasks', 'He did something in 2004', 'images/yellow/step5.jpg'),                    # Big Mingos
        (6, 'ratsarestinky', 'it’s just', 'images/yellow/step6.jpg'),                                       # MM Foods
        (7, 'ilikekatwilliams', 'Baseball', 'images/yellow/step7.jpg'),                                     # A Block
        (8, '1RUA23CSE182', 'Final Clue: USN of volunteer wearing a different colored shirt...', 'images/yellow/final.jpg')                   # Final C Block
    ]
}

for color, steps in routes.items():
    for step in steps:
        c.execute('''INSERT OR IGNORE INTO routes VALUES (?,?,?,?,?)''',
                 (color, step[0], step[1], step[2], step[3]))

conn.commit()
conn.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start")
async def start(leader: str = Form(...)):
    return RedirectResponse(f"/color?leader={leader}", status_code=303)

@app.get("/color", response_class=HTMLResponse)
async def color_page(request: Request):
    return templates.TemplateResponse("color.html", {"request": request})

@app.post("/route")
async def create_team(leader: str = Form(...), color: str = Form(...)):
    conn = sqlite3.connect('/tmp/treasure.db')
    c = conn.cursor()
    c.execute("INSERT INTO teams (leader, color) VALUES (?, ?)", (leader, color))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/route?leader={leader}&color={color}", status_code=303)

@app.get("/route", response_class=HTMLResponse)
async def route_page(request: Request, leader: str, color: str):
    conn = sqlite3.connect('/tmp/treasure.db')
    c = conn.cursor()
    c.execute("SELECT current_step FROM teams WHERE leader=? AND color=?", (leader, color))
    step = c.fetchone()[0]
    conn.close()
    return templates.TemplateResponse("route.html", {
        "request": request,
        "leader": leader,
        "color": color,
        "step": step
    })

@app.post("/validate")
async def validate_flag(leader: str = Form(...), color: str = Form(...), flag: str = Form(...)):
    conn = sqlite3.connect('/tmp/treasure.db')
    c = conn.cursor()
    
    c.execute("SELECT current_step FROM teams WHERE leader=? AND color=?", (leader, color))
    current_step = c.fetchone()[0]
    
    c.execute("SELECT clue, image FROM routes WHERE color=? AND step=? AND expected_flag=?", 
             (color, current_step, flag))
    result = c.fetchone()
    
    if result:
        new_step = current_step + 1
        c.execute("UPDATE teams SET current_step=? WHERE leader=? AND color=?", 
                 (new_step, leader, color))
        conn.commit()
        conn.close()
        return {"success": True, "clue": result[0], "image": result[1], "step": new_step}
    
    conn.close()
    return {"success": False, "error": "Invalid flag!"}
