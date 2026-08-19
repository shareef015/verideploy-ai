# ADR-0007 — PostgreSQL/pgvector Schema Authority

**Status:** Accepted

## Decision

Use Alembic migrations as the schema authority for canonical PostgreSQL tables. Use PostgreSQL pgvector for semantic vectors, HNSW cosine indexing for the Phase 12 vector index, explicit tenant filters in repositories, and RLS as a second isolation layer.

Runtime `metadata.create_all()` is not permitted for canonical Phase 12 tables. Temporary cumulative tables from earlier phases remain until explicit later migrations replace them.

Embedding dimension is a migration/index decision, not an arbitrary runtime switch. A model/dimension change requires re-embedding into a new compatible index.
