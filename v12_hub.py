from flask import Blueprint, current_app, render_template_string

hub_bp = Blueprint("v12_hub", __name__, url_prefix="/v12/hub")

@hub_bp.route("/", methods=["GET"])
def home():
    candidates = [
        ("Module Center", "/v12/modules"),
        ("Tool Runner", "/v12/tools/"),
        ("Integrations", "/v12/integrations/"),
        ("Control Panel", "/v12/control"),
        ("Reports", "/v12/reports"),
        ("Cases", "/v12/cases"),
        ("Evidence", "/v12/evidence"),
        ("Health", "/v12/health/"),
        ("Recovery", "/v12/recovery/"),
        ("Workspace", "/v12/manage/"),
    ]

    existing = {rule.rule for rule in current_app.url_map.iter_rules()}
    links = [(name, path) for name, path in candidates if path in existing]

    page = """
    <!doctype html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>TORDISSX86 HUB</title>
      <style>
        body{background:#07110d;color:#d8ffe8;font-family:Arial;padding:18px}
        h1{color:#00ff88}
        .card{background:#10251b;border:1px solid #176b43;
        border-radius:12px;padding:16px;margin:12px 0}
        a{color:#00ff99;text-decoration:none;font-weight:bold}
        .status{color:#a8d9bd;font-size:13px}
      </style>
    </head>
    <body>
      <h1>TORDISSX86 HUB</h1>
      <p>Central Navigation Dashboard</p>
      {% for name,path in links %}
      <div class="card">
        <a href="{{ path }}">{{ name }} →</a>
        <div class="status">{{ path }}</div>
      </div>
      {% endfor %}
      {% if not links %}
      <p>Hakuna route iliyopatikana bado.</p>
      {% endif %}
      <p class="status">TORDISSX86 | Local Dashboard</p>
    </body>
    </html>
    """
    return render_template_string(page, links=links)
