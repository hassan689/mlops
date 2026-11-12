from datetime import datetime, timezone
from typing import Any

from airflow.decorators import dag, task
from airflow.providers.mongo.hooks.mongo import MongoHook
import requests

BASE_CURRENCY = "EUR"
TARGET_CURRENCIES = ("USD", "GBP", "JPY")
API_URL = "https://api.frankfurter.dev/v2/rates"
REQUEST_TIMEOUT_SECONDS = 30

@dag(
    dag_id="currency_exchange_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 2},
    tags=["etl", "mongodb", "frankfurter"],
)
def currency_etl_pipeline():

    @task
    def extract_rates() -> list[dict[str, Any]]:
        """Extract raw rates from Frankfurter API."""
        response = requests.get(
            API_URL,
            params={
                "base": BASE_CURRENCY,
                "quotes": ",".join(TARGET_CURRENCIES),
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Frankfurter API returned an unexpected response shape")
        return payload

    @task
    def transform_rates(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform raw API data into the required document schema."""
        transformed_records = []
        retrieved_at = datetime.now(timezone.utc).isoformat()

        for item in raw_data:
            record = {
                "base_currency": item["base"],
                "target_currency": item["quote"],
                "exchange_rate": item["rate"],
                "rate_date": item["date"],
                "source": "Frankfurter API",
                "retrieved_at": retrieved_at
            }
            transformed_records.append(record)

        return transformed_records

    @task
    def load_to_mongodb(transformed_data):
        """Load transformed data into MongoDB."""
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client['currency_db']
        collection = db['exchange_rates']

        if transformed_data:
            collection.insert_many(transformed_data)
            print(f"Inserted {len(transformed_data)} records.")

    raw = extract_rates()
    transformed = transform_rates(raw)
    load_to_mongodb(transformed)
44
currency_etl_pipeline()