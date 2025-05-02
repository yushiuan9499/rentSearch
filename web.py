#!/bin/python3
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Optional
import filter_sorter
import client
import parser
import json
import time

app = FastAPI()
with open(".env", "r") as f:
    env = f.read().splitlines()
    for line in env:
        if line.startswith("SECRET_KEY"):
            secret_key = line.split("=")[1]
            break
    else:
        raise ValueError("SECRET_KEY not found in .env file")
app.add_middleware(SessionMiddleware, secret_key=secret_key)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
nfu_client = client.NfuClient()


def fetch_data(school_abbr: str, force_update = False) -> list[dict]:
    """
    Fetches data from the database or updates it if force_update is True.
    """
    with open("data/houses-raw/last_update.json", "r") as f:
        last_update = json.load(f)
    if not force_update:
        # 資料有效日期是2周
        if school_abbr in last_update and time.time() - last_update[school_abbr] < 14 * 24 * 60 * 60:
            with open(f"data/houses/{school_abbr}.json", "r") as f:
                data = json.load(f)
            return data
    # 更新資料
    raw_data = nfu_client.get_house_data_by_abbr(school_abbr)
    parsed_data = parser.parse_list(raw_data)
    # 儲存資料
    with open(f"data/houses-raw/{school_abbr}.json", "w", encoding='utf-8') as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)
    with open(f"data/houses/{school_abbr}.json", "w", encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
    with open("data/houses-raw/last_update.json", "w") as f:
        last_update[school_abbr] = time.time()
        json.dump(last_update, f)
    return parsed_data


@app.get("/")
def form_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": [], 
    })

@app.post("/search")
async def search(request: Request,
                 min_price: Optional[int] = Form(0),
                 max_price: Optional[int] = Form(1000000),
                 min_area: Optional[int] = Form(0),
                 max_area: Optional[int] = Form(1000000),
                 max_travel_time: Optional[int] = Form(1000000),
                 max_distance: Optional[int] = Form(1000000),
                 gender: Optional[str] = Form("N/A"),
                 room_types: Optional[list[str]] = Form([]),
                 rent_types: Optional[list[str]] = Form([]),
                 house_types: Optional[list[str]] = Form([]),
                 materials: Optional[list[str]] = Form([]),
                 longitude: Optional[float] = Form(0),
                 latitude: Optional[float] = Form(0),
                 min_price_order: Optional[int] = Form(0),
                 max_price_order: Optional[int] = Form(0),
                 area_order: Optional[int] = Form(0),
                 duration_order: Optional[int] = Form(1000),
                 distance_order: Optional[int] = Form(1000)):
    filter = filter_sorter.Filter(
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        max_travel_time=max_travel_time,
        max_distance=max_distance,
        gender=gender,
        room_types=room_types,
        rent_types=rent_types,
        house_types=house_types,
        materials=materials,
        school_location=((longitude, latitude) if longitude != 1000 and latitude != 1000 else None))
    sorter = filter_sorter.Sort(
        min_price=min_price_order,
        max_price=max_price_order,
        area=area_order,
        travel_time=duration_order,
        distance=distance_order)


    # 取得資料
    data = fetch_data(request.session.get("school_abbr"))
    # 過濾與排序資料
    filtered_data = filter_sorter.sortNfilter(data, sorter,filter)
    return JSONResponse(filtered_data)

@app.post("/set_school")
def set_school(request: Request, school_abbr: str = Form(...)):
    request.session["school_abbr"] = school_abbr
    # 取得資料
    result = fetch_data(school_abbr)
    return JSONResponse(result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
