#!/usr/bin/env python3
"""Generate a clean ER diagram (PNG) for the Genlogs database design."""
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONTM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

f_title = ImageFont.truetype(FONTB, 30)
f_head = ImageFont.truetype(FONTB, 19)
f_row = ImageFont.truetype(FONT, 16)
f_badge = ImageFont.truetype(FONTB, 11)
f_small = ImageFont.truetype(FONT, 14)
f_card = ImageFont.truetype(FONTB, 14)

W, H = 1580, 940
SCALE = 2  # supersample for crisp text
img = Image.new("RGB", (W*SCALE, H*SCALE), "#f7f8fa")
d = ImageDraw.Draw(img)

def S(v): return v*SCALE
def font(fp, sz): return ImageFont.truetype(fp, sz*SCALE)

f_title = font(FONTB, 28)
f_head = font(FONTB, 18)
f_row = font(FONT, 15)
f_badge = font(FONTB, 10)
f_small = font(FONT, 13)
f_card = font(FONTB, 13)
f_leg = font(FONT, 14)
f_legb = font(FONTB, 15)

HEADER_H = 38
ROW_H = 28
BOX_W = 340

# table: (x, y, title, color, [ (col, type, badge) ])
tables = {
 "cameras": (60, 80, "#3b6fd6", [
     ("id","bigserial","PK"),("external_ref","text","UK"),("highway","text",""),
     ("location","geography",""),("status","text","")]),
 "images": (60, 320, "#3b6fd6", [
     ("id","bigserial","PK"),("camera_id","bigint","FK"),("captured_at","timestamptz",""),
     ("storage_uri","text",""),("processing_status","text","")]),
 "detections": (60, 560, "#3b6fd6", [
     ("id","bigserial","PK"),("image_id","bigint","FK"),("kind","text",""),
     ("raw_value","text",""),("confidence","real",""),("bbox","jsonb","")]),
 "carriers": (1100, 80, "#2e9e54", [
     ("id","bigserial","PK"),("usdot_number","bigint","UK"),("legal_name","text",""),
     ("dba_name","text",""),("safer_synced_at","timestamptz","")]),
 "vehicles": (1100, 320, "#2e9e54", [
     ("id","bigserial","PK"),("carrier_id","bigint","FK"),("vin","text",""),
     ("plate","text",""),("plate_state","text","")]),
 "safer_cache": (1100, 560, "#2e9e54", [
     ("usdot_number","bigint","PK"),("payload","jsonb",""),("fetched_at","timestamptz","")]),
 "sightings": (580, 300, "#e08a17", [
     ("id","bigserial","PK"),("image_id","bigint","FK"),("camera_id","bigint","FK"),
     ("carrier_id","bigint","FK"),("vehicle_id","bigint","FK"),("usdot_number","bigint",""),
     ("seen_at","timestamptz",""),("location","geography","")]),
 "carrier_corridor_volume": (580, 650, "#8e44ad", [
     ("id","bigserial","PK"),("origin_city","text",""),("destination_city","text",""),
     ("carrier_id","bigint","FK"),("trucks_per_day","numeric",""),
     ("window_start","date",""),("window_end","date","")]),
}

geom = {}  # name -> dict with box + row y centers
def box_h(cols): return HEADER_H + ROW_H*len(cols)

def draw_table(name):
    x,y,color,cols = tables[name]
    h = box_h(cols)
    geom[name] = {"x":x,"y":y,"w":BOX_W,"h":h,"rows":{}}
    # shadow
    d.rounded_rectangle([S(x+3),S(y+4),S(x+BOX_W+3),S(y+h+4)], radius=S(10), fill="#e2e5ea")
    # body
    d.rounded_rectangle([S(x),S(y),S(x+BOX_W),S(y+h)], radius=S(10), fill="white",
                        outline="#cfd4dc", width=S(1))
    # header
    d.rounded_rectangle([S(x),S(y),S(x+BOX_W),S(y+HEADER_H+10)], radius=S(10), fill=color)
    d.rectangle([S(x),S(y+HEADER_H-6),S(x+BOX_W),S(y+HEADER_H+6)], fill=color)
    d.text((S(x+16),S(y+HEADER_H/2)), name, font=f_head, fill="white", anchor="lm")
    # rows
    for i,(col,typ,badge) in enumerate(cols):
        ry = y+HEADER_H+ROW_H*i
        cy = ry+ROW_H/2
        geom[name]["rows"][col]=cy
        if i%2==1:
            d.rectangle([S(x+1),S(ry),S(x+BOX_W-1),S(ry+ROW_H)], fill="#f4f6f9")
        # badge
        bx = x+14
        if badge:
            bcol = {"PK":"#d4a017","FK":"#5a6b8c","UK":"#7a8aa3"}[badge]
            d.rounded_rectangle([S(bx),S(cy-9),S(bx+26),S(cy+9)], radius=S(4), fill=bcol)
            d.text((S(bx+13),S(cy)), badge, font=f_badge, fill="white", anchor="mm")
        colname_x = x+50
        cf = ImageFont.truetype(FONTB, 15*SCALE) if badge in ("PK","UK") else f_row
        d.text((S(colname_x),S(cy)), col, font=cf, fill="#1f2733", anchor="lm")
        d.text((S(x+BOX_W-14),S(cy)), typ, font=f_small, fill="#8b94a3", anchor="rm")
    # separators
    for i in range(1,len(cols)):
        ry=y+HEADER_H+ROW_H*i
        d.line([S(x+1),S(ry),S(x+BOX_W-1),S(ry)], fill="#eceef2", width=S(1))

for t in tables: draw_table(t)

LINE = "#6b7686"
def anchor(name,col,side):
    g=geom[name]; cy=g["rows"][col]
    x = g["x"] if side=="L" else g["x"]+g["w"]
    return x,cy

def crowfoot(cx,cy,side):
    dx = -16 if side=="L" else 16
    apex=(cx+dx,cy)
    for fy in (cy-8,cy,cy+8):
        d.line([S(apex[0]),S(apex[1]),S(cx),S(fy)], fill=LINE, width=S(2))

def one_tick(px,py,side):
    tx = px-12 if side=="L" else px+12
    d.line([S(tx),S(py-7),S(tx),S(py+7)], fill=LINE, width=S(2))

def zero_one(px,py,side):
    cxx = px-13 if side=="L" else px+13
    d.ellipse([S(cxx-6),S(py-6),S(cxx+6),S(py+6)], outline=LINE, width=S(2), fill="white")
    tx = px-26 if side=="L" else px+26
    d.line([S(tx),S(py-7),S(tx),S(py+7)], fill=LINE, width=S(2))

def connect(p, c, label, child_kind="many", g=34):
    pname,pcol,pside = p
    cname,ccol,cside = c
    px,py = anchor(pname,pcol,pside)
    cx,cy = anchor(cname,ccol,cside)
    pox = px-g if pside=="L" else px+g
    cox = cx-g if cside=="L" else cx+g
    midx = (pox+cox)/2
    pts=[(px,py),(pox,py),(midx,py),(midx,cy),(cox,cy),(cx,cy)]
    sp=[]
    for a in pts: sp+= [S(a[0]),S(a[1])]
    d.line(sp, fill=LINE, width=S(2), joint="curve")
    one_tick(px,py,pside)
    if child_kind=="many": crowfoot(cx,cy,cside)
    else: zero_one(cx,cy,cside)
    # label near the vertical segment, clamped on-canvas
    lxp = min(max(midx+8, 46), W-90)
    d.text((S(lxp),S((py+cy)/2)), label, font=f_card, fill="#465061", anchor="lm")

# relationships  (same-column loops use a tight gap; cross-gap links spread out)
connect(("cameras","id","L"), ("images","camera_id","L"), "1:N", g=22)
connect(("images","id","L"), ("detections","image_id","L"), "1:N", g=22)
connect(("images","id","R"), ("sightings","image_id","L"), "1:N", g=44)
connect(("cameras","id","R"), ("sightings","camera_id","L"), "1:N", g=78)
connect(("carriers","id","R"), ("vehicles","carrier_id","R"), "1:N", g=22)
connect(("carriers","id","L"), ("sightings","carrier_id","R"), "1:N", g=44)
connect(("vehicles","id","L"), ("sightings","vehicle_id","R"), "0..1:N", "many", g=78)
connect(("carriers","id","L"), ("carrier_corridor_volume","carrier_id","R"), "1:N", g=120)
connect(("carriers","usdot_number","R"), ("safer_cache","usdot_number","R"), "1:0..1", "zero_one", g=46)

# Title
d.text((S(60),S(34)), "Genlogs — Database design (ER diagram)", font=f_title, fill="#1f2733", anchor="lm")

# Legend (bottom-left)
lx,ly = 60, 800
legend = [("#3b6fd6","Ingest / vision side"),("#2e9e54","Carrier reference (SAFER FMCSA)"),
          ("#e08a17","Fact: sightings"),("#8e44ad","Read model (CQRS, denormalized)")]
d.text((S(lx),S(ly)), "Layers", font=f_legb, fill="#1f2733", anchor="lm")
for i,(c,t) in enumerate(legend):
    yy=ly+26+i*26
    d.rounded_rectangle([S(lx),S(yy-8),S(lx+18),S(yy+8)], radius=S(3), fill=c)
    d.text((S(lx+28),S(yy)), t, font=f_leg, fill="#1f2733", anchor="lm")

# notation legend (bottom-right)
nx,ny = 1100, 800
d.text((S(nx),S(ny)), "Notation", font=f_legb, fill="#1f2733", anchor="lm")
d.text((S(nx),S(ny+26)), "PK primary key   FK foreign key   UK unique", font=f_leg, fill="#465061", anchor="lm")
d.text((S(nx),S(ny+50)), "|  one        —<  many (crow's foot)", font=f_leg, fill="#465061", anchor="lm")
d.text((S(nx),S(ny+74)), "○|  zero-or-one", font=f_leg, fill="#465061", anchor="lm")

out = "/tmp/claude-1000/-home-rubiano-Genlogs/d47cbf60-4286-4329-90b3-a3aa3a4b93f5/scratchpad/database_erd.png"
img = img.resize((W,H), Image.LANCZOS)
img.save(out)
print("saved", out)
