from app.database import SessionLocal, Base, engine
from app.models.avatar import Avatar

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    avatars = [
        {
            "id": "1",
            "name": "Marcus Aurelius",
            "type": "Historic",
            "image_url": "/avatars/marcus_aurelius.jpg"
        },
        {
            "id": "2",
            "name": "Modern Male",
            "type": "Modern",
            "image_url": "/avatars/modern_male.png"
        },
        {
            "id": "3",
            "name": "Monk",
            "type": "Historic",
            "image_url": "/avatars/monk.jpg"
        },
        {
            "id": "4",
            "name": "William Shakespeare",
            "type": "Historic",
            "image_url": "/avatars/shakespeare.jpg"
        }
    ]
    
    for avatar_data in avatars:
        avatar = db.query(Avatar).filter(Avatar.id == avatar_data["id"]).first()
        if not avatar:
            avatar = Avatar(**avatar_data)
            db.add(avatar)
            print(f"Seeded avatar: {avatar_data['name']}")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
