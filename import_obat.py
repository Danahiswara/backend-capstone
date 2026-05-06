from openpyxl import load_workbook
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.type import Type


def import_excel():
    db: Session = SessionLocal()

    wb = load_workbook("Formulariumrev.xlsx")
    ws = wb["Usulan Formularium 2026"]

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # skip header

        composition = row[0]     # KOMPOSISI
        name = row[2]            # MEREK
        pharmacy = row[4]        # FARMASI
        distribution = row[5]    # DISTRIBUTOR

        if not composition or not name:
            continue

        # cek apakah sudah ada
        existing = db.query(Type).filter(
            Type.name == name
        ).first()

        if existing:
            continue

        new_type = Type(
            name=name.strip(),
            description=name.strip(),
            category="obat",
            total_items=0,
            composition=composition.strip() if composition else None,
            pharmacy=pharmacy.strip() if pharmacy else None,
            distribution=distribution.strip() if distribution else None
        )

        db.add(new_type)

    db.commit()
    db.close()

    print("✅ Import selesai")


if __name__ == "__main__":
    import_excel()