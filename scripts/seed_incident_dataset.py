from __future__ import annotations
import asyncio, json
from pathlib import Path
from sqlalchemy.ext.asyncio import async_sessionmaker
from verideploy.config import get_settings
from verideploy.database.session import DatabaseManager
from verideploy.incidents.repository import SqlAlchemyIncidentDatasetRepository
from verideploy.incidents.schemas import IncidentDataset
from verideploy.incidents.validation import validate_incident_dataset

ROOT = Path(__file__).resolve().parents[1]

async def main() -> None:
    dataset = IncidentDataset.model_validate(json.loads((ROOT / "data/incidents/nexuspay-incidents.json").read_text()))
    report = validate_incident_dataset(dataset)
    if not report.valid:
        raise RuntimeError(f"dataset validation failed: {report.errors}")
    manager = DatabaseManager(get_settings().database_url)
    try:
        repo = SqlAlchemyIncidentDatasetRepository(async_sessionmaker(manager.engine, expire_on_commit=False))
        count = await repo.upsert_dataset(dataset)
        print(json.dumps({"upserted": count, "dataset_sha256": dataset.dataset_sha256}))
    finally:
        await manager.dispose()

if __name__ == "__main__":
    asyncio.run(main())
