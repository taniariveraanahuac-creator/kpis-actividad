"""Regenera data/kpis.js y dashboard/kpis_casos.xlsx a partir de las macros.
Lo ejecuta GitHub Actions cada vez que cambia algo en macros/.
Uso manual:  python scripts/build_data.py
"""
import json, pathlib, openpyxl
from openpyxl.styles import Font, PatternFill

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = [
 {
  "g": "L",
  "t": 1,
  "n": "Abarrotes «La Esquina»",
  "file": "Macro_KPIs_Liderazgo_Equipo1.xlsx"
 },
 {
  "g": "L",
  "t": 2,
  "n": "Boutique «Moda Centro»",
  "file": "Macro_KPIs_Liderazgo_Equipo2.xlsx"
 },
 {
  "g": "L",
  "t": 3,
  "n": "Panadería «El Trigal»",
  "file": "Macro_KPIs_Liderazgo_Equipo3.xlsx"
 },
 {
  "g": "L",
  "t": 4,
  "n": "Outsourcing «Contacto Directo»",
  "file": "Macro_KPIs_Liderazgo_Equipo4.xlsx"
 },
 {
  "g": "L",
  "t": 5,
  "n": "Oficina «Facturación y pagos»",
  "file": "Macro_KPIs_Liderazgo_Equipo5.xlsx"
 },
 {
  "g": "A",
  "t": 1,
  "n": "Universidad «Facultad de Negocios»",
  "file": "Macro_KPIs_Administracion_Equipo1.xlsx"
 },
 {
  "g": "A",
  "t": 2,
  "n": "Fábrica «Envases del Sureste»",
  "file": "Macro_KPIs_Administracion_Equipo2.xlsx"
 },
 {
  "g": "A",
  "t": 3,
  "n": "Despacho jurídico «Bufete Peninsular»",
  "file": "Macro_KPIs_Administracion_Equipo3.xlsx"
 },
 {
  "g": "A",
  "t": 4,
  "n": "Construcción «Casa Maya»",
  "file": "Macro_KPIs_Administracion_Equipo4.xlsx"
 },
 {
  "g": "A",
  "t": 5,
  "n": "Hotel «Caribe» (Cancún)",
  "file": "Macro_KPIs_Administracion_Equipo5.xlsx"
 }
]
G = {"L": "Liderazgo", "A": "Administración"}
TIPO = {"A": "↑ Más es mejor", "B": "↑ Más es mejor", "C": "↓ Menos es mejor"}


def cumplimiento(t, v, m):
    """% de cumplimiento: ↑ real ÷ meta × 100 · ↓ meta ÷ real × 100."""
    return m / v * 100 if t == "C" else v / m * 100


def semaforo(t, v, m):
    c = round(cumplimiento(t, v, m), 6)
    return "VERDE" if c >= 100 else ("AMARILLO" if c >= 90 else "ROJO")


rows, comp, meta = [], [], {}
for c in CASES:
    wb = openpyxl.load_workbook(ROOT / "macros" / c["file"])
    d, tb = wb["Datos"], wb["Tablero"]
    for k in range(3):
        name, tipo, m = tb.cell(14 + k, 1).value, tb.cell(14 + k, 2).value, tb.cell(14 + k, 3).value
        pct = "*100" in str(tb.cell(5, 2 + k).value)
        t = "C" if "↓" in str(tipo) else ("A" if pct else "B")
        unit = "%" if pct else ("$" if "$" in str(d.cell(4, 2 + 2 * k).value) else "")
        meta[f"{c['g']}{c['t']}-{k + 1}"] = [name, t, m, unit]
        for mes in range(6):
            a, b = d.cell(5 + mes, 2 + 2 * k).value, d.cell(5 + mes, 3 + 2 * k).value
            if not b:
                continue
            v = a / b * (100 if pct else 1)
            comp.append([c["g"], c["t"], k + 1, mes + 1, round(v, 4)])
            rows.append([G[c["g"]], c["t"], c["n"], k + 1, name, TIPO[t], mes + 1, round(v, 4), m, unit,
                         semaforo(t, v, m), round(cumplimiento(t, v, m), 2)])

(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "kpis.js").write_text(
    "var KPIDATA=" + json.dumps(comp, separators=(",", ":")) + ";\nvar KPIMETA="
    + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "KPIs"
ws.append(["Grupo", "Equipo", "Caso", "KPI_num", "KPI", "Tipo", "Mes", "Valor", "Meta", "Unidad", "Semaforo", "Cumplimiento"])
for r in rows:
    ws.append(r)
for cell in ws[1]:
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="0F1923")
ws.freeze_panes = "A2"
wb.save(ROOT / "dashboard" / "kpis_casos.xlsx")
print(f"Listo: {len(rows)} filas de {len(CASES)} casos.")
