"""
数据库模型定义
使用 SQLAlchemy ORM
"""

from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class Keyword(Base):
    """关键词记录"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), unique=True, index=True, nullable=False)
    source = Column(String(50), nullable=False)  # youtube, article, seo
    total_found = Column(Integer, default=0)
    eligible_count = Column(Integer, default=0)
    email_found_count = Column(Integer, default=0)
    email_rate = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    last_analyzed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Keyword {self.keyword} (source={self.source})>"


class Email(Base):
    """邮箱记录"""
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_valid = Column(Boolean, default=True)
    is_blacklisted = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)
    domain = Column(String(255), index=True)
    source_keyword = Column(String(255), ForeignKey("keywords.keyword"))
    last_validated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Email {self.email}>"


class SEOOpportunity(Base):
    """SEO 机会记录"""
    __tablename__ = "seo_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, index=True, nullable=False)
    title = Column(String(500))
    keyword = Column(String(255), ForeignKey("keywords.keyword"), index=True)
    relevance_score = Column(Float, default=0.0)
    level = Column(String(10), default="C")  # A, B, C
    opportunity_type = Column(String(100))
    action = Column(Text)
    domain = Column(String(255), index=True)
    contacted = Column(Boolean, default=False)
    contacted_at = Column(DateTime)
    response_status = Column(String(50))  # no_response, positive, negative
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SEOOpportunity {self.url}>"


class Report(Base):
    """报告记录"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, index=True, nullable=False)
    report_type = Column(String(50), nullable=False)  # keyword_review, seo_analysis, email_validation
    title = Column(String(255))
    status = Column(String(50), default="processing")  # processing, completed, failed
    generated_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(500))
    file_url = Column(String(500))
    data = Column(Text)  # JSON 格式的报告数据
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report {self.report_id}>"


class EmailCampaign(Base):
    """邮件活动记录"""
    __tablename__ = "email_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(100), unique=True, index=True, nullable=False)
    campaign_name = Column(String(255))
    keyword = Column(String(255), ForeignKey("keywords.keyword"))
    total_emails = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    replied_count = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<EmailCampaign {self.campaign_name}>"


class ApiLog(Base):
    """API 调用日志"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), index=True)
    method = Column(String(10))  # GET, POST, etc.
    status_code = Column(Integer)
    response_time = Column(Float)  # 毫秒
    user_ip = Column(String(50))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ApiLog {self.endpoint}>"


class User(Base):
    """用户（未来功能）"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"


class ApiKey(Base):
    """API 密钥（用于外部集成）"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ApiKey {self.name}>"
