import pandas as pd
import json
from datetime import datetime
from validators.sql_validator import run_sql_validation
from validators.ai_validator import run_ai_validation

def generate_html_report(sql_results, ai_results, run_timestamp):
    """Generates a professional HTML data quality dashboard."""

    total_checks = len(sql_results) + len(ai_results)
    sql_passed = sum(1 for r in sql_results if r['passed'])
    ai_passed = sum(1 for r in ai_results
                    if r['pass_rate'] >= 80)
    overall_score = round(
        ((sql_passed + ai_passed) / total_checks) * 100, 1)

    # Build SQL rows
    sql_rows = ""
    for r in sql_results:
        status = "✓ PASS" if r['passed'] else "✗ FAIL"
        color = "#1a7a4a" if r['passed'] else "#c0392b"
        sql_rows += f"""
        <tr>
          <td>{r['field']}</td>
          <td>SQL Rule-based</td>
          <td>{r['owner']}</td>
          <td style='color:{color};font-weight:600'>{status}</td>
          <td>{r['detail']}</td>
          <td>{r['impact']}</td>
        </tr>"""

    # Build AI rows
    ai_rows = ""
    for r in ai_results:
        status = ("✓ PASS" if r['pass_rate'] >= 80
                  else "✗ FAIL")
        color = "#1a7a4a" if r['pass_rate'] >= 80 else "#c0392b"
        ai_rows += f"""
        <tr>
          <td>{r['field']}</td>
          <td>AI Semantic (Ollama)</td>
          <td>{r['owner']}</td>
          <td style='color:{color};font-weight:600'>{status}</td>
          <td>Pass rate: {r['pass_rate']}% |
              P1 failures: {r['p1_failures']}</td>
          <td>{r['impact']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>AI Data Quality Sentinel — Quality Report</title>
  <style>
    body {{font-family:Arial,sans-serif;margin:40px;color:#1a1a1a}}
    h1 {{color:#1F3864;border-bottom:3px solid #2E5FA3;padding-bottom:8px}}
    .score-box {{background:#1F3864;color:white;padding:20px 32px;
                 border-radius:8px;display:inline-block;margin:16px 0}}
    .score-number {{font-size:48px;font-weight:bold}}
    .score-label {{font-size:14px;opacity:.8}}
    table {{width:100%;border-collapse:collapse;margin-top:20px}}
    th {{background:#1F3864;color:white;padding:10px 12px;
         text-align:left;font-size:13px}}
    td {{padding:9px 12px;border-bottom:1px solid #e0e0e0;font-size:13px}}
    tr:nth-child(even) td {{background:#f4f6fb}}
    .section-title {{color:#2E5FA3;margin-top:32px;font-size:16px;
                     font-weight:600;border-left:4px solid #2E5FA3;
                     padding-left:10px}}
    .meta {{color:#666;font-size:12px;margin-top:4px}}
  </style>
</head>
<body>
  <h1>AI Hybrid Data Quality Sentinel</h1>
  <p class="meta">Run: {run_timestamp} |
     Framework: Great Expectations + Ollama LLM |
     Designed by Rasmi Murugavel</p>

  <div class="score-box">
    <div class="score-number">{overall_score}%</div>
    <div class="score-label">Overall data quality score</div>
  </div>

  <div class="section-title">
    SQL Rule-Based Validation (Structured Fields)
  </div>
  <table>
    <tr><th>CDE Field</th><th>Validation Type</th><th>Owner</th>
        <th>Result</th><th>Detail</th><th>Business Impact</th></tr>
    {sql_rows}
  </table>

  <div class="section-title">
    AI Semantic Validation (Unstructured Text Fields)
  </div>
  <table>
    <tr><th>CDE Field</th><th>Validation Type</th><th>Owner</th>
        <th>Result</th><th>Detail</th><th>Business Impact</th></tr>
    {ai_rows}
  </table>

  <p class="meta" style="margin-top:32px">
    AI findings are advisory. Final remediation decisions require
    data owner review and approval per governance policy.
  </p>
</body>
</html>"""

    filename = (f"reports/quality_report_"
                f"{datetime.now().strftime('%Y%m%d_%H%M')}.html")
    with open(filename, 'w') as f:
        f.write(html)
    print(f"Report generated: {filename}")
    return filename


if __name__ == "__main__":
    # Load data and registry
    df = pd.read_csv('data/sample_dataset.csv')
    with open('config/cde_registry.json') as f:
        registry = json.load(f)

    print("Running SQL validation...")
    sql_results = run_sql_validation(df, registry)

    print("Running AI semantic validation...")
    ai_results = run_ai_validation(df, registry)

    print("Generating report...")
    generate_html_report(
        sql_results, ai_results,
        datetime.now().strftime('%Y-%m-%d %H:%M'))
