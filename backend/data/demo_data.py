# data/demo_data.py
# ─────────────────────────────────────────────────────────────────────────────
# Comprehensive realistic Indian agricultural demo data for KrishiLink.
# This file is the single source of truth in DEMO_MODE.
# All IDs are consistent across tables so joins work correctly.
# ─────────────────────────────────────────────────────────────────────────────

from datetime import date, timedelta

# ── Helper: generate dates for the last N days ───────────────────────────────
def _last_n_days(n: int) -> list[str]:
    """Return a list of ISO-formatted date strings for the last n calendar days."""
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(n - 1, -1, -1)]

DATES_15 = _last_n_days(15)   # e.g. ['2026-08-14', ..., '2026-08-28']


# ─────────────────────────────────────────────────────────────────────────────
# CROPS
# ─────────────────────────────────────────────────────────────────────────────
CROPS: list[str] = [
    "Onion",
    "Tomato",
    "Soybean",
    "Cotton",
    "Wheat",
    "Rice",
    "Potato",
    "Chilli",
]


# ─────────────────────────────────────────────────────────────────────────────
# MARKETS (APMC mandis across Maharashtra)
# ─────────────────────────────────────────────────────────────────────────────
MARKETS: list[str] = [
    "Nashik",
    "Lasalgaon",
    "Pune",
    "Ahmednagar",
    "Solapur",
    "Aurangabad",
    "Nagpur",
    "Mumbai",
]


# ─────────────────────────────────────────────────────────────────────────────
# PRICES
# For each (crop, market) combination we store 15 days of historical price data.
# Prices are in INR per quintal (100 kg).
# ─────────────────────────────────────────────────────────────────────────────

def _price_row(modal: int, volume: int, day_index: int, date_str: str) -> dict:
    """Build a single price record with min/max derived from modal price."""
    min_p = round(modal * 0.93)   # ~7% below modal
    max_p = round(modal * 1.07)   # ~7% above modal
    return {
        "modal_price": modal,
        "min_price": min_p,
        "max_price": max_p,
        "volume": volume,        # in tonnes
        "date": date_str,
        "day_index": day_index,  # 0 = oldest, 14 = today
    }


# Raw price series: (modal_price, volume) for each of 15 days
# Index 0 = 14 days ago, Index 14 = today
_RAW: dict[str, dict[str, list[tuple[int, int]]]] = {
    # ── Onion (seasonal, price swings are large) ─────────────────────────────
    "Onion": {
        "Nashik":     [(1200,320),(1180,310),(1220,330),(1300,290),(1350,280),
                       (1400,270),(1420,265),(1380,275),(1360,280),(1320,295),
                       (1280,305),(1250,315),(1230,320),(1210,325),(1200,330)],
        "Lasalgaon":  [(1100,410),(1090,400),(1120,415),(1180,395),(1220,385),
                       (1270,375),(1300,370),(1260,380),(1240,385),(1210,395),
                       (1180,405),(1160,410),(1140,415),(1120,420),(1110,425)],
        "Pune":       [(1350,150),(1330,145),(1370,155),(1420,140),(1460,135),
                       (1500,130),(1520,128),(1490,132),(1470,138),(1440,143),
                       (1410,148),(1390,152),(1370,155),(1355,157),(1340,160)],
        "Ahmednagar": [(1150,200),(1140,195),(1160,205),(1200,190),(1240,185),
                       (1280,180),(1300,178),(1270,183),(1250,188),(1230,193),
                       (1200,198),(1180,202),(1165,205),(1155,207),(1145,210)],
        "Solapur":    [(1050,180),(1040,175),(1070,182),(1110,172),(1150,168),
                       (1190,165),(1210,163),(1180,167),(1160,170),(1140,174),
                       (1110,178),(1090,181),(1075,183),(1060,185),(1050,188)],
        "Aurangabad": [(1080,160),(1070,155),(1095,162),(1130,152),(1165,148),
                       (1195,145),(1215,143),(1190,147),(1170,151),(1150,155),
                       (1125,158),(1105,161),(1090,163),(1082,165),(1075,167)],
        "Nagpur":     [(1020,140),(1010,135),(1030,142),(1065,133),(1095,129),
                       (1120,126),(1140,124),(1115,128),(1100,131),(1080,135),
                       (1060,138),(1045,141),(1030,143),(1022,145),(1015,147)],
        "Mumbai":     [(1500,90),(1480,88),(1510,92),(1560,86),(1600,83),
                       (1640,81),(1660,80),(1630,82),(1610,84),(1580,87),
                       (1550,89),(1530,91),(1515,93),(1505,94),(1495,96)],
    },

    # ── Tomato (highly volatile, seasonal peaks) ──────────────────────────────
    "Tomato": {
        "Nashik":     [(800,200),(820,195),(780,205),(750,210),(700,215),
                       (680,220),(700,218),(730,212),(760,208),(800,203),
                       (840,198),(870,194),(890,191),(910,189),(920,188)],
        "Lasalgaon":  [(750,180),(770,175),(730,185),(710,190),(665,194),
                       (648,198),(665,196),(692,191),(720,187),(755,183),
                       (790,179),(818,175),(838,172),(855,170),(865,169)],
        "Pune":       [(1100,120),(1120,117),(1080,123),(1050,127),(1000,131),
                       (980,134),(1000,132),(1025,128),(1050,125),(1080,122),
                       (1110,119),(1135,116),(1150,114),(1160,113),(1165,112)],
        "Ahmednagar": [(820,110),(840,107),(800,113),(775,117),(730,120),
                       (715,123),(730,121),(753,118),(778,115),(810,112),
                       (840,109),(862,107),(878,105),(890,104),(897,103)],
        "Solapur":    [(700,100),(718,97),(683,103),(660,107),(620,110),
                       (605,113),(620,111),(641,108),(664,105),(693,102),
                       (719,100),(738,98),(752,96),(762,95),(768,94)],
        "Aurangabad": [(750,95),(768,92),(733,98),(710,102),(668,105),
                       (653,108),(668,106),(690,103),(714,100),(743,97),
                       (771,95),(791,93),(806,91),(816,90),(823,89)],
        "Nagpur":     [(680,90),(697,87),(664,93),(642,97),(603,100),
                       (589,103),(603,101),(622,98),(644,95),(671,92),
                       (696,90),(715,88),(728,86),(737,85),(743,84)],
        "Mumbai":     [(1400,60),(1430,58),(1370,62),(1340,65),(1280,68),
                       (1255,70),(1280,68),(1314,66),(1350,63),(1390,61),
                       (1430,58),(1458,57),(1476,55),(1488,54),(1494,54)],
    },

    # ── Soybean (relatively stable commodity) ────────────────────────────────
    "Soybean": {
        "Nashik":     [(4500,600),(4480,610),(4510,595),(4540,590),(4560,585),
                       (4580,580),(4600,578),(4590,579),(4575,581),(4560,583),
                       (4545,585),(4530,587),(4520,589),(4510,590),(4505,591)],
        "Lasalgaon":  [(4450,550),(4430,560),(4460,545),(4490,540),(4510,535),
                       (4530,530),(4550,528),(4540,529),(4525,531),(4510,533),
                       (4495,535),(4480,537),(4470,539),(4460,540),(4455,541)],
        "Pune":       [(4600,300),(4580,305),(4610,295),(4640,290),(4660,285),
                       (4680,280),(4700,278),(4690,279),(4675,281),(4660,283),
                       (4645,285),(4630,287),(4620,289),(4610,290),(4605,291)],
        "Ahmednagar": [(4470,400),(4450,408),(4480,395),(4508,391),(4528,387),
                       (4548,383),(4568,381),(4558,382),(4543,384),(4528,386),
                       (4513,388),(4498,390),(4488,392),(4478,393),(4473,394)],
        "Solapur":    [(4400,380),(4380,388),(4410,375),(4438,371),(4458,367),
                       (4478,363),(4498,361),(4488,362),(4473,364),(4458,366),
                       (4443,368),(4428,370),(4418,372),(4408,373),(4403,374)],
        "Aurangabad": [(4480,420),(4460,428),(4490,415),(4518,411),(4538,407),
                       (4558,403),(4578,401),(4568,402),(4553,404),(4538,406),
                       (4523,408),(4508,410),(4498,412),(4488,413),(4483,414)],
        "Nagpur":     [(4520,500),(4500,510),(4530,495),(4558,491),(4578,487),
                       (4598,483),(4618,481),(4608,482),(4593,484),(4578,486),
                       (4563,488),(4548,490),(4538,492),(4528,493),(4523,494)],
        "Mumbai":     [(4700,150),(4680,153),(4710,147),(4738,143),(4758,139),
                       (4778,135),(4798,133),(4788,134),(4773,136),(4758,138),
                       (4743,140),(4728,142),(4718,144),(4708,145),(4703,146)],
    },

    # ── Cotton (MSP-linked, stable with seasonal variation) ───────────────────
    "Cotton": {
        "Nashik":     [(6200,400),(6220,395),(6180,405),(6160,410),(6140,415),
                       (6120,420),(6100,422),(6110,421),(6125,418),(6140,416),
                       (6160,413),(6175,411),(6185,409),(6195,407),(6200,406)],
        "Lasalgaon":  [(6100,360),(6120,355),(6080,365),(6060,370),(6040,375),
                       (6020,380),(6000,382),(6010,381),(6025,378),(6040,376),
                       (6060,373),(6075,371),(6085,369),(6095,367),(6100,366)],
        "Pune":       [(6400,200),(6420,197),(6380,203),(6360,207),(6340,211),
                       (6320,215),(6300,217),(6310,216),(6325,213),(6340,211),
                       (6360,208),(6375,206),(6385,204),(6395,202),(6400,201)],
        "Ahmednagar": [(6150,300),(6170,296),(6130,304),(6110,308),(6090,312),
                       (6070,316),(6050,318),(6060,317),(6075,314),(6090,312),
                       (6110,309),(6125,307),(6135,305),(6145,303),(6150,302)],
        "Solapur":    [(6050,280),(6070,276),(6030,284),(6010,288),(5990,292),
                       (5970,296),(5950,298),(5960,297),(5975,294),(5990,292),
                       (6010,289),(6025,287),(6035,285),(6045,283),(6050,282)],
        "Aurangabad": [(6250,320),(6270,316),(6230,324),(6210,328),(6190,332),
                       (6170,336),(6150,338),(6160,337),(6175,334),(6190,332),
                       (6210,329),(6225,327),(6235,325),(6245,323),(6250,322)],
        "Nagpur":     [(6300,450),(6320,445),(6280,455),(6260,460),(6240,465),
                       (6220,470),(6200,472),(6210,471),(6225,468),(6240,466),
                       (6260,463),(6275,461),(6285,459),(6295,457),(6300,456)],
        "Mumbai":     [(6600,100),(6620,98),(6580,102),(6560,105),(6540,108),
                       (6520,111),(6500,113),(6510,112),(6525,109),(6540,107),
                       (6560,104),(6575,102),(6585,100),(6595,98),(6600,97)],
    },

    # ── Wheat (MSP-supported, very stable) ───────────────────────────────────
    "Wheat": {
        "Nashik":     [(2100,800),(2105,795),(2095,805),(2098,802),(2102,798),
                       (2108,793),(2112,789),(2110,791),(2106,795),(2103,798),
                       (2100,800),(2098,802),(2096,804),(2094,806),(2092,808)],
        "Lasalgaon":  [(2080,720),(2085,715),(2075,725),(2078,722),(2082,718),
                       (2088,713),(2092,709),(2090,711),(2086,715),(2083,718),
                       (2080,720),(2078,722),(2076,724),(2074,726),(2072,728)],
        "Pune":       [(2200,400),(2205,397),(2195,403),(2198,401),(2202,398),
                       (2208,393),(2212,389),(2210,391),(2206,395),(2203,398),
                       (2200,400),(2198,402),(2196,404),(2194,406),(2192,408)],
        "Ahmednagar": [(2120,500),(2125,496),(2115,504),(2118,501),(2122,497),
                       (2128,492),(2132,488),(2130,490),(2126,494),(2123,497),
                       (2120,500),(2118,502),(2116,504),(2114,506),(2112,508)],
        "Solapur":    [(2090,450),(2095,446),(2085,454),(2088,451),(2092,447),
                       (2098,442),(2102,438),(2100,440),(2096,444),(2093,447),
                       (2090,450),(2088,452),(2086,454),(2084,456),(2082,458)],
        "Aurangabad": [(2130,480),(2135,476),(2125,484),(2128,481),(2132,477),
                       (2138,472),(2142,468),(2140,470),(2136,474),(2133,477),
                       (2130,480),(2128,482),(2126,484),(2124,486),(2122,488)],
        "Nagpur":     [(2150,550),(2155,546),(2145,554),(2148,551),(2152,547),
                       (2158,542),(2162,538),(2160,540),(2156,544),(2153,547),
                       (2150,550),(2148,552),(2146,554),(2144,556),(2142,558)],
        "Mumbai":     [(2300,200),(2305,198),(2295,202),(2298,201),(2302,198),
                       (2308,194),(2312,191),(2310,192),(2306,196),(2303,198),
                       (2300,200),(2298,202),(2296,204),(2294,205),(2292,207)],
    },

    # ── Rice (seasonal, varies by variety) ───────────────────────────────────
    "Rice": {
        "Nashik":     [(2200,600),(2210,595),(2190,605),(2180,610),(2170,615),
                       (2160,620),(2155,622),(2158,621),(2163,618),(2170,615),
                       (2178,612),(2185,609),(2190,607),(2196,605),(2200,604)],
        "Lasalgaon":  [(2100,540),(2110,535),(2090,545),(2080,550),(2070,555),
                       (2060,560),(2055,562),(2058,561),(2063,558),(2070,555),
                       (2078,552),(2085,549),(2090,547),(2096,545),(2100,544)],
        "Pune":       [(2400,300),(2410,297),(2390,303),(2380,307),(2370,311),
                       (2360,315),(2355,317),(2358,316),(2363,313),(2370,311),
                       (2378,308),(2385,306),(2390,304),(2396,302),(2400,301)],
        "Ahmednagar": [(2150,380),(2160,376),(2140,384),(2130,388),(2120,392),
                       (2110,396),(2105,398),(2108,397),(2113,394),(2120,392),
                       (2128,389),(2135,387),(2140,385),(2146,383),(2150,382)],
        "Solapur":    [(2050,340),(2060,336),(2040,344),(2030,348),(2020,352),
                       (2010,356),(2005,358),(2008,357),(2013,354),(2020,352),
                       (2028,349),(2035,347),(2040,345),(2046,343),(2050,342)],
        "Aurangabad": [(2180,360),(2190,356),(2170,364),(2160,368),(2150,372),
                       (2140,376),(2135,378),(2138,377),(2143,374),(2150,372),
                       (2158,369),(2165,367),(2170,365),(2176,363),(2180,362)],
        "Nagpur":     [(2300,480),(2310,476),(2290,484),(2280,488),(2270,492),
                       (2260,496),(2255,498),(2258,497),(2263,494),(2270,492),
                       (2278,489),(2285,487),(2290,485),(2296,483),(2300,482)],
        "Mumbai":     [(2600,150),(2610,148),(2590,152),(2580,155),(2570,158),
                       (2560,161),(2555,163),(2558,162),(2563,159),(2570,158),
                       (2578,155),(2585,153),(2590,151),(2596,150),(2600,149)],
    },

    # ── Potato (affordable staple, moderate volatility) ───────────────────────
    "Potato": {
        "Nashik":     [(800,700),(810,693),(790,707),(775,714),(760,721),
                       (748,725),(740,728),(745,726),(752,722),(760,718),
                       (770,714),(778,711),(784,709),(790,707),(795,706)],
        "Lasalgaon":  [(780,640),(790,633),(770,647),(755,654),(740,661),
                       (728,665),(720,668),(725,666),(732,662),(740,658),
                       (750,654),(758,651),(764,649),(770,647),(775,646)],
        "Pune":       [(950,350),(960,346),(940,354),(925,360),(910,366),
                       (898,370),(890,373),(895,371),(902,367),(910,364),
                       (920,360),(928,357),(934,355),(940,353),(945,352)],
        "Ahmednagar": [(820,430),(830,426),(810,434),(795,440),(780,446),
                       (768,450),(760,453),(765,451),(772,447),(780,444),
                       (790,440),(798,437),(804,435),(810,433),(815,432)],
        "Solapur":    [(760,400),(770,396),(750,404),(735,410),(720,416),
                       (708,420),(700,423),(705,421),(712,417),(720,414),
                       (730,410),(738,407),(744,405),(750,403),(755,402)],
        "Aurangabad": [(800,380),(810,376),(790,384),(775,390),(760,396),
                       (748,400),(740,403),(745,401),(752,397),(760,394),
                       (770,390),(778,387),(784,385),(790,383),(795,382)],
        "Nagpur":     [(840,500),(850,495),(830,505),(815,511),(800,517),
                       (788,521),(780,524),(785,522),(792,518),(800,515),
                       (810,511),(818,508),(824,506),(830,504),(835,503)],
        "Mumbai":     [(1100,180),(1110,178),(1090,182),(1075,185),(1060,188),
                       (1048,191),(1040,193),(1045,192),(1052,189),(1060,187),
                       (1070,184),(1078,182),(1084,180),(1090,179),(1095,178)],
    },

    # ── Chilli (high-value spice, volatile) ───────────────────────────────────
    "Chilli": {
        "Nashik":     [(8000,120),(8100,118),(7900,122),(7800,125),(7700,128),
                       (7650,130),(7600,132),(7650,131),(7700,129),(7750,127),
                       (7820,125),(7880,123),(7930,121),(7970,120),(8000,119)],
        "Lasalgaon":  [(7800,110),(7900,108),(7700,112),(7600,115),(7500,118),
                       (7450,120),(7400,122),(7450,121),(7500,119),(7550,117),
                       (7620,115),(7680,113),(7730,111),(7770,110),(7800,109)],
        "Pune":       [(8500,70),(8600,68),(8400,72),(8300,75),(8200,78),
                       (8150,80),(8100,82),(8150,81),(8200,79),(8250,77),
                       (8320,75),(8380,73),(8430,71),(8470,70),(8500,69)],
        "Ahmednagar": [(7900,90),(8000,88),(7800,92),(7700,95),(7600,98),
                       (7550,100),(7500,102),(7550,101),(7600,99),(7650,97),
                       (7720,95),(7780,93),(7830,91),(7870,90),(7900,89)],
        "Solapur":    [(7600,80),(7700,78),(7500,82),(7400,85),(7300,88),
                       (7250,90),(7200,92),(7250,91),(7300,89),(7350,87),
                       (7420,85),(7480,83),(7530,81),(7570,80),(7600,79)],
        "Aurangabad": [(7700,85),(7800,83),(7600,87),(7500,90),(7400,93),
                       (7350,95),(7300,97),(7350,96),(7400,94),(7450,92),
                       (7520,90),(7580,88),(7630,86),(7670,85),(7700,84)],
        "Nagpur":     [(8200,100),(8300,98),(8100,102),(8000,105),(7900,108),
                       (7850,110),(7800,112),(7850,111),(7900,109),(7950,107),
                       (8020,105),(8080,103),(8130,101),(8170,100),(8200,99)],
        "Mumbai":     [(9500,40),(9600,39),(9400,41),(9300,43),(9200,45),
                       (9150,46),(9100,47),(9150,46),(9200,45),(9250,44),
                       (9320,43),(9380,42),(9430,41),(9470,40),(9500,40)],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Build the PRICES dict from the raw data above
# Structure: PRICES[crop][market] = [list of 15 price records]
# ─────────────────────────────────────────────────────────────────────────────
PRICES: dict[str, dict[str, list[dict]]] = {}

for crop, markets_data in _RAW.items():
    PRICES[crop] = {}
    for market, day_series in markets_data.items():
        PRICES[crop][market] = [
            _price_row(modal, volume, idx, DATES_15[idx])
            for idx, (modal, volume) in enumerate(day_series)
        ]


# ─────────────────────────────────────────────────────────────────────────────
# BUYERS  (6 buyers who purchase agricultural produce)
# ─────────────────────────────────────────────────────────────────────────────
BUYERS: list[dict] = [
    {
        "id": "B001",
        "name": "Reliance Fresh Procurement",
        "type": "Processor",
        "crops_interested": ["Onion", "Potato", "Tomato"],
        "min_quantity": 50,    # minimum tonnes per order
        "max_quantity": 500,
        "location": "Mumbai",
        "district": "Mumbai",
        "state": "Maharashtra",
        "verified": True,
        "rating": 4.8,
        "contact": "procurement@reliancefresh.com",
        "preferred_grade": "A",
    },
    {
        "id": "B002",
        "name": "Sahyadri Farms Export",
        "type": "Exporter",
        "crops_interested": ["Onion", "Chilli", "Soybean"],
        "min_quantity": 100,
        "max_quantity": 1000,
        "location": "Nashik",
        "district": "Nashik",
        "state": "Maharashtra",
        "verified": True,
        "rating": 4.6,
        "contact": "exports@sahyadrifarms.com",
        "preferred_grade": "A",
    },
    {
        "id": "B003",
        "name": "Agro Star Commodity Traders",
        "type": "Trader",
        "crops_interested": ["Wheat", "Rice", "Soybean", "Cotton"],
        "min_quantity": 20,
        "max_quantity": 300,
        "location": "Ahmednagar",
        "district": "Ahmednagar",
        "state": "Maharashtra",
        "verified": True,
        "rating": 4.2,
        "contact": "+91-9876543210",
        "preferred_grade": "B",
    },
    {
        "id": "B004",
        "name": "Vidarbha Cotton Mills",
        "type": "Processor",
        "crops_interested": ["Cotton"],
        "min_quantity": 200,
        "max_quantity": 2000,
        "location": "Nagpur",
        "district": "Nagpur",
        "state": "Maharashtra",
        "verified": True,
        "rating": 4.5,
        "contact": "+91-7890123456",
        "preferred_grade": "A",
    },
    {
        "id": "B005",
        "name": "Spice Route India Pvt. Ltd.",
        "type": "Exporter",
        "crops_interested": ["Chilli", "Onion"],
        "min_quantity": 30,
        "max_quantity": 400,
        "location": "Aurangabad",
        "district": "Aurangabad",
        "state": "Maharashtra",
        "verified": False,
        "rating": 3.9,
        "contact": "+91-8765432109",
        "preferred_grade": "B",
    },
    {
        "id": "B006",
        "name": "Maharashtra Agro Processing Corp",
        "type": "Processor",
        "crops_interested": ["Tomato", "Potato", "Onion", "Chilli"],
        "min_quantity": 10,
        "max_quantity": 150,
        "location": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "verified": True,
        "rating": 4.0,
        "contact": "+91-9001234567",
        "preferred_grade": "B",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# FARMERS  (4 farmers registered on the platform)
# ─────────────────────────────────────────────────────────────────────────────
FARMERS: list[dict] = [
    {
        "id": "F001",
        "name": "Ramesh Patil",
        "location": "Lasalgaon",
        "district": "Nashik",
        "state": "Maharashtra",
        "crops": ["Onion", "Wheat"],
        "phone": "+91-9423100001",
        "land_acres": 12,
        "verified": True,
    },
    {
        "id": "F002",
        "name": "Sunita Deshmukh",
        "location": "Aurangabad",
        "district": "Aurangabad",
        "state": "Maharashtra",
        "crops": ["Cotton", "Soybean"],
        "phone": "+91-9423100002",
        "land_acres": 20,
        "verified": True,
    },
    {
        "id": "F003",
        "name": "Kishor Jadhav",
        "location": "Solapur",
        "district": "Solapur",
        "state": "Maharashtra",
        "crops": ["Tomato", "Chilli"],
        "phone": "+91-9423100003",
        "land_acres": 8,
        "verified": False,
    },
    {
        "id": "F004",
        "name": "Anita Shinde",
        "location": "Nagpur",
        "district": "Nagpur",
        "state": "Maharashtra",
        "crops": ["Rice", "Soybean", "Wheat"],
        "phone": "+91-9423100004",
        "land_acres": 15,
        "verified": True,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# FPOs  (Farmer Producer Organisations)
# ─────────────────────────────────────────────────────────────────────────────
FPOS: list[dict] = [
    {
        "id": "FPO001",
        "name": "Nashik Onion Growers FPO",
        "location": "Nashik",
        "district": "Nashik",
        "state": "Maharashtra",
        "members": 340,
        "crops": ["Onion", "Tomato"],
        "contact": "+91-9012345678",
        "registered": True,
        "turnover_lakh": 480,   # annual turnover in lakh INR
    },
    {
        "id": "FPO002",
        "name": "Vidarbha Cotton & Soya FPO",
        "location": "Nagpur",
        "district": "Nagpur",
        "state": "Maharashtra",
        "members": 520,
        "crops": ["Cotton", "Soybean"],
        "contact": "+91-9023456789",
        "registered": True,
        "turnover_lakh": 720,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# LOTS  (Produce lots listed by farmers for sale)
# ─────────────────────────────────────────────────────────────────────────────
LOTS: list[dict] = [
    {
        "id": "L001",
        "farmer_id": "F001",          # Ramesh Patil
        "crop": "Onion",
        "quantity": 80,               # in tonnes
        "unit": "tonnes",
        "grade": "A",
        "location": "Lasalgaon",
        "district": "Nashik",
        "state": "Maharashtra",
        "expected_price": 1300,       # INR per quintal
        "status": "active",           # active / matched / sold / cancelled
        "description": "Premium Nashik red onion, freshly harvested, well sorted.",
        "images": [],
        "created_at": (date.today() - timedelta(days=3)).isoformat(),
    },
    {
        "id": "L002",
        "farmer_id": "F002",          # Sunita Deshmukh
        "crop": "Cotton",
        "quantity": 250,
        "unit": "tonnes",
        "grade": "A",
        "location": "Aurangabad",
        "district": "Aurangabad",
        "state": "Maharashtra",
        "expected_price": 6300,
        "status": "matched",
        "description": "Long staple cotton, moisture <8%, ready for ginning.",
        "images": [],
        "created_at": (date.today() - timedelta(days=5)).isoformat(),
    },
    {
        "id": "L003",
        "farmer_id": "F003",          # Kishor Jadhav
        "crop": "Tomato",
        "quantity": 25,
        "unit": "tonnes",
        "grade": "B",
        "location": "Solapur",
        "district": "Solapur",
        "state": "Maharashtra",
        "expected_price": 750,
        "status": "active",
        "description": "Round tomatoes, suitable for processing.",
        "images": [],
        "created_at": (date.today() - timedelta(days=1)).isoformat(),
    },
    {
        "id": "L004",
        "farmer_id": "F004",          # Anita Shinde
        "crop": "Soybean",
        "quantity": 120,
        "unit": "tonnes",
        "grade": "A",
        "location": "Nagpur",
        "district": "Nagpur",
        "state": "Maharashtra",
        "expected_price": 4600,
        "status": "sold",
        "description": "Yellow soybean, moisture <10%, good oil content.",
        "images": [],
        "created_at": (date.today() - timedelta(days=10)).isoformat(),
    },
    {
        "id": "L005",
        "farmer_id": "F001",          # Ramesh Patil (second lot)
        "crop": "Wheat",
        "quantity": 40,
        "unit": "tonnes",
        "grade": "B",
        "location": "Lasalgaon",
        "district": "Nashik",
        "state": "Maharashtra",
        "expected_price": 2100,
        "status": "active",
        "description": "Lokwan wheat variety, good milling quality.",
        "images": [],
        "created_at": (date.today() - timedelta(days=2)).isoformat(),
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# OFFERS  (Buyer offers to farmers on their lots)
# ─────────────────────────────────────────────────────────────────────────────
OFFERS: list[dict] = [
    {
        "id": "O001",
        "lot_id": "L001",
        "buyer_id": "B002",           # Sahyadri Farms Export
        "farmer_id": "F001",
        "price": 1280,                # INR per quintal offered
        "quantity": 80,               # tonnes
        "status": "pending",          # pending / accepted / rejected / expired
        "message": "Interested in your onion lot for export to Malaysia.",
        "created_at": (date.today() - timedelta(days=2)).isoformat(),
        "expires_at": (date.today() + timedelta(days=3)).isoformat(),
    },
    {
        "id": "O002",
        "lot_id": "L002",
        "buyer_id": "B004",           # Vidarbha Cotton Mills
        "farmer_id": "F002",
        "price": 6250,
        "quantity": 200,
        "status": "accepted",
        "message": "Grade A cotton required for our new season production.",
        "created_at": (date.today() - timedelta(days=4)).isoformat(),
        "expires_at": (date.today() + timedelta(days=1)).isoformat(),
    },
    {
        "id": "O003",
        "lot_id": "L003",
        "buyer_id": "B006",           # Maharashtra Agro Processing
        "farmer_id": "F003",
        "price": 700,
        "quantity": 20,
        "status": "pending",
        "message": "We need tomatoes for our paste plant in Pune.",
        "created_at": (date.today() - timedelta(days=1)).isoformat(),
        "expires_at": (date.today() + timedelta(days=5)).isoformat(),
    },
    {
        "id": "O004",
        "lot_id": "L004",
        "buyer_id": "B003",           # Agro Star Traders
        "farmer_id": "F004",
        "price": 4550,
        "quantity": 120,
        "status": "rejected",
        "message": "Looking for bulk soybean for futures market.",
        "created_at": (date.today() - timedelta(days=9)).isoformat(),
        "expires_at": (date.today() - timedelta(days=3)).isoformat(),
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTIONS  (Confirmed deals progressing through stages)
# ─────────────────────────────────────────────────────────────────────────────
# Valid stages (in order):
# offer_created → offer_accepted → produce_dispatched →
# payment_pending → payment_received → completed
TRANSACTIONS: list[dict] = [
    {
        "id": "T001",
        "offer_id": "O002",
        "lot_id": "L002",
        "farmer_id": "F002",
        "buyer_id": "B004",
        "crop": "Cotton",
        "quantity": 200,
        "price_per_quintal": 6250,
        "total_amount": 6250 * 200 * 10,   # price×qty×10 (1 tonne = 10 quintal)
        "current_stage": "produce_dispatched",
        "stage_history": [
            {"stage": "offer_created",    "timestamp": (date.today() - timedelta(days=4)).isoformat()},
            {"stage": "offer_accepted",   "timestamp": (date.today() - timedelta(days=3)).isoformat()},
            {"stage": "produce_dispatched","timestamp": (date.today() - timedelta(days=1)).isoformat()},
        ],
        "created_at": (date.today() - timedelta(days=4)).isoformat(),
    },
    {
        "id": "T002",
        "offer_id": "O001",
        "lot_id": "L001",
        "farmer_id": "F001",
        "buyer_id": "B002",
        "crop": "Onion",
        "quantity": 60,
        "price_per_quintal": 1280,
        "total_amount": 1280 * 60 * 10,
        "current_stage": "offer_accepted",
        "stage_history": [
            {"stage": "offer_created",  "timestamp": (date.today() - timedelta(days=2)).isoformat()},
            {"stage": "offer_accepted", "timestamp": (date.today() - timedelta(days=1)).isoformat()},
        ],
        "created_at": (date.today() - timedelta(days=2)).isoformat(),
    },
    {
        "id": "T003",
        "offer_id": "O004",
        "lot_id": "L004",
        "farmer_id": "F004",
        "buyer_id": "B003",
        "crop": "Soybean",
        "quantity": 120,
        "price_per_quintal": 4600,
        "total_amount": 4600 * 120 * 10,
        "current_stage": "completed",
        "stage_history": [
            {"stage": "offer_created",     "timestamp": (date.today() - timedelta(days=10)).isoformat()},
            {"stage": "offer_accepted",    "timestamp": (date.today() - timedelta(days=9)).isoformat()},
            {"stage": "produce_dispatched","timestamp": (date.today() - timedelta(days=7)).isoformat()},
            {"stage": "payment_pending",   "timestamp": (date.today() - timedelta(days=5)).isoformat()},
            {"stage": "payment_received",  "timestamp": (date.today() - timedelta(days=3)).isoformat()},
            {"stage": "completed",         "timestamp": (date.today() - timedelta(days=2)).isoformat()},
        ],
        "created_at": (date.today() - timedelta(days=10)).isoformat(),
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# STORAGE FACILITIES  (Cold storage / warehouses near major mandis)
# ─────────────────────────────────────────────────────────────────────────────
STORAGE: list[dict] = [
    {
        "id": "S001",
        "name": "Nashik Cold Storage Complex",
        "location": "Nashik",
        "district": "Nashik",
        "state": "Maharashtra",
        "type": "Cold Storage",
        "total_capacity_tonnes": 5000,
        "available_capacity_tonnes": 1200,
        "rate_per_tonne_per_day": 4.5,   # INR
        "crops_supported": ["Onion", "Potato", "Tomato"],
        "contact": "+91-9988776655",
    },
    {
        "id": "S002",
        "name": "Aurangabad Agri Warehouse",
        "location": "Aurangabad",
        "district": "Aurangabad",
        "state": "Maharashtra",
        "type": "Dry Warehouse",
        "total_capacity_tonnes": 8000,
        "available_capacity_tonnes": 3500,
        "rate_per_tonne_per_day": 2.0,
        "crops_supported": ["Cotton", "Soybean", "Wheat"],
        "contact": "+91-9876600001",
    },
    {
        "id": "S003",
        "name": "Nagpur Grain Silo",
        "location": "Nagpur",
        "district": "Nagpur",
        "state": "Maharashtra",
        "type": "Silo",
        "total_capacity_tonnes": 12000,
        "available_capacity_tonnes": 4000,
        "rate_per_tonne_per_day": 1.5,
        "crops_supported": ["Wheat", "Rice", "Soybean"],
        "contact": "+91-9765432100",
    },
    {
        "id": "S004",
        "name": "Pune Multi-Commodity Hub",
        "location": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "type": "Cold Storage",
        "total_capacity_tonnes": 3000,
        "available_capacity_tonnes": 600,
        "rate_per_tonne_per_day": 5.0,
        "crops_supported": ["Tomato", "Potato", "Onion", "Chilli"],
        "contact": "+91-9654321000",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# GRIEVANCES  (Complaints / disputes raised by farmers)
# ─────────────────────────────────────────────────────────────────────────────
GRIEVANCES: list[dict] = [
    {
        "id": "G001",
        "farmer_id": "F003",
        "transaction_id": None,          # not linked to a transaction
        "issue_type": "Price Dispute",
        "description": "Buyer at Solapur mandi charged extra commission of ₹50 per quintal not agreed in contract.",
        "status": "open",                # open / under_review / resolved
        "created_at": (date.today() - timedelta(days=2)).isoformat(),
        "resolved_at": None,
        "resolution_note": None,
    },
    {
        "id": "G002",
        "farmer_id": "F001",
        "transaction_id": "T002",
        "issue_type": "Payment Delay",
        "description": "Payment not received within agreed 7-day window after dispatch.",
        "status": "under_review",
        "created_at": (date.today() - timedelta(days=1)).isoformat(),
        "resolved_at": None,
        "resolution_note": "Team has contacted the buyer. Resolution expected in 48 hours.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATIONS  (In-app notifications for demo users)
# ─────────────────────────────────────────────────────────────────────────────
NOTIFICATIONS: list[dict] = [
    {
        "id": "N001",
        "user_id": "F001",
        "type": "offer_received",
        "title": "New Offer on Lot L001",
        "body": "Sahyadri Farms Export has offered ₹1,280/quintal for your Onion lot.",
        "read": False,
        "created_at": (date.today() - timedelta(days=2)).isoformat(),
    },
    {
        "id": "N002",
        "user_id": "F002",
        "type": "transaction_update",
        "title": "Produce Dispatched – T001",
        "body": "Your Cotton lot (200 tonnes) has been marked as dispatched to Vidarbha Cotton Mills.",
        "read": True,
        "created_at": (date.today() - timedelta(days=1)).isoformat(),
    },
    {
        "id": "N003",
        "user_id": "F003",
        "type": "price_alert",
        "title": "Tomato Price Rising in Pune",
        "body": "Tomato modal price in Pune mandi has risen 8% in the last 3 days.",
        "read": False,
        "created_at": date.today().isoformat(),
    },
    {
        "id": "N004",
        "user_id": "F004",
        "type": "payment_received",
        "title": "Payment Received – T003",
        "body": "₹55,20,000 has been credited for your Soybean transaction.",
        "read": True,
        "created_at": (date.today() - timedelta(days=3)).isoformat(),
    },
    {
        "id": "N005",
        "user_id": "F001",
        "type": "grievance_update",
        "title": "Grievance G002 Under Review",
        "body": "Your payment delay complaint is now under review by our team.",
        "read": False,
        "created_at": (date.today() - timedelta(days=1)).isoformat(),
    },
]
