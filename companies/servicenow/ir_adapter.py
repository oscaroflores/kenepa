from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceNowIRAdapter:
    base_url: str = "https://investors.servicenow.com/"

    def quarterly_results_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/financials/quarterly-results/default.aspx"

    def locate_earnings_release(self, quarter: str) -> dict:
        return {
            "quarter": quarter,
            "status": "manual_required",
            "message": "IR scraping is intentionally not automated in the MVP. Use SEC 8-K exhibits first, then attach manual source URL if needed.",
        }
