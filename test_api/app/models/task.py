from app import db
 
 
class Task(db.Model):
    __tablename__ = "tasks"
 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
 
    # Chave estrangeira ligando a tarefa ao usuário dono
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
 
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "done": self.done,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
 
    def __repr__(self):
        return f"<Task {self.title!r} done={self.done}>"