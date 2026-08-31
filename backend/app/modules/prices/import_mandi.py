import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.database import SessionLocal
from app.models import (
    Crop,
    IngestionRun,
    Market,
    PriceObservation,
    PriceSource,
)

JSON_FILE = Path(__file__).resolve().parents[3] / "mandi_final_100.json"


def make_record_id(record):
    fields = [
        record.get("state", ""),
        record.get("district", ""),
        record.get("market", ""),
        record.get("commodity", ""),
        record.get("variety", ""),
        record.get("grade", ""),
        record.get("arrival_date", ""),
        record.get("min_price", ""),
        record.get("max_price", ""),
        record.get("modal_price", ""),
    ]

    raw = "|".join(str(value) for value in fields)

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def parse_date(value):
    if not value:
        return None

    return datetime.strptime(
        value,
        "%d/%m/%Y",
    ).date()


def load_first_100():
    print(f"Reading: {JSON_FILE}")

    if not JSON_FILE.exists():
        raise FileNotFoundError(f"Could not find {JSON_FILE}")

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8-sig",
    ) as file:
        payload = json.load(file)

    records = payload.get("records", [])

    if not isinstance(records, list):
        raise RuntimeError("Invalid JSON format: records is not a list")

    # HARD LIMIT: only first 100.
    records = records[:100]

    print(f"Loaded {len(records)} records from JSON.")

    return records


def import_records(records):

    db = SessionLocal()

    inserted = 0
    skipped = 0
    rejected = 0

    try:
        # ---------------------------------------------------------
        # SOURCE
        # ---------------------------------------------------------

        source = db.query(PriceSource).filter(PriceSource.name == "data.gov.in Mandi Prices").first()

        if not source:
            source = PriceSource(
                name="data.gov.in Mandi Prices",
                url=("https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"),
                adapter="data_gov_mandi",
                is_active=True,
            )

            db.add(source)
            db.flush()

        # ---------------------------------------------------------
        # INGESTION RUN
        # ---------------------------------------------------------

        ingestion = IngestionRun(
            source_id=source.id,
            status="running",
            records_fetched=len(records),
            records_ok=0,
            records_rejected=0,
            parser_version="mandi-v1",
        )

        db.add(ingestion)
        db.flush()

        # ---------------------------------------------------------
        # PROCESS 100 RECORDS
        # ---------------------------------------------------------

        for index, record in enumerate(
            records,
            start=1,
        ):
            try:
                commodity = str(record.get("commodity", "")).strip()

                market_name = str(record.get("market", "")).strip()

                district = str(record.get("district", "")).strip()

                state = str(record.get("state", "")).strip()

                arrival_date = parse_date(record.get("arrival_date"))

                min_price = float(record.get("min_price", 0))

                modal_price = float(record.get("modal_price", 0))

                max_price = float(record.get("max_price", 0))

                # -------------------------------------------------
                # VALIDATION
                # -------------------------------------------------

                if not commodity:
                    raise ValueError("Missing commodity")

                if not market_name:
                    raise ValueError("Missing market")

                if not district:
                    raise ValueError("Missing district")

                if not state:
                    raise ValueError("Missing state")

                if not arrival_date:
                    raise ValueError("Missing arrival date")

                if modal_price <= 0:
                    raise ValueError("Invalid modal price")

                # -------------------------------------------------
                # CROP
                # -------------------------------------------------

                crop = db.query(Crop).filter(Crop.name == commodity).first()

                if not crop:
                    crop = Crop(
                        name=commodity,
                        unit="quintal",
                    )

                    db.add(crop)
                    db.flush()

                # -------------------------------------------------
                # MARKET
                # -------------------------------------------------

                market = (
                    db.query(Market)
                    .filter(
                        Market.name == market_name,
                        Market.district == district,
                        Market.state == state,
                    )
                    .first()
                )

                if not market:
                    market = Market(
                        name=market_name,
                        district=district,
                        state=state,
                        market_type="APMC",
                        is_active=True,
                    )

                    db.add(market)
                    db.flush()

                # -------------------------------------------------
                # DUPLICATE CHECK
                # -------------------------------------------------

                source_record_id = make_record_id(record)

                existing = (
                    db.query(PriceObservation)
                    .filter(
                        PriceObservation.crop_id == crop.id,
                        PriceObservation.market_id == market.id,
                        PriceObservation.price_date == arrival_date,
                        PriceObservation.source_id == source.id,
                    )
                    .first()
                )

                if existing:
                    skipped += 1

                    print(f"[{index}/100] SKIPPED {commodity} | {market_name}")

                    continue

                # -------------------------------------------------
                # PRICE OBSERVATION
                # -------------------------------------------------

                observation = PriceObservation(
                    crop_id=crop.id,
                    market_id=market.id,
                    price_date=arrival_date,
                    min_price=min_price,
                    modal_price=modal_price,
                    max_price=max_price,
                    # API doesn't provide volume.
                    volume_tonnes=None,
                    source_id=source.id,
                    source_record_id=source_record_id,
                    source_url=("https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"),
                    retrieved_at=datetime.now(timezone.utc),
                    ingestion_run_id=ingestion.id,
                    parser_version="mandi-v1",
                    normalization_version="v1",
                    quality_status="MEDIUM",
                )

                db.add(observation)

                inserted += 1

                print(f"[{index}/100] {commodity} | {market_name} | ₹{modal_price}")

            except Exception as exc:
                rejected += 1

                print(f"[{index}/100] REJECTED: {exc}")

        # ---------------------------------------------------------
        # FINISH
        # ---------------------------------------------------------

        ingestion.records_ok = inserted

        ingestion.records_rejected = rejected

        ingestion.status = "completed"

        ingestion.finished_at = datetime.now(timezone.utc)

        db.commit()

        print()
        print("=" * 50)
        print("IMPORT COMPLETE")
        print("=" * 50)

        print(f"Fetched : {len(records)}")

        print(f"Inserted: {inserted}")

        print(f"Skipped : {skipped}")

        print(f"Rejected: {rejected}")

        print("=" * 50)

    except Exception:
        db.rollback()

        raise

    finally:
        db.close()


def main():

    records = load_first_100()

    import_records(records)


if __name__ == "__main__":
    main()
