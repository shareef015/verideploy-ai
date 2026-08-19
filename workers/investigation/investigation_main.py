from __future__ import annotations

import asyncio
import os

from verideploy.config import get_settings
from verideploy.observability.telemetry import configure_telemetry
from verideploy.investigations.repository import SqlAlchemyInvestigationRepository
from verideploy.investigations.service import InvestigationService
from workers.investigation.investigation_worker import run_kafka_worker


def main() -> None:
    settings = get_settings()
    configure_telemetry(settings, service_name="verideploy-investigation-worker")
    database_url = os.getenv("INVESTIGATION_DATABASE_URL", settings.database_url)
    repository = SqlAlchemyInvestigationRepository(database_url, create_schema=settings.app_env in {"development", "test"})
    asyncio.run(run_kafka_worker(InvestigationService(repository), settings.kafka_brokers))


if __name__ == "__main__":
    main()
