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
    rows = "".join(
        f'<tr><th scope="row"><code>{escape(term)}</code></th>'
        f'<td>{escape(meaning)}</td></tr>'
        for term, meaning in reference["rows"]
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
                    <table class="knowledge-reference-table">
                      <caption class="sr-only">{escape(example['name'])}: {escape(reference['title'])}</caption>
                      <thead><tr><th scope="col">Entry</th><th scope="col">Meaning / constraint</th></tr></thead>
                      <tbody>{rows}</tbody>
                    </table>
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
