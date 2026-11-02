# Release process / 发布流程

`VERSION` is authoritative; release tags must be `v` plus that exact value. User authorization is required to publish; the current task explicitly requests Releases. Do not rewrite published tags.

## Prepare

1. Update both READMEs, root summary, changelog, work log, installation and release notes. Record actual checks in VERIFICATION.md; never invent release dates or signing status.
2. Review an explicit source/docs allowlist. Exclude `.reports/`, `.qa/`, build outputs, credentials, config, logs, databases and real usage. The repository is MIT-licensed; bundled font licensing is SIL OFL and third-party notices are copied into packages.
3. Install build dependencies in an isolated environment: `python -m pip install -r requirements-build.txt`. `python -B build_tools/build.py --prepare-only` fetches the pinned Google Fonts Git blobs, validates blob integrity and derives a regular TrueType font. Build-time downloads occur only on the builder, never in installed apps.
4. Run `python -B -m unittest discover -s tests -v` and `node tests/test_dashboard.cjs`. Tests use synthetic fixtures; CLI fixtures disable update checks. Manually inspect the synthetic dashboard; DOM tests do not prove layout.
5. `python -B build_tools/build.py` on the target OS builds a one-folder app, exercises a real guarded worker and packages the result. Windows requires Inno Setup 6; macOS uses hdiutil; Linux uses dpkg-deb. Local `--bundle-only` can validate the standalone app without installer tooling.

## CI and publication

`.github/workflows/release.yml` builds natively on Windows x64, macOS Intel/ARM64 and Linux x64/ARM64 for pushes, pull requests and manual dispatch. Each job tests Python/JS, bundles the runtime/font, and exercises all nine standalone outputs; Windows also installs, exercises and uninstalls its package. Hosted runners contain public source and synthetic fixtures only.

Review branch CI before merging. Push a matching version tag only when ready. After **all five** native builds succeed, the publish job verifies all eight packages, creates SHA256SUMS.txt, creates a draft Release, uploads the complete asset set, then publishes. Failed builds never publish a partial release. An interrupted upload can leave a draft requiring maintainer cleanup/retry; do not recreate a public release with different binaries under the same tag.

Windows trusted signing is optional until configured; see [WINDOWS_TRUST.md](WINDOWS_TRUST.md). `REQUIRE_WINDOWS_SIGNING=true` blocks unsigned publication. If signing is configured, launcher/setup/temp copies/uninstaller signature and timestamp validation must pass. Unsigned packages must be labeled in notes. macOS builds currently have no Developer ID notarization.

Finally verify the public Release assets, checksums, version and current release API. Record actual CI and publication evidence in WORKLOG/VERIFICATION, without real user data. GitHub source archives are not installation packages.
