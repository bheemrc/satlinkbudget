"""Tests for link budget results."""

import pytest
import matplotlib
matplotlib.use("Agg")

from satlinkbudget.budget._results import LinkBudgetResult


class TestLinkBudgetResult:
    @pytest.fixture
    def closing_result(self):
        return LinkBudgetResult(
            eirp_dbw=8.0,
            free_space_path_loss_db=140.0,
            figure_of_merit_db_per_k=-13.0,
            c_over_n0_db_hz=55.0,
            eb_n0_db=15.0,
            required_eb_n0_db=9.6,
            margin_db=5.4,
            data_rate_bps=9600,
            system_noise_temp_k=500.0,
        )

    def test_link_closes(self, closing_result):
        assert closing_result.link_closes is True

    def test_link_does_not_close(self):
        r = LinkBudgetResult(margin_db=-2.0)
        assert r.link_closes is False

    def test_waterfall_returns_figure(self, closing_result):
        fig = closing_result.plot_waterfall()
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_summary_keys(self, closing_result):
        s = closing_result.summary()
        assert "margin_db" in s
        assert "eirp_dbw" in s
        assert "link_closes" in s

    def test_to_text_format(self, closing_result):
        text = closing_result.to_text()
        assert "LINK BUDGET ANALYSIS" in text
        assert "YES" in text  # link closes
