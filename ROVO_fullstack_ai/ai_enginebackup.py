import sqlite3
import json
import re
import random
from pathlib import Path

from geo import nearest_pickup


HILL_DESTINATIONS = {
    "lonavala", "khandala", "mahabaleshwar", "matheran", "igatpuri",
    "panchgani", "bhandardara", "malsej", "lavasa", "amboli"
}

LONG_TRIP_DESTINATIONS = {
    "ratnagiri", "goa", "pune", "nashik", "shirdi", "alibaug",
    "kolhapur", "satara", "mahabaleshwar", "lonavala", "igatpuri"
}


class RovoAI:
    MODEL_VERSION = 4

    def __init__(self, db_path, model_path):
        self.db_path = Path(db_path)
        self.model_path = Path(model_path)

        self.sessions = {}
        self.model = None
        self.model_info = {}

        self._load_or_train()

    def reset(self, sid):
        self.sessions.pop(sid, None)

    # ============================================================
    # DATABASE
    # ============================================================

    def _cars(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row

        rows = [
            dict(r)
            for r in con.execute(
                "SELECT * FROM cars WHERE approved=1"
            )
        ]

        con.close()

        for r in rows:
            try:
                r["locations"] = json.loads(
                    r["locations_json"]
                )
            except Exception:
                r["locations"] = (
                    [r["location"]]
                    if r.get("location")
                    else []
                )

        return rows

    # ============================================================
    # CAR CAPABILITY
    # ============================================================

    def _hill_fit(self, c):
        score = (
            c["highway"] * 0.55
            + c["comfort"] * 0.15
        )

        if c["category"] == "SUV":
            score += 2.0

        elif c["category"] == "MUV":
            score += 0.8

        elif c["category"] == "Hatchback":
            score -= 0.8

        name = (
            f'{c["brand"]} {c["model"]}'
            .lower()
        )

        capable = [
            "thar",
            "scorpio",
            "xuv",
            "nexon",
            "creta",
            "seltos",
            "grand vitara",
            "hyryder",
            "elevate",
            "compass",
            "harrier",
            "safari",
            "fortuner",
            "taigun",
            "kushaq",
            "hector"
        ]

        city_oriented = [
            "comet",
            "kwid",
            "alto",
            "celerio"
        ]

        if any(x in name for x in capable):
            score += 1.2

        if any(x in name for x in city_oriented):
            score -= 1.5

        return max(
            1.0,
            min(
                10.0,
                score
            )
        )

    def _desc(self, c):
        return (
            f'{c["brand"]} {c["model"]} '
            f'{c["category"]} '
            f'{c["fuel"]} '
            f'{c["transmission"]} '
            f'{c["seats"]} seats '
            f'price {c["price"]} '
            f'efficiency {c["efficiency"]} '
            f'comfort {c["comfort"]} '
            f'highway {c["highway"]} '
            f'hills {self._hill_fit(c):.1f} '
            f'bags {c["bags"]} '
            f'year {c["year"]}'
        )

    # ============================================================
    # SYNTHETIC TRAINING DATA
    # ============================================================

    def _synthetic(self, cars):
        templates = [

            (
                "cheap fuel efficient city car",
                {
                    "price": 5,
                    "eff": 4
                }
            ),

            (
                "comfortable automatic for parents on a long highway trip",
                {
                    "comfort": 5,
                    "highway": 5,
                    "auto": 4
                }
            ),

            (
                "7 people luggage outstation",
                {
                    "seats": 7,
                    "bags": 4,
                    "highway": 5
                }
            ),

            (
                "electric city car",
                {
                    "ev": 5,
                    "eff": 4
                }
            ),

            (
                "premium luxury automatic business trip",
                {
                    "luxury": 5,
                    "auto": 4,
                    "comfort": 4
                }
            ),

            (
                "CNG low running cost",
                {
                    "cng": 5,
                    "price": 4,
                    "eff": 4
                }
            ),

            (
                "diesel SUV hills highway",
                {
                    "diesel": 5,
                    "suv": 4,
                    "highway": 4,
                    "hills": 6
                }
            ),

            (
                "hybrid comfortable efficient",
                {
                    "hybrid": 5,
                    "comfort": 4,
                    "eff": 5
                }
            ),

            (
                "small budget hatchback",
                {
                    "hatch": 5,
                    "price": 6
                }
            ),

            (
                "family 5 people 3 bags",
                {
                    "seats": 5,
                    "bags": 3,
                    "comfort": 4
                }
            ),

            (
                "lonavala hilly roads fuel efficient",
                {
                    "hills": 7,
                    "eff": 5,
                    "highway": 3
                }
            ),

            (
                "mahabaleshwar family automatic hills",
                {
                    "hills": 7,
                    "comfort": 4,
                    "auto": 4,
                    "highway": 3
                }
            ),

            (
                "ratnagiri family luggage",
                {
                    "highway": 5,
                    "comfort": 4,
                    "bags": 3
                }
            ),

            (
                "5 seater automatic under 3000",
                {
                    "seats": 5,
                    "auto": 5,
                    "budget": 3000
                }
            ),

            (
                "premium EV weekend",
                {
                    "ev": 5,
                    "luxury": 4,
                    "comfort": 4
                }
            ),

            (
                "older affordable car",
                {
                    "old": 4,
                    "price": 6
                }
            ),

            (
                "need something cheaper",
                {
                    "price": 8
                }
            ),

            (
                "better mileage",
                {
                    "eff": 8
                }
            ),

            (
                "comfort matters more",
                {
                    "comfort": 8
                }
            ),

            (
                "nearest car close to my location",
                {
                    "distance": 8
                }
            ),

            (
                "automatic suv close to me",
                {
                    "auto": 4,
                    "suv": 4,
                    "distance": 6
                }
            ),

            (
                "five people hills luggage comfort",
                {
                    "seats": 5,
                    "hills": 6,
                    "bags": 3,
                    "comfort": 4
                }
            ),
        ]

        X = []
        y = []

        rng = random.Random(42)

        for _ in range(24):

            for prompt, w in templates:

                for c in rng.sample(
                    cars,
                    min(
                        26,
                        len(cars)
                    )
                ):

                    s = 5.0

                    s += (
                        w.get("eff", 0)
                        * (c["efficiency"] - 5)
                        / 5
                    )

                    s += (
                        w.get("comfort", 0)
                        * (c["comfort"] - 5)
                        / 5
                    )

                    s += (
                        w.get("highway", 0)
                        * (c["highway"] - 5)
                        / 5
                    )

                    s += (
                        w.get("hills", 0)
                        * (self._hill_fit(c) - 5)
                        / 5
                    )

                    s += (
                        w.get("price", 0)
                        * (
                            1
                            - min(
                                c["price"],
                                12000
                            )
                            / 12000
                        )
                    )

                    if (
                        w.get("auto")
                        and c["transmission"] == "Automatic"
                    ):
                        s += 2.0

                    if (
                        w.get("ev")
                        and c["fuel"] == "Electric"
                    ):
                        s += 2.3

                    if (
                        w.get("cng")
                        and c["fuel"] == "CNG"
                    ):
                        s += 2.3

                    if (
                        w.get("diesel")
                        and c["fuel"] == "Diesel"
                    ):
                        s += 2.3

                    if (
                        w.get("hybrid")
                        and c["fuel"] == "Hybrid"
                    ):
                        s += 2.3

                    if (
                        w.get("luxury")
                        and c["category"] == "Luxury"
                    ):
                        s += 2.0

                    if (
                        w.get("suv")
                        and c["category"] == "SUV"
                    ):
                        s += 1.5

                    if (
                        w.get("hatch")
                        and c["category"] == "Hatchback"
                    ):
                        s += 1.5

                    if w.get("seats"):
                        s += (
                            2.0
                            if c["seats"] >= w["seats"]
                            else -5.0
                        )

                    if w.get("bags"):
                        s += (
                            1.5
                            if c["bags"] >= w["bags"]
                            else -2.0
                        )

                    if w.get("budget"):
                        s += (
                            2.5
                            if c["price"] <= w["budget"]
                            else -4.0
                        )

                    if w.get("old"):
                        if c["year"] <= 2021:
                            s += 1.2

                    X.append(
                        prompt
                        + " [CAR] "
                        + self._desc(c)
                    )

                    y.append(s)

        return X, y

    # ============================================================
    # MODEL
    # ============================================================

    def _load_or_train(self):

        try:

            import joblib

            if self.model_path.exists():

                b = joblib.load(
                    self.model_path
                )

                self.model = (
                    b["pipeline"]
                )

                self.model_info = (
                    b.get(
                        "info",
                        {}
                    )
                )

                if (
                    self.model_info.get("version")
                    == self.MODEL_VERSION
                ):
                    return

        except Exception:
            pass

        self.train()

    def train(self):

        from sklearn.pipeline import Pipeline

        from sklearn.feature_extraction.text import (
            TfidfVectorizer
        )

        from sklearn.linear_model import Ridge

        from sklearn.model_selection import (
            train_test_split
        )

        from sklearn.metrics import (
            mean_absolute_error,
            r2_score
        )

        import joblib

        X, y = self._synthetic(
            self._cars()
        )

        Xtr, Xte, ytr, yte = (
            train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42
            )
        )

        pipe = Pipeline([

            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=16000,
                    sublinear_tf=True
                )
            ),

            (
                "reg",
                Ridge(
                    alpha=1.15
                )
            )

        ])

        pipe.fit(
            Xtr,
            ytr
        )

        p = pipe.predict(
            Xte
        )

        self.model_info = {

            "version":
                self.MODEL_VERSION,

            "type":
                "TF-IDF + Ridge hybrid ranker v4",

            "training_examples":
                len(X),

            "mae":
                round(
                    float(
                        mean_absolute_error(
                            yte,
                            p
                        )
                    ),
                    3
                ),

            "r2":
                round(
                    float(
                        r2_score(
                            yte,
                            p
                        )
                    ),
                    3
                ),

            "features": [
                "price",
                "efficiency",
                "comfort",
                "highway",
                "hills",
                "distance",
                "seats",
                "fuel",
                "transmission",
                "luggage"
            ]
        }

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            {
                "pipeline":
                    pipe,

                "info":
                    self.model_info
            },
            self.model_path
        )

        self.model = pipe

    # ============================================================
    # CONVERSATION STATE
    # ============================================================

    def _state(self):

        return {

            "ctx": {},

            "weights": {

                "price": 1.0,

                "comfort": 1.0,

                "eff": 1.0,

                "highway": 1.0,

                "hills": 1.0,

                "space": 1.0,

                "distance": 1.0
            },

            "last": []
        }

    # ============================================================
    # TEXT NORMALISATION
    # ============================================================

    def _normalise_text(
        self,
        text
    ):

        t = (
            text
            or ""
        ).lower().strip()

        replacements = {

            "ppl":
                "people",

            "pax":
                "passengers",

            "automtic":
                "automatic",

            "automaticc":
                "automatic",

            "manuel":
                "manual",

            "diesal":
                "diesel",

            "effecient":
                "efficient",

            "efficent":
                "efficient",

            "milage":
                "mileage",

            "lonvala":
                "lonavala",

            "lonavla":
                "lonavala",

            "ratnagri":
                "ratnagiri",

            "lugage":
                "luggage",

            "cheper":
                "cheaper",

            "cheapr":
                "cheaper",

            "near by":
                "nearby",

            "7-seater":
                "7 seater",

            "5-seater":
                "5 seater"
        }

        for old, new in replacements.items():

            t = t.replace(
                old,
                new
            )

        return re.sub(
            r"\s+",
            " ",
            t
        ).strip()

    # ============================================================
    # CLEAR / OVERRIDE PREFERENCES
    # ============================================================

    def _clear_if_requested(
        self,
        t,
        c
    ):

        if any(
            x in t
            for x in [
                "any fuel",
                "no fuel preference",
                "fuel doesn't matter",
                "fuel doesnt matter"
            ]
        ):

            c.pop(
                "fuel",
                None
            )

        if any(
            x in t
            for x in [
                "any transmission",
                "transmission doesn't matter",
                "transmission doesnt matter",
                "either transmission"
            ]
        ):

            c.pop(
                "transmission",
                None
            )

        if any(
            x in t
            for x in [
                "any category",
                "any type",
                "category doesn't matter",
                "category doesnt matter"
            ]
        ):

            c.pop(
                "category",
                None
            )

        if any(
            x in t
            for x in [
                "any seats",
                "seat count doesn't matter",
                "seat count doesnt matter"
            ]
        ):

            for key in [
                "exact_seats",
                "min_seats",
                "max_seats"
            ]:

                c.pop(
                    key,
                    None
                )

        if any(
            x in t
            for x in [
                "no budget",
                "ignore budget",
                "budget doesn't matter",
                "budget doesnt matter"
            ]
        ):

            c.pop(
                "budget",
                None
            )

            c.pop(
                "soft_price_target",
                None
            )

    # ============================================================
    # PASSENGER PARSER
    # ============================================================

    def _parse_passengers(
        self,
        t,
        c
    ):

        patterns = [

            (
                r'\b(\d{1,2})\s*'
                r'(?:people|persons|passengers|adults|members|friends)\b'
            ),

            (
                r'\b(?:we are|we\'re|there are|for)\s*'
                r'(\d{1,2})\s*'
                r'(?:people|persons|passengers|adults)?\b'
            )
        ]

        for pattern in patterns:

            m = re.search(
                pattern,
                t
            )

            if m:

                n = int(
                    m.group(1)
                )

                if 1 <= n <= 20:

                    c["passengers"] = n

                    return

    # ============================================================
    # SEATING PARSER
    # ============================================================

    def _parse_seating(
        self,
        t,
        c
    ):

        # Minimum
        m = re.search(
            r'\b(?:at least|minimum|min)\s*'
            r'(\d{1,2})\s*'
            r'(?:seat|seats|seater)?\b',
            t
        )

        if m:

            c["min_seats"] = int(
                m.group(1)
            )

            c.pop(
                "exact_seats",
                None
            )

            c.pop(
                "max_seats",
                None
            )

            return


        # Maximum
        m = re.search(
            r'\b(?:maximum|max|at most|up to)\s*'
            r'(\d{1,2})\s*'
            r'(?:seat|seats|seater)\b',
            t
        )

        if m:

            c["max_seats"] = int(
                m.group(1)
            )

            c.pop(
                "exact_seats",
                None
            )

            c.pop(
                "min_seats",
                None
            )

            return


        # Exact
        m = re.search(

            r'\b(?:'
            r'only\s+|'
            r'exactly\s+|'
            r'must\s+be\s+|'
            r'should\s+be\s+(?:only\s+)?'
            r')?'

            r'(\d{1,2})\s*'

            r'(?:seater|seat|seats)\b',

            t
        )

        if m:

            c["exact_seats"] = int(
                m.group(1)
            )

            c.pop(
                "min_seats",
                None
            )

            c.pop(
                "max_seats",
                None
            )

    # ============================================================
    # CONTEXT UPDATE
    # ============================================================

    def _update(
        self,
        text,
        state
    ):

        t = self._normalise_text(
            text
        )


        if any(
            x in t
            for x in [

                "start over",

                "reset chat",

                "new search",

                "clear preferences",

                "new trip",

                "start again"
            ]
        ):

            return (
                self._state(),
                True
            )


        c = dict(
            state["ctx"]
        )

        w = dict(
            state["weights"]
        )


        self._clear_if_requested(
            t,
            c
        )


        # ========================================================
        # PASSENGERS + VEHICLE SEATS ARE DIFFERENT
        # ========================================================

        self._parse_passengers(
            t,
            c
        )

        self._parse_seating(
            t,
            c
        )


        # ========================================================
        # BUDGET
        # ========================================================

        m = re.search(

            r'\b(?:'
            r'under|'
            r'below|'
            r'budget(?: of)?|'
            r'around|'
            r'max(?:imum)?|'
            r'up to|'
            r'upto'
            r')\s*'

            r'₹?\s*'

            r'([\d,]{3,6})\b',

            t
        )

        if m:

            c["budget"] = int(
                m.group(1)
                .replace(
                    ",",
                    ""
                )
            )

            c.pop(
                "soft_price_target",
                None
            )


        # ========================================================
        # TRANSMISSION
        # ========================================================

        if re.search(
            r'\b(?:automatic|auto)\b',
            t
        ):

            c["transmission"] = (
                "Automatic"
            )


        if re.search(
            r'\bmanual\b',
            t
        ):

            c["transmission"] = (
                "Manual"
            )


        # ========================================================
        # FUEL
        # Latest explicit fuel wins
        # ========================================================

        fuel_hits = []


        for fuel in [

            "petrol",

            "diesel",

            "cng",

            "electric",

            "hybrid"
        ]:

            pattern = (

                r'\bev\b'

                if fuel == "electric"

                else rf'\b{fuel}\b'
            )


            for m2 in re.finditer(
                pattern,
                t
            ):

                fuel_hits.append(
                    (
                        m2.start(),
                        fuel
                    )
                )


        if "electric" in t:

            fuel_hits.append(
                (
                    t.rfind(
                        "electric"
                    ),
                    "electric"
                )
            )


        if fuel_hits:

            _, fuel = max(
                fuel_hits,
                key=lambda x: x[0]
            )

            c["fuel"] = (
                fuel.capitalize()
            )


        # ========================================================
        # CATEGORY
        # ========================================================

        category_hits = []


        for cat in [

            "suv",

            "sedan",

            "hatchback",

            "muv",

            "luxury"
        ]:

            for m2 in re.finditer(
                rf'\b{cat}\b',
                t
            ):

                category_hits.append(
                    (
                        m2.start(),
                        cat
                    )
                )


        if category_hits:

            _, cat = max(
                category_hits,
                key=lambda x: x[0]
            )


            c["category"] = (

                cat.upper()

                if cat in (
                    "suv",
                    "muv"
                )

                else cat.capitalize()
            )


        # ========================================================
        # EXCLUDED FUELS
        # ========================================================

        if re.search(
            r'\b(?:no|not|avoid)\s+diesel\b',
            t
        ):

            c["exclude_fuel"] = (
                "Diesel"
            )


        if re.search(
            r'\b(?:no|not|avoid)\s+petrol\b',
            t
        ):

            c["exclude_fuel"] = (
                "Petrol"
            )


        if re.search(
            r'\b(?:no|not|avoid)\s+cng\b',
            t
        ):

            c["exclude_fuel"] = (
                "CNG"
            )


        if re.search(
            r'\b(?:no|not|avoid)\s+(?:electric|ev)\b',
            t
        ):

            c["exclude_fuel"] = (
                "Electric"
            )


        # ========================================================
        # LUGGAGE
        # ========================================================

        if any(
            x in t
            for x in [

                "luggage",

                "bags",

                "suitcase",

                "suitcases",

                "boot space"
            ]
        ):

            c["luggage"] = True


        m = re.search(
            r'\b(\d{1,2})\s*'
            r'(?:bags|bag|suitcases|suitcase)\b',
            t
        )


        if m:

            c["bags_needed"] = int(
                m.group(1)
            )

            c["luggage"] = True


        # ========================================================
        # LONG TRIPS
        # ========================================================

        if (

            any(
                x in t
                for x in [

                    "long drive",

                    "highway",

                    "outstation",

                    "road trip",

                    "long trip"
                ]
            )

            or any(
                d in t
                for d in LONG_TRIP_DESTINATIONS
            )

        ):

            c["long_trip"] = True


            w["highway"] = max(

                w["highway"],

                2.2
            )


        # ========================================================
        # HILLS
        # ========================================================

        if (

            any(
                x in t
                for x in [

                    "hilly",

                    "hills",

                    "hill road",

                    "hilly roads",

                    "ghat",

                    "ghats",

                    "mountain",

                    "mountains",

                    "steep"
                ]
            )

            or any(
                d in t
                for d in HILL_DESTINATIONS
            )

        ):

            c["hills"] = True


            w["hills"] = max(

                w["hills"],

                3.2
            )


            w["highway"] = max(

                w["highway"],

                1.8
            )


        # ========================================================
        # COMFORT
        # ========================================================

        if any(
            x in t
            for x in [

                "parents",

                "elderly",

                "grandmother",

                "grandfather",

                "family",

                "comfortable",

                "comfort"
            ]
        ):

            c["comfort"] = True


            w["comfort"] = max(

                w["comfort"],

                2.0
            )


        # ========================================================
        # EFFICIENCY
        # ========================================================

        if any(
            x in t
            for x in [

                "mileage",

                "fuel efficient",

                "fuel-efficient",

                "economy",

                "efficient",

                "running cost"
            ]
        ):

            c["efficiency"] = True


            w["eff"] = max(

                w["eff"],

                2.2
            )


        # ========================================================
        # NEARBY
        # ========================================================

        if any(
            x in t
            for x in [

                "near me",

                "nearby",

                "close to me",

                "close from my location",

                "close to my location",

                "closest",

                "nearest"
            ]
        ):

            c["nearby"] = True


            w["distance"] = max(

                w["distance"],

                4.2
            )


        # ========================================================
        # FOLLOW-UP: CHEAPER
        # ========================================================

        if any(
            x in t
            for x in [

                "cheaper",

                "less expensive",

                "lower price",

                "save money",

                "budget option"
            ]
        ):

            w["price"] = min(

                5.0,

                w["price"]
                + 2.8
            )


            c["price_sensitive"] = True


            if state["last"]:

                c["soft_price_target"] = int(

                    min(
                        x["price"]
                        for x
                        in state["last"][:3]
                    )

                    * 0.88
                )


        # ========================================================
        # FOLLOW-UP: COMFORT
        # ========================================================

        if any(
            x in t
            for x in [

                "more comfortable",

                "comfort matters more",

                "better comfort"
            ]
        ):

            w["comfort"] = min(

                5.0,

                w["comfort"]
                + 2.8
            )


        # ========================================================
        # FOLLOW-UP: MILEAGE
        # ========================================================

        if any(
            x in t
            for x in [

                "better mileage",

                "mileage matters more",

                "more fuel efficient",

                "better fuel economy"
            ]
        ):

            w["eff"] = min(

                5.0,

                w["eff"]
                + 3.0
            )


        # ========================================================
        # FOLLOW-UP: SPACE
        # ========================================================

        if any(
            x in t
            for x in [

                "more space",

                "more spacious",

                "bigger boot",

                "more luggage space"
            ]
        ):

            w["space"] = min(

                5.0,

                w["space"]
                + 2.5
            )


        # ========================================================
        # FOLLOW-UP: HILLS
        # ========================================================

        if any(
            x in t
            for x in [

                "better for hills",

                "more capable in hills",

                "hill capability"
            ]
        ):

            w["hills"] = min(

                5.0,

                w["hills"]
                + 3.0
            )


        state["ctx"] = c

        state["weights"] = w


        return (
            state,
            False
        )

    # ============================================================
    # HARD FILTERS
    # ============================================================

    def _filter(
        self,
        cars,
        c
    ):

        out = [

            car

            for car in cars

            if car["available"]
        ]


        # Actual people:
        # car may have MORE seats than passengers.
        if c.get("passengers"):

            out = [

                car

                for car in out

                if car["seats"]
                >= c["passengers"]
            ]


        # Exact requested seat count.
        if c.get("exact_seats"):

            out = [

                car

                for car in out

                if car["seats"]
                == c["exact_seats"]
            ]


        if c.get("min_seats"):

            out = [

                car

                for car in out

                if car["seats"]
                >= c["min_seats"]
            ]


        if c.get("max_seats"):

            out = [

                car

                for car in out

                if car["seats"]
                <= c["max_seats"]
            ]


        if c.get("bags_needed") is not None:

            out = [

                car

                for car in out

                if car["bags"]
                >= c["bags_needed"]
            ]


        if c.get("budget"):

            out = [

                car

                for car in out

                if car["price"]
                <= c["budget"]
            ]


        if c.get("transmission"):

            out = [

                car

                for car in out

                if car["transmission"]
                == c["transmission"]
            ]


        if c.get("fuel"):

            out = [

                car

                for car in out

                if car["fuel"]
                == c["fuel"]
            ]


        if c.get("exclude_fuel"):

            out = [

                car

                for car in out

                if car["fuel"]
                != c["exclude_fuel"]
            ]


        if c.get("category"):

            out = [

                car

                for car in out

                if car["category"]
                == c["category"]
            ]


        return out

    # ============================================================
    # CONSTRAINT SUMMARY
    # ============================================================

    def _constraint_summary(
        self,
        c
    ):

        bits = []


        if c.get("passengers"):

            bits.append(
                f'{c["passengers"]} passengers'
            )


        if c.get("exact_seats"):

            bits.append(
                f'exactly {c["exact_seats"]} seats'
            )


        elif c.get("min_seats"):

            bits.append(
                f'at least {c["min_seats"]} seats'
            )


        elif c.get("max_seats"):

            bits.append(
                f'at most {c["max_seats"]} seats'
            )


        if c.get("fuel"):

            bits.append(
                c["fuel"]
            )


        if c.get("transmission"):

            bits.append(
                c["transmission"]
            )


        if c.get("category"):

            bits.append(
                c["category"]
            )


        if c.get("budget"):

            bits.append(
                f'under ₹{c["budget"]:,}/day'
            )


        if c.get("bags_needed") is not None:

            bits.append(
                f'{c["bags_needed"]} bags'
            )


        return ", ".join(
            bits
        )

    # ============================================================
    # LOGICAL CONTRADICTIONS
    # ============================================================

    def _impossible_reason(
        self,
        c
    ):

        if (

            c.get("passengers")

            and c.get("exact_seats")

            and c["exact_seats"]
            < c["passengers"]

        ):

            return (

                f'You have {c["passengers"]} passengers, '

                f'but requested exactly '

                f'{c["exact_seats"]} seats. '

                f'The vehicle needs at least '

                f'{c["passengers"]} seats.'
            )


        if (

            c.get("passengers")

            and c.get("max_seats")

            and c["max_seats"]
            < c["passengers"]

        ):

            return (

                f'You have {c["passengers"]} passengers, '

                f'but set a maximum of '

                f'{c["max_seats"]} seats.'
            )


        return None

    # ============================================================
    # CHAT
    # ============================================================

    def chat(
        self,
        sid,
        message,
        current_car_id=None,
        user_location=None
    ):

        cars = self._cars()


        state = self.sessions.get(

            sid,

            self._state()
        )


        state, reset = self._update(

            message,

            state
        )


        self.sessions[sid] = state


        if reset:

            return {

                "answer":
                    "Preferences cleared. Tell me about the new trip.",

                "cars":
                    [],

                "context":
                    {},

                "priorities":
                    state["weights"],

                "model":
                    self.model_info
            }


        c = state["ctx"]

        w = state["weights"]


        # ========================================================
        # LOGICAL IMPOSSIBILITY
        # ========================================================

        impossible = (
            self._impossible_reason(
                c
            )
        )


        if impossible:

            return {

                "answer":

                    impossible

                    + " Change either the passenger count "
                    + "or seating requirement.",

                "cars":
                    [],

                "context":
                    c,

                "priorities":
                    w,

                "model":
                    self.model_info
            }


        # ========================================================
        # USER LOCATION
        # ========================================================

        if (

            user_location

            and user_location.get("lat")
            is not None

        ):

            c["user_location_label"] = (

                user_location.get(
                    "label"
                )

                or user_location.get(
                    "nearest_hub"
                )
            )


        # ========================================================
        # HARD FILTERING
        # ========================================================

        candidates = self._filter(

            cars,

            c
        )


        # IMPORTANT:
        # We no longer silently remove category/fuel/etc.
        # If nothing matches, tell the user honestly.
        if not candidates:

            summary = (
                self._constraint_summary(
                    c
                )
            )


            answer = (

                "I couldn't find a car that matches all "
                "of those requirements at the same time."
            )


            if summary:

                answer += (

                    f" Current hard requirements: "
                    f"{summary}."
                )


            answer += (

                " Try increasing the budget or relaxing "
                "one of the seat, fuel, transmission, "
                "category, or luggage constraints."
            )


            return {

                "answer":
                    answer,

                "cars":
                    [],

                "context":
                    c,

                "priorities":
                    w,

                "model":
                    self.model_info
            }


        # ========================================================
        # DISTANCE + HILL FEATURES
        # ========================================================

        enriched = []


        for car in candidates:

            near = (

                nearest_pickup(

                    car["locations"],

                    user_location
                )

                if user_location

                else None
            )


            car = dict(
                car
            )


            car["nearest_pickup"] = (

                near["name"]

                if near

                else car["location"]
            )


            car["distance_km"] = (

                near["distance_km"]

                if near

                else None
            )


            car["hill_fit"] = round(

                self._hill_fit(
                    car
                ),

                1
            )


            enriched.append(
                car
            )


        candidates = enriched


        # ========================================================
        # NORMALIZATION VALUES
        # ========================================================

        prices = [

            x["price"]

            for x in candidates
        ]


        lo = min(
            prices
        )


        hi = max(
            prices
        )


        span = max(

            1,

            hi - lo
        )


        known_dist = [

            x["distance_km"]

            for x in candidates

            if x["distance_km"]
            is not None
        ]


        max_dist = (

            max(
                known_dist
            )

            if known_dist

            else 1
        )


        # ========================================================
        # ML PROMPT
        # ========================================================

        prompt = (

            message

            + " "

            + " ".join(

                f"{k}:{v}"

                for k, v
                in c.items()
            )
        )


        ml = self.model.predict([

            prompt

            + " [CAR] "

            + self._desc(x)

            for x in candidates
        ])


        # ========================================================
        # HYBRID RANKING
        # ========================================================

        scored = []


        for car, m in zip(
            candidates,
            ml
        ):

            price_score = (

                1

                - (
                    car["price"]
                    - lo
                )

                / span
            )


            distance_score = (

                0.5

                if car["distance_km"]
                is None

                else max(

                    0,

                    1

                    - car["distance_km"]

                    / max(
                        1,
                        max_dist
                    )
                )
            )


            s = (
                float(m)
                * 0.72
            )


            s += (

                price_score

                * 4

                * w["price"]
            )


            s += (

                (
                    car["comfort"]
                    / 10
                )

                * 3

                * w["comfort"]
            )


            s += (

                (
                    car["efficiency"]
                    / 10
                )

                * 3

                * w["eff"]
            )


            s += (

                (
                    car["highway"]
                    / 10
                )

                * 3

                * w["highway"]
            )


            s += (

                (
                    car["hill_fit"]
                    / 10
                )

                * 4

                * w["hills"]
            )


            s += (

                min(

                    1,

                    car["bags"]
                    / 4
                )

                * 2

                * w["space"]
            )


            # Real pickup distance.
            if (

                user_location

                and car["distance_km"]
                is not None

            ):

                s += (

                    distance_score

                    * 4

                    * w["distance"]
                )


            # Follow-up: cheaper.
            target = (
                c.get(
                    "soft_price_target"
                )
            )


            if target:

                if (
                    car["price"]
                    <= target
                ):

                    s += 5

                else:

                    s -= min(

                        6,

                        (
                            car["price"]
                            - target
                        )
                        / 500
                    )


            if (

                c.get("luggage")

                and car["bags"]
                >= 3

            ):

                s += 2


            if (

                c.get("hills")

                and car["hill_fit"]
                >= 8

            ):

                s += 2.5


            # Weak hill cars are strongly penalised.
            if (

                c.get("hills")

                and car["hill_fit"]
                < 5.5

            ):

                s -= 5.0


            if (

                c.get("exact_seats")

                and car["seats"]
                == c["exact_seats"]

            ):

                s += 1.0


            scored.append(
                (
                    car,
                    s
                )
            )


        # ========================================================
        # REMOVE DUPLICATE MODELS
        # ========================================================

        best = {}


        for car, s in scored:

            k = (

                car["brand"]
                .lower(),

                car["model"]
                .lower()
            )


            if (

                k not in best

                or s
                > best[k][1]

            ):

                best[k] = (
                    car,
                    s
                )


        ranked = sorted(

            best.values(),

            key=lambda x: x[1],

            reverse=True

        )[:6]


        if not ranked:

            return {

                "answer":

                    "I found matching inventory, but none "
                    "could be ranked. Try changing one preference.",

                "cars":
                    [],

                "context":
                    c,

                "priorities":
                    w,

                "model":
                    self.model_info
            }


        # ========================================================
        # RESULT CARDS
        # ========================================================

        result = []


        top = (
            ranked[0][1]
        )


        bot = (
            ranked[-1][1]
        )


        den = max(

            0.001,

            top - bot
        )


        for car, s in ranked:

            why = []


            if (

                c.get("hills")

                and car["hill_fit"]
                >= 7

            ):

                why.append(

                    f'hill fit '
                    f'{car["hill_fit"]}/10'
                )


            if (

                c.get("efficiency")

                and car["efficiency"]
                >= 8

            ):

                why.append(
                    "good efficiency"
                )


            if c.get("passengers"):

                why.append(

                    f'fits '
                    f'{c["passengers"]} passengers'
                )


            if c.get("exact_seats"):

                why.append(

                    f'exactly '
                    f'{c["exact_seats"]} seats'
                )


            elif c.get("min_seats"):

                why.append(

                    f'at least '
                    f'{c["min_seats"]} seats'
                )


            elif c.get("max_seats"):

                why.append(

                    f'maximum '
                    f'{c["max_seats"]} seats'
                )


            if (

                c.get("luggage")

                and car["bags"]
                >= 3

            ):

                why.append(
                    "useful luggage space"
                )


            if (

                w["comfort"]
                >= 2

                and car["comfort"]
                >= 8

            ):

                why.append(
                    "good comfort"
                )


            if (

                w["highway"]
                >= 2

                and car["highway"]
                >= 8

            ):

                why.append(
                    "good highway fit"
                )


            if (

                c.get("nearby")

                and car["distance_km"]
                is not None

            ):

                why.append(

                    f'{car["distance_km"]} km '
                    f'to pickup'
                )


            if (
                w["price"]
                >= 2.5
            ):

                why.append(
                    "lower rental cost"
                )


            if not why:

                why.append(
                    "strong overall balance"
                )


            result.append({

                **{
                    k: car[k]

                    for k in [

                        "id",

                        "brand",

                        "model",

                        "category",

                        "seats",

                        "price",

                        "fuel",

                        "transmission",

                        "efficiency",

                        "comfort",

                        "highway",

                        "rating",

                        "year",

                        "bags"
                    ]
                },


                "location":
                    car["nearest_pickup"],


                "nearest_pickup":
                    car["nearest_pickup"],


                "distance_km":
                    car["distance_km"],


                "hill_fit":
                    car["hill_fit"],


                "match":
                    round(

                        78

                        + (
                            (
                                s - bot
                            )

                            / den
                        )

                        * 18
                    ),


                "why":
                    ", ".join(
                        why[:3]
                    )
            })


        state["last"] = result

        self.sessions[sid] = state


        # ========================================================
        # NATURAL RESPONSE
        # ========================================================

        lead = (

            "I ranked the fleet using "
            "your current trip context."
        )


        if (

            c.get("nearby")

            and user_location

            and user_location.get("lat")
            is not None

        ):

            lead = (

                "I re-ranked by real pickup distance from "

                f'{user_location.get("label") or "your location"} '

                "while keeping your other trip requirements."
            )


        elif (

            c.get("hills")

            and c.get("efficiency")

        ):

            lead = (

                "I balanced hill capability with fuel efficiency "

                "instead of simply choosing the most efficient car."
            )


        elif (
            w["price"]
            >= 3
        ):

            lead = (

                "I re-ranked toward cheaper cars while keeping "

                "your earlier hard requirements."
            )


        elif (
            w["comfort"]
            >= 3
        ):

            lead = (

                "I re-ranked toward comfort while keeping "

                "the rest of your trip context."
            )


        elif (
            w["eff"]
            >= 3
        ):

            lead = (

                "I re-ranked toward better mileage while keeping "

                "your earlier requirements."
            )


        t = result[0]


        return {

            "answer":

                f'{lead} '

                f'My strongest match now is the '

                f'{t["brand"]} {t["model"]}: '

                f'{t["why"]}.',


            "cars":
                result,


            "context":
                c,


            "priorities":
                w,


            "model":
                self.model_info
        }