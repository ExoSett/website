#!/usr/bin/env python3
"""Run all ExoSett website validation checks."""

from __future__ import annotations

import validate_site
import validate_structured_data


def main() -> int:
    site_result = validate_site.main()
    structured_data_result = validate_structured_data.main()
    return 1 if site_result or structured_data_result else 0


if __name__ == "__main__":
    raise SystemExit(main())
