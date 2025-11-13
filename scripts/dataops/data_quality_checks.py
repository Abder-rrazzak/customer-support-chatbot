#!/usr/bin/env python3
"""DataOps data quality validation."""

import pandas as pd
import great_expectations as gx
from pathlib import Path

def validate_conversation_data():
    """Validate conversation data quality."""
    
    # Load data
    data_path = Path("data/raw/conversations.csv")
    if not data_path.exists():
        print("No conversation data found")
        return
    
    df = pd.read_csv(data_path)
    
    # Create Great Expectations context
    context = gx.get_context()
    
    # Create data source
    datasource = context.sources.add_pandas("conversation_data")
    data_asset = datasource.add_dataframe_asset(name="conversations", dataframe=df)
    
    # Create expectations
    suite = context.add_expectation_suite("conversation_quality")
    
    # Add expectations
    suite.add_expectation(
        gx.expectations.ExpectColumnToExist(column="message")
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnToExist(column="intent")
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column="message")
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValueLengthsToBeBetween(
            column="message", min_value=1, max_value=1000
        )
    )
    
    # Validate
    batch_request = data_asset.build_batch_request()
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite=suite
    )
    
    results = validator.validate()
    
    if results.success:
        print("✅ Data quality validation passed")
    else:
        print("❌ Data quality validation failed")
        for result in results.results:
            if not result.success:
                print(f"Failed: {result.expectation_config.expectation_type}")
    
    return results.success

if __name__ == "__main__":
    validate_conversation_data()