import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ruta raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent

# Agregar directorio raíz al path para importar modulos
sys.path.insert(0, str(PROJECT_ROOT))
from supply.validate_allowlist import validar_allowlist

# Rutas de los archivos
SBOM_FILE = PROJECT_ROOT/"sbom.json"
ALLOWLIST_FILE = PROJECT_ROOT/"allowlist.json"
DASHBOARD_FILE = PROJECT_ROOT/"dashboard.html"

def generar_dashboard_html(sbom_path, allowlist_path, output_path):
    with open(sbom_path, "r", encoding="utf-8") as f:
        sbom = json.load(f)
    total_dependencias = len(sbom.get("components", []))
    es_valido, mensaje = validar_allowlist(sbom_path, allowlist_path)
    # Contar hallazgos
    hallazgos = 0
    if not es_valido:
        for linea in mensaje.split("\n"):
            if "Dependencia" in linea and ("NO está en el allowlist" in linea or "no coincide" in linea):
                hallazgos += 1
    # Estado de validacion
    estado = "PASSED" if es_valido else "FAILED"
    color_estado = "#28a745" if es_valido else "#dc3545"
    # Timestamp actual
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    # Generar HTML
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SBOM Security Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-bottom: 3px solid {color_estado};
        }}
        h1 {{
            font-size: 24px;
            font-weight: 600;
            margin: 0;
        }}
        .subtitle {{
            font-size: 13px;
            margin-top: 5px;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 12px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }}
        .status-box {{
            background-color: {color_estado};
            color: white;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-left: 4px solid rgba(0,0,0,0.2);
        }}
        .status-text {{
            font-size: 18px;
            font-weight: 600;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .metric-box {{
            border: 1px solid #e0e0e0;
            padding: 20px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 42px;
            font-weight: 300;
            color: #2c3e50;
            line-height: 1;
        }}
        .metric-label {{
            font-size: 13px;
            color: #666;
            margin-top: 8px;
        }}
        .footer {{
            background-color: #f8f8f8;
            padding: 15px 20px;
            border-top: 1px solid #ddd;
            font-size: 11px;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SBOM Security Dashboard</h1>
            <div class="subtitle">Security Report</div>
        </div>
        
        <div class="content">
            <div class="status-box">
                <div class="status-text">Hallazgos SBOM - Allowlist:  {hallazgos}  ({estado})</div>
            </div>

            <div class="section">
                <div class="section-title">Resumen de Dependencias</div>
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-value">{total_dependencias}</div>
                        <div class="metric-label">Total Dependencias</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">{hallazgos}</div>
                        <div class="metric-label">Hallazgos</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            Generado: {timestamp} | Proyecto: Cadena de Suministro
        </div>
    </div>
</body>
</html>
"""

    # Escribir HTML
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_file, es_valido, hallazgos, total_dependencias


if __name__ == "__main__":
    try:
        dashboard_path, valido, hallazgos, total = generar_dashboard_html(
            str(SBOM_FILE),
            str(ALLOWLIST_FILE),
            str(DASHBOARD_FILE)
        )
        print(f"Dashboard generado exitosamente: {dashboard_path}")
        print(f"  - Total dependencias: {total}")
        print(f"  - Hallazgos: {hallazgos}")
        print(f"  - Estado: {'PASSED' if valido else 'FAILED'}")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generando dashboard: {e}", file=sys.stderr)
        sys.exit(1)
