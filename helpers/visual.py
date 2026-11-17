import ast
import re

def extract_sql_result(response):
    """Safely extract the SQL result rows from SQLDatabaseChain's intermediate_steps."""
    steps = response.get("intermediate_steps", [])
    if len(steps) < 3:
        return None

    raw = steps[2]

    # Already a list of tuples
    if isinstance(raw, list):
        return raw

    # String repr — strip Decimal(...) wrappers, then literal_eval (safe, unlike eval)
    if isinstance(raw, str):
        try:
            cleaned = re.sub(r"Decimal\('([^']+)'\)", r"\1", raw)
            return ast.literal_eval(cleaned)
        except (ValueError, SyntaxError):
            return None
    return None

def extract_sql_query(response):
    """Pull the generated SQL string for display + column-name inference."""
    steps = response.get("intermediate_steps", [])
    if len(steps) >= 2 and isinstance(steps[1], str):
        return steps[1]
    return None

def infer_column_names(sql_query, n_cols):
    """
    Quick-and-dirty: parse the SELECT clause to get column aliases/names.
    Falls back to generic names if parsing fails or counts mismatch.
    """
    if not sql_query:
        return [f"col_{i}" for i in range(n_cols)]
    try:
        # Grab text between SELECT and FROM (first occurrence, case-insensitive)
        match = re.search(r"SELECT\s+(.*?)\s+FROM", sql_query, re.IGNORECASE | re.DOTALL)
        if not match:
            return [f"col_{i}" for i in range(n_cols)]
        select_clause = match.group(1)

        # Split on commas that aren't inside parentheses (handles SUM(a), b, c)
        parts, depth, buf = [], 0, ""
        for ch in select_clause:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append(buf.strip())
                buf = ""
            else:
                buf += ch
            if buf.strip():
                parts.append(buf.strip())

        names = []
        for p in parts:
            # Handle "expr AS alias" or just bare column
            alias_match = re.search(r"\s+AS\s+`?(\w+)`?\s*$", p, re.IGNORECASE)
            if alias_match:
                names.append(alias_match.group(1))
            else:
                # Strip backticks and take the last identifier-ish token
                clean = p.replace("`", "").strip()
                names.append(clean)

            if len(names) == n_cols:
                return names
    except Exception:
        pass
    return [f"col_{i}" for i in range(n_cols)]
