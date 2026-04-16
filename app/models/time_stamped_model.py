from datetime import datetime, timezone
from beanie import Document, before_event, Insert, Replace, Update, Save


class TimeStampedDocument(Document):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @before_event([Insert])
    def set_created_at(self):
        """Définit la date de création avant insertion."""
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at

    @before_event([Replace, Save, Update])
    def set_updated_at(self):
        """Met à jour la date de modification avant update."""
        self.updated_at = datetime.now(timezone.utc)
