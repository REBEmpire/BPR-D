# Procedural Memory: Syncing Static Content to Database on Render

**Context:**
Building a gamification layer on top of a static Markdown-based Next.js site. Need to track "points" for content that exists as files.

**Pattern:**
1.  **Database:** Use Render Postgres.
2.  **Migration:** Run a migration script (`node scripts/migrate.js`) as part of the `build` command. Ensure it checks for `DATABASE_URL` existence to avoid breaking local builds.
3.  **Content Sync:** Create a sync script (`node scripts/sync-gamification.js`) that:
    - Scans the file system (Markdown files).
    - Parses metadata (e.g., Author).
    - Upserts records into the Database (e.g., "Quest Completed").
    - Updates aggregate stats (Points).
    - Runs during `build` *after* migration.

**Benefits:**
- Keeps the "Source of Truth" in Git (Markdown files).
- Adds dynamic capabilities (Leaderboards, Stats) without a complex CMS.
- Idempotent scripts ensure data consistency on every deploy.

**Caveats:**
- Requires `DATABASE_URL` to be available at build time (or runtime if using Server Actions).
- Local development requires a local DB or connection to remote (via proxy).
