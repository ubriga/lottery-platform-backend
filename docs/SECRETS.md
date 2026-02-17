## DATA_ARCHIVE_PAT

To enable scheduled ingestion into the companion data repo, add a fine-grained PAT as a GitHub Actions secret:

- Repository: `lottery-platform-backend`
- Secret name: `DATA_ARCHIVE_PAT`
- Token permissions: **Contents: Read and write**
- Repository access: only `ubriga/lottery-data-archive`

The workflow that uses it is `.github/workflows/ingest_and_publish.yml`.
