"""Render the curated Skill and Reference examples as static HTML."""

import html
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
START = "<!-- knowledge-examples:start -->"
END = "<!-- knowledge-examples:end -->"


def escape(value):
    return html.escape(value, quote=True)


def render_panel(example):
    key = example["id"]
    skill = example["skill"]
    reference = example["reference"]
    steps = "".join(
        f'<li><strong>{escape(title)}</strong><p>{escape(body)}</p></li>'
        for title, body in skill["steps"]
    )
    code = ""
    if skill.get("code"):
        code = (
            '<div class="knowledge-code">'
            f'<span>{escape(skill["codeLabel"])}</span>'
            f'<pre><code>{escape(skill["code"])}</code></pre></div>'
        )
    columns = reference.get("columns", [reference.get("entryLabel", "Entry"), "Meaning / constraint"])
    code_columns = set(reference.get("codeColumns", []))
    headings = "".join(f'<th scope="col">{escape(column)}</th>' for column in columns)
    def render_rows(rows):
        rendered_rows = []
        for row in rows:
            if len(row) != len(columns):
                raise ValueError(f"Column count mismatch in {key}")
            first = escape(row[0])
            if reference.get("codeFirstColumn", True):
                first = f"<code>{first}</code>"
            cells = [f'<th scope="row">{first}</th>']
            for index, value in enumerate(row[1:], start=1):
                value = escape(value)
                if index in code_columns:
                    value = f"<code>{value}</code>"
                cells.append(f"<td>{value}</td>")
            rendered_rows.append("<tr>" + "".join(cells) + "</tr>")
        return "".join(rendered_rows)

    if reference.get("groups"):
        bodies = "".join(
            '<tbody><tr class="knowledge-row-group">'
            f'<th colspan="{len(columns)}" scope="rowgroup">{escape(group["title"])}</th></tr>'
            f'{render_rows(group["rows"])}</tbody>'
            for group in reference["groups"]
        )
    else:
        bodies = f'<tbody>{render_rows(reference["rows"])}</tbody>'
    wide_table = len(columns) > 2
    table_kind = reference.get("tableKind", "commands" if wide_table else "standard")
    table_variant = {
        "standard": "",
        "commands": " knowledge-command-table",
        "parameters": " knowledge-parameter-table",
        "settings": " knowledge-settings-table",
        "shortcuts": " knowledge-shortcut-table",
        "hierarchy": " knowledge-hierarchy-table",
    }[table_kind]
    table_class = "knowledge-reference-table" + table_variant
    scroll_class = "knowledge-reference-scroll" + (" knowledge-parameter-scroll" if table_kind == "parameters" else "")
    table_start = (
        f'<div class="{scroll_class}" role="region" tabindex="0" '
        f'aria-label="{escape(example["name"])}: {escape(reference["title"])}">'
        if wide_table else ""
    )
    table_end = "</div>" if wide_table else ""
    table_hint = (
        f'<p class="knowledge-table-hint">{escape(reference["tableHint"])}</p>'
        if reference.get("tableHint") else ""
    )
    notes = "".join(
        '<div class="knowledge-reference-note">'
        f'<h5>{escape(note["title"])}</h5>'
        f'<code>{escape(note["code"])}</code>'
        f'<p>{escape(note["text"])}</p></div>'
        for note in reference.get("notes", [])
    )
    return f"""
            <div id="knowledge-panel-{key}" class="knowledge-panel" role="tabpanel" aria-labelledby="knowledge-tab-{key}" tabindex="0">
              <div class="knowledge-panel-heading">
                <h3>{escape(example['name'])}</h3>
                <p>{escape(example['domain'])}</p>
              </div>
              <div class="knowledge-pair">
                <article class="knowledge-card knowledge-card-skill" aria-labelledby="knowledge-skill-{key}">
                  <header class="knowledge-card-header">
                    <strong>Skill</strong><span>Reusable procedure</span>
                  </header>
                  <div class="knowledge-card-body">
                    <h4 id="knowledge-skill-{key}">{escape(skill['title'])}</h4>
                    <p class="knowledge-description">{escape(skill['description'])}</p>
                    <ol class="knowledge-steps">{steps}</ol>
                    {code}
                  </div>
                </article>
                <article class="knowledge-card knowledge-card-reference" aria-labelledby="knowledge-reference-{key}">
                  <header class="knowledge-card-header">
                    <strong>Reference</strong><span>On-demand lookup</span>
                  </header>
                  <div class="knowledge-card-body">
                    <h4 id="knowledge-reference-{key}">{escape(reference['title'])}</h4>
                    <p class="knowledge-description">{escape(reference['description'])}</p>
                    {table_hint}
                    {table_start}<table class="{table_class}">
                      <caption class="sr-only">{escape(example['name'])}: {escape(reference['title'])}</caption>
                      <thead><tr>{headings}</tr></thead>
                      {bodies}
                    </table>{table_end}
                    {notes}
                  </div>
                </article>
              </div>
            </div>"""


def main():
    examples = json.loads((PROJECT / "assets/data/knowledge-examples.json").read_text(encoding="utf-8"))
    tabs = "\n".join(
        f'              <button id="knowledge-tab-{item["id"]}" type="button" role="tab" '
        f'aria-selected="{str(index == 0).lower()}" aria-controls="knowledge-panel-{item["id"]}" '
        f'tabindex="{0 if index == 0 else -1}">{escape(item["name"])}</button>'
        for index, item in enumerate(examples)
    )
    panels = "".join(render_panel(item) for item in examples)
    rendered = f"""{START}
          <div class="knowledge-explorer">
            <div class="knowledge-tabs" role="tablist" aria-label="Choose an application to explore its Skill and Reference" hidden>
{tabs}
            </div>
{panels}
          </div>
          {END}"""
    rendered = "\n".join(line.rstrip() for line in rendered.splitlines())
    path = PROJECT / "index.html"
    document = path.read_text(encoding="utf-8")
    start = document.index(START)
    end = document.index(END, start) + len(END)
    path.write_text(document[:start] + rendered + document[end:], encoding="utf-8")
    print(f"Rendered {len(examples)} application pairs.")


if __name__ == "__main__":
    main()
