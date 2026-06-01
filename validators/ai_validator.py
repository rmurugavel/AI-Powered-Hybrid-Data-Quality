import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"  # or qwen — whatever you have running locally

def validate_text_field_with_ai(value, cde_rule, field_name):
    """
    Uses local Ollama LLM to semantically validate a text field
    against a natural language quality rule.
    Returns: pass/fail + explanation
    """

    # Handle empty/null values before sending to LLM
    if not value or str(value).strip() == "":
        return {
            "passed": False,
            "confidence": "high",
            "explanation": "Field is empty. No content to validate.",
            "severity": "P1"
        }

    prompt = f"""You are a data quality validator for enterprise financial systems.

Field being validated: {field_name}
Field value: "{value}"
Quality rule: {cde_rule}

Evaluate whether this field value PASSES or FAILS the quality rule.
Respond ONLY with valid JSON in this exact format:
{{
  "passed": true or false,
  "confidence": "high" or "medium" or "low",
  "explanation": "one sentence explaining why it passes or fails",
  "severity": "P1" if critical failure, "P2" if significant, "P3" if minor
}}

Do not include any text outside the JSON."""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })

    try:
        raw = response.json()['response']
        result = json.loads(raw)
        return result
    except Exception as e:
        return {
            "passed": False,
            "confidence": "low",
            "explanation": f"Validation error: {str(e)}",
            "severity": "P2"
        }


def run_ai_validation(df, cde_registry):
    """
    Runs AI semantic validation on all text-type CDE fields.
    Samples records to manage API/LLM cost — validates up to 50 rows.
    """
    ai_cdes = [c for c in cde_registry['cdes']
               if c['validation_type'] == 'ai']

    all_results = []
    sample = df.sample(min(50, len(df)), random_state=42)

    for cde in ai_cdes:
        field = cde['field']
        rule = cde['rule']
        field_results = []

        print(f"Running AI validation on field: {field}")

        for _, row in sample.iterrows():
            value = str(row.get(field, ""))
            result = validate_text_field_with_ai(value, rule, field)
            result['consultant_id'] = row.get('consultant_id', 'unknown')
            result['field'] = field
            result['value_preview'] = value[:80]
            field_results.append(result)

        pass_rate = sum(1 for r in field_results if r['passed']) / len(field_results)
        p1_count = sum(1 for r in field_results if r.get('severity') == 'P1')

        all_results.append({
            "field": field,
            "owner": cde['owner'],
            "validation_type": "AI — Semantic",
            "impact": cde['failure_impact'],
            "pass_rate": round(pass_rate * 100, 1),
            "p1_failures": p1_count,
            "record_results": field_results
        })

    return all_results
