from __future__ import annotations

import asyncio

from verideploy.config import get_settings
from verideploy.observability.telemetry import configure_telemetry
from verideploy.observability.logging import configure_logging
from verideploy.releases.repository import SqlAlchemyReleaseRiskRepository
from verideploy.releases.service import ReleaseRiskService
from workers.investigation.release_risk_worker import run_kafka_worker


async def main() -> None:
    settings = get_settings()
    configure_telemetry(settings, service_name="verideploy-release-risk-worker")
    configure_logging(settings.log_level)
    repository = SqlAlchemyReleaseRiskRepository(
        settings.database_url,
        create_schema=settings.app_env == "development",
    )
    service = ReleaseRiskService(repository, settings.require_human_approval_at_risk_score)
    await run_kafka_worker(service, settings.kafka_brokers)


if __name__ == "__main__":
    asyncio.run(main())
