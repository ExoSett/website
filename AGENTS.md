# Website release agreement

Follow README.md validation requirements and ../modelling/docs/releasing-sketch.md
for Sketch integration. Test the complete assembled _site with modelling/sketch's
npm run test:release before deployment; Vite development tests are insufficient.
Copy all embedded build output. Run scripts/test_build_site.py for packaging changes.
Deploy the tested artifact without rebuilding and record both repository SHAs.
Report unrun checks and distinguish local changes from deployed changes.
The user already runs production smoke checks; do not duplicate that monitoring.
Require the integration build on PRs through GitHub branch rules; verify the actual
setting before claiming merge protection. Preserve failure evidence and the prior
successful release artifact for rollback.
