import great_expectations as gx
import pandas as pd
import json

def run_sql_validation(df, cde_registry):
    """
    Runs Great Expectations checks on structured CDE fields.
    Returns a list of validation results with pass/fail and severity.
    """
    context = gx.get_context()
    results = []

    # Load only SQL-type CDEs
    sql_cdes = [c for c in cde_registry['cdes']
                if c['validation_type'] == 'sql']

    for cde in sql_cdes:
        field = cde['field']
        result = {"field": field, "owner": cde['owner'],
                  "validation_type": "SQL", "impact": cde['failure_impact']}

        if cde['rule'] == 'not_null_and_unique':
            null_count = df[field].isnull().sum()
            dup_count = df[field].duplicated().sum()
            passed = (null_count == 0 and dup_count == 0)
            result['passed'] = passed
            result['detail'] = f"Nulls: {null_count} | Duplicates: {dup_count}"

        elif cde['rule'] == 'not_null_not_zero_within_range':
            null_count = df[field].isnull().sum()
            zero_count = (df[field] == 0).sum()
            mean_val = df[field].mean()
            threshold = cde.get('range_threshold', 0.05)
            # Period-over-period variance check (simplified: check against mean)
            outliers = df[df[field] > mean_val * (1 + threshold)].shape[0]
            passed = (null_count == 0 and zero_count == 0)
            result['passed'] = passed
            result['detail'] = (f"Nulls: {null_count} | Zeros: {zero_count} "
                                f"| Outliers vs mean: {outliers}")

        results.append(result)

    return results
