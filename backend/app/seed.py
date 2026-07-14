import asyncio
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models import Base, Representative, Hcp, Product, Interaction

async def seed_data():
    print(f"Connecting to database: {settings.database_url}")
    engine = create_async_engine(settings.database_url, future=True)
    
    async with engine.begin() as conn:
        print("Dropping existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session_maker() as session:
        # 1. Create Representative
        rep = Representative(
            id=uuid.UUID("e0a6d45e-4c07-4228-b9a5-1ffef76e330e"),
            name="Demo Rep",
            email="demo.rep@pharma.com",
            territory="South Region"
        )
        session.add(rep)

        # 2. Create HCPs
        hcp_rao = Hcp(
            id=uuid.UUID("a74f4b23-1d88-4c12-9c44-d8fcf5d27572"),
            name="Dr. Rao",
            specialty="Cardiology",
            hospital="Apollo Hospital",
            city="Bangalore",
            prescription_preferences={
                "brand_preference": "Lipitor",
                "patient_volume": "high",
                "notes": "Prefers evening visits."
            }
        )
        hcp_sharma = Hcp(
            id=uuid.UUID("b134d1b8-6a56-4c91-9e2e-2f587aa5d7c8"),
            name="Dr. Sharma",
            specialty="Diabetology",
            hospital="Fortis Hospital",
            city="Delhi",
            prescription_preferences={
                "brand_preference": "Ozempic",
                "patient_volume": "medium",
                "notes": "Interested in clinical trial updates."
            }
        )
        hcp_patil = Hcp(
            id=uuid.UUID("c561b369-2f56-41ee-a841-db1d528ef0c1"),
            name="Dr. Patil",
            specialty="Oncology",
            hospital="Tata Memorial Hospital",
            city="Mumbai",
            prescription_preferences={
                "brand_preference": "Keytruda",
                "patient_volume": "very high",
                "notes": "Active researcher."
            }
        )
        hcp_smith = Hcp(
            id=uuid.UUID("d114d1b8-6a56-4c91-9e2e-2f587aa5d7c9"),
            name="Dr. Smith",
            specialty="Cardiology",
            hospital="Metro Cardiology",
            city="Boston",
            prescription_preferences={
                "brand_preference": "Lipitor",
                "patient_volume": "high",
                "notes": "Prefers clinical trial data."
            }
        )
        hcp_john = Hcp(
            id=uuid.UUID("e114d1b8-6a56-4c91-9e2e-2f587aa5d7d0"),
            name="Dr. John",
            specialty="Cardiology",
            hospital="Mercy Hospital",
            city="Chicago",
            prescription_preferences={
                "brand_preference": "Lipitor",
                "patient_volume": "high",
                "notes": "Interested in new clinical evidence."
            }
        )
        session.add_all([hcp_rao, hcp_sharma, hcp_patil, hcp_smith, hcp_john])

        # 3. Create Products
        prod_ozempic = Product(
            id=uuid.UUID("d0e6d45e-4c07-4228-b9a5-1ffef76e330e"),
            name="Ozempic",
            category="Diabetes"
        )
        prod_keytruda = Product(
            id=uuid.UUID("f0a6d45e-4c07-4228-b9a5-1ffef76e330f"),
            name="Keytruda",
            category="Oncology"
        )
        prod_januvia = Product(
            id=uuid.UUID("a0a6d45e-4c07-4228-b9a5-1ffef76e3310"),
            name="Januvia",
            category="Diabetes"
        )
        prod_lipitor = Product(
            id=uuid.UUID("b0a6d45e-4c07-4228-b9a5-1ffef76e3311"),
            name="Lipitor",
            category="Cardiology"
        )
        session.add_all([prod_ozempic, prod_keytruda, prod_januvia, prod_lipitor])

        # 4. Create an Initial Interaction
        interaction = Interaction(
            id=uuid.UUID("fa03d1b8-6a56-4c91-9e2e-2f587aa5d7c8"),
            hcp_id=hcp_sharma.id,
            representative_id=rep.id,
            visit_date=date.today(),
            summary="Introduced Ozempic details. Discussed dosage guidelines.",
            raw_notes="Met Dr. Sharma to discuss Ozempic. Discussed dosage and provided a 5-unit sample pack. Scheduled a follow-up visit in two weeks.",
            extracted_entities={
                "hcp_name": "Dr. Sharma",
                "products": ["Ozempic"],
                "samples_given": [{"product_name": "Ozempic", "qty": 5}],
                "follow_up_date": "2026-07-27"
            },
            samples_given=[{"product_name": "Ozempic", "qty": 5}],
            action_items=[{"description": "Send Ozempic clinical trial brochure", "due_date": "2026-07-16"}],
            follow_up_date=date(2026, 7, 27),
            source="form",
            products=[prod_ozempic]
        )
        session.add(interaction)

        await session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
