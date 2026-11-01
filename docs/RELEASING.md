# Release checklist / 发布检查清单

This is a future manual process. No remote repository, tag, release or CI job is created by these instructions.

## Prepare locally / 本地准备

- [ ] Finish the intended functionality and resolve or clearly document remaining limitations.
- [ ] Synchronize documents using [MAINTENANCE.md](MAINTENANCE.md).
- [ ] Confirm `VERSION`, root README and both full READMEs agree. Initial candidate: 0.1.0.
- [ ] Record user-visible changes in `CHANGELOG.md`; keep publication status accurate.
- [ ] Run applicable tests and update `VERIFICATION.md` with actual date, environment and results.
- [ ] Manually inspect the synthetic demo in a local browser; never upload the private live report as a preview.
- [ ] Choose repository visibility and, if publishing as open source, have the owner select and add a license. A license is not supplied automatically.

## Review the upload / 检查上传内容

Review the staged file list and content before the first commit/push. Use an explicit allowlist of source/docs rather than blindly adding the entire directory. Confirm `.reports/`, `.qa/`, credentials, logs, databases, CSV exports and environment files are absent. Check any already tracked files too; ignore rules do not untrack them.

Create an empty GitHub repository for the first push. If following this route, do not initialize it with a second README/license/gitignore. Replace example repository URLs with your own; never put a password or token into a remote URL. Use your normal Git authentication flow.

## Publish when authorized / 正式发布

After the final commit is reviewed, push its branch. A GitHub Release is separate from uploading source. When actually publishing the release, record the real release date/status, commit those documentation changes, then create an annotated tag matching `VERSION` and push that tag. Create release notes from `CHANGELOG.md`. Do not upload `.reports/`, `.qa/` or a zip of the entire working folder as release assets.

Verify the remote file list, README links, tag and release notes. For subsequent updates, use focused commits/PRs and the next appropriate version. Do not use force push to resolve an unexpected first-push conflict without understanding the remote history.
