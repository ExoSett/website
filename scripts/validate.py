#!/usr/bin/env python3
"""Run ExoSett-specific checks. Use npm run check for the complete validation."""

from __future__ import annotations

import validate_site
import validate_structured_data
import sync_navigation


def main() -> int:
    site_result = validate_site.main()
    structured_data_result = validate_structured_data.main()
    navigation_result = sync_navigation.main(check=True)
    return 1 if site_result or structured_data_result or navigation_result else 0


if __name__ == "__main__":
    raise SystemExit(main())
