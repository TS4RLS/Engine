"""The in-app changelog renderer must handle Date Versioning headings."""
from src.gui import theme


def test_sort_sections_with_date_version_headings():
    md = (
        "## v26.10.23-1\n\n### Fixed\n\n- a\n\n### Added\n\n- b\n\n"
        "## v26.10.23\n\n### Security\n\n- c\n\n### Changed\n\n- d\n"
    )
    out = theme.sort_changelog_sections(md).splitlines()
    assert out[0] == "## v26.10.23-1"
    assert out.index("### Added") < out.index("### Fixed")
    assert "## v26.10.23" in out
    assert out.index("### Changed") < out.index("### Security")
