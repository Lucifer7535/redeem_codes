import asyncio
from typing import List

import aiohttp
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()


async def get_code_from_eurogamer() -> List[dict]:
    codes = []
    try:
        async with aiohttp.ClientSession() as session, session.get(
            "https://www.eurogamer.net/genshin-impact-codes-livestream-active-working-how-to-redeem-9026" # noqa
        ) as response:
            html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        entries = soup.select("div.article_body_content > ul > li")

        for entry in entries:
            code_element = entry.find("strong")
            if code_element:
                code = code_element.get_text().strip()
                description = entry.get_text(separator=' ').replace(code, '').strip() # noqa
                if code == code.upper():
                    description = description.lstrip(': - ')
                    codes.append({"code": code, "description": description})

    except Exception as e:
        print(f"Error in get_code_from_eurogamer: {e}")
        return []

    return codes


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Genshin Impact redeem code API! Please visit /codes for codes." # noqa
    }


@app.get("/codes")
async def read_codes() -> List[dict]:
    euro_gamer = await asyncio.gather(
        get_code_from_eurogamer(),
    )

    old_codes = ["GENSHINGIFT", "XBRSDNF6BP4R", "FTRUFT7AT5SV"]

    all_codes = [code for sublist in euro_gamer for code in sublist]

    unique_codes = {code["code"]: code for code in all_codes}.values()

    filtered_codes = [
        code
        for code in unique_codes
        if code["code"] not in old_codes and code["description"] != ""
    ]

    if len(filtered_codes) == 0:
        return all_codes
    return list(filtered_codes)


if __name__ == "__main__":
    import uvicorn
    import uvloop

    uvloop.install()
    uvicorn.run(app)
