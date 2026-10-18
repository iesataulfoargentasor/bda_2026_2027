"""Genera paquetes personales equivalentes; solo biblioteca estándar de Python."""
import argparse
import csv
import hashlib
import io
import json
import random
import zipfile
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {"reservas_pdi.csv": ",", "cobros_pdi.csv": ";", "hoteles_pdi.csv": ";"}


def read_csv(data, sep):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig")), delimiter=sep))


def encode_csv(rows, sep):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=list(rows[0]), delimiter=sep, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def results(data):
    reservas = read_csv(data["reservas_pdi.csv"], ",")
    cobros = read_csv(data["cobros_pdi.csv"], ";")
    hoteles = read_csv(data["hoteles_pdi.csv"], ";")
    assert [len(reservas), len(cobros), len(hoteles)] == [20, 15, 5]
    for rows, key in [(reservas, "id_reserva"), (cobros, "id_reserva"), (hoteles, "id_hotel")]:
        assert len({row[key] for row in rows}) == len(rows), "Clave duplicada"
    rr = {r["id_reserva"]: r for r in reservas}
    hh = {r["id_hotel"]: r for r in hoteles}
    assert all(r["id_hotel"] in hh for r in reservas)
    grouped = defaultdict(lambda: [0, Decimal(0)])
    for c in cobros:
        r = rr[c["id_reserva"]]
        amount = Decimal(c["cobrado"])
        assert amount > 0 and amount == Decimal(r["importe"])
        key = (hh[r["id_hotel"]]["hotel"], r["canal"])
        grouped[key][0] += 1
        grouped[key][1] += amount
    paid = {c["id_reserva"] for c in cobros}
    unpaid = sorted((int(r["id_reserva"]), hh[r["id_hotel"]]["hotel"], r["canal"],
                     Decimal(r["importe"]), "Sin cobro asociado en el archivo recibido")
                    for r in reservas if r["id_reserva"] not in paid)
    assert len(grouped) == 13
    assert sum(x[0] for x in grouped.values()) == 15
    assert sum(x[1] for x in grouped.values()) == Decimal("3965.50")
    assert grouped[("Laredo", "web")] == [2, Decimal("496.50")]
    assert [r[0] for r in unpaid] == [4, 9, 11, 15, 18]
    return dict(grouped), unpaid


def make_variant(original, number):
    rows = {name: read_csv(data, FILES[name]) for name, data in original.items()}
    # Redistribución dentro de Laredo/web y Comillas/web: misma suma por grupo.
    delta = {"1": number, "16": -number, "8": number * 7, "19": -number * 7}
    for name, field in [("reservas_pdi.csv", "importe"), ("cobros_pdi.csv", "cobrado")]:
        for row in rows[name]:
            change = Decimal(delta.get(row["id_reserva"], 0)) / 100
            row[field] = format(Decimal(row[field]) + change, ".2f")
    for i, name in enumerate(FILES):
        random.Random(number * 101 + i).shuffle(rows[name])
    return {name: encode_csv(rows[name], sep) for name, sep in FILES.items()}


def add_zip(z, name, data):
    # Fecha fija para reproducir exactamente el paquete de cada código.
    info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cantidad", type=int, default=15)
    parser.add_argument("--destino", type=Path, default=ROOT / "materiales-docentes/pentaho/paquetes-pentaho.zip")
    args = parser.parse_args()
    if not 1 <= args.cantidad <= 1000:
        parser.error("La cantidad debe estar entre 1 y 1000")
    original = {name: (ROOT / "docs/assets/practicas" / name).read_bytes() for name in FILES}
    reference = results(original)
    packages = []
    manifest = []
    signatures = set()
    for number in range(1, args.cantidad + 1):
        code = f"A{number:03d}"
        data = make_variant(original, number)
        assert results(data) == reference, f"Resultados distintos en {code}"
        signature = tuple(sorted((r["id_reserva"], r["cobrado"]) for r in read_csv(data["cobros_pdi.csv"], ";")))
        assert signature not in signatures, "Variantes de detalle repetidas"
        signatures.add(signature)
        digest = {name: hashlib.sha256(content).hexdigest() for name, content in data.items()}
        note = {"codigo": code, "conjunto": "cierre_aula_01", "version": 1, "sha256": digest}
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, "w") as z:
            for name, content in data.items():
                add_zip(z, "entrada/" + name, content)
            add_zip(z, "asignacion.json", json.dumps(note, ensure_ascii=False, indent=2).encode("utf-8"))
            add_zip(z, "LEEME.txt", (f"Paquete {code} — cierre_aula_01\n"
                    "Copia entrada/ a tu repositorio y conserva asignacion.json en la raíz.\n"
                    "No modifiques estos originales. Usa copias para las pruebas de fallo.\n"
                    "Aplica las instrucciones y los resultados de referencia de la práctica.\n"
                    "Registra el código asignado en tu README.\n").encode("utf-8"))
        packages.append((f"{code}.zip", memory.getvalue()))
        manifest.extend({"codigo": code, "archivo": name, "sha256": value} for name, value in digest.items())
    args.destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.destino, "w") as z:
        for name, content in packages:
            add_zip(z, name, content)
        add_zip(z, "control-docente.csv", encode_csv(manifest, ";"))
        add_zip(z, "LEEME-DOCENTE.txt", (
            "Asigna un código diferente a cada alumno y entrega solo su ZIP mediante Moodle o en el aula.\n"
            "Conserva la relación código/alumno en Moodle, no en el repositorio público.\n"
            "control-docente.csv contiene huellas SHA-256 de los originales, no datos personales.\n"
            "Los dos informes completos deben coincidir con la referencia; esto no acredita copia.\n"
            "El paquete identifica los datos usados, no certifica autoría ni horario.\n"
        ).encode("utf-8"))
    print(f"{args.cantidad} paquetes únicos comprobados: {args.destino}")
    print("Ambos resultados completos coinciden con la referencia; 13 grupos, 15 cobros, 3965.50 y 5 sin cobro.")


if __name__ == "__main__":
    main()
