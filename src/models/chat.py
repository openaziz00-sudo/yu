from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Chat(db.Model):
    """نموذج المحادثة"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='محادثة جديدة')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # علاقة مع الرسائل
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': len(self.messages)
        }

class Message(db.Model):
    """نموذج الرسالة"""
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' أو 'assistant'
    content = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(50), nullable=True)  # النموذج المستخدم
    message_metadata = db.Column(db.Text, nullable=True)  # معلومات إضافية كـ JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        metadata_dict = {}
        if self.message_metadata:
            try:
                metadata_dict = json.loads(self.message_metadata)
            except:
                pass
                
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'role': self.role,
            'content': self.content,
            'model_used': self.model_used,
            'metadata': metadata_dict,
            'created_at': self.created_at.isoformat()
        }
    
    def set_metadata(self, metadata_dict):
        """تعيين البيانات الوصفية كـ JSON"""
        self.message_metadata = json.dumps(metadata_dict, ensure_ascii=False)
