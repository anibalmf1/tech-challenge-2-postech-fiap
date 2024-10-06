import uuid
from app.database import Session
from app.models import Resource


class ResourceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, resource: Resource) -> None:
        resource.id = str(uuid.uuid4())
        self.session.add(resource)
        self.session.commit()

    def update(self, resource_id: str, resource: Resource) -> None:
        existing_resource = self.session.query(Resource).filter(Resource.id == resource_id).first()
        if existing_resource:
            for key, value in vars(resource).items():
                if key != 'id' and not key.startswith('_'):
                    setattr(existing_resource, key, value)
            self.session.commit()

    def retrieve_all(self):
        return self.session.query(Resource).all()

    def retrieve_by_id(self, resource_id: str):
        return self.session.query(Resource).filter(Resource.id == resource_id).first()


def get_repository():
    db: Session = Session()
    try:
        repo = ResourceRepository(db)
        yield repo
    finally:
        db.close()
