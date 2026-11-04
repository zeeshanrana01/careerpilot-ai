"""Application configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CareerPilot AI"
    environment: str = "development"
    debug: bool = False
    
    # Storage settings
    database_url: str = "sqlite:///careerpilot.db"
    
    # Ingestion policies
    max_job_age_days: int = 30
    min_description_length: int = 50
    strict_security_mode: bool = True
    
    # LLM & Matcher Provider settings
    # Options: "mock", "ollama", "cloud"
    llm_provider: str = "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    cloud_api_key: str = ""
    cloud_model: str = "gemini-2.5-flash"
    cloud_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    
    # SMTP & Outbound Application Dispatch settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    sandbox_email_mode: bool = True
    auto_apply_enabled: bool = False
    auto_apply_threshold: float = 85.0
    
    # Tracking params to strip from URLs
    tracking_params: list[str] = [
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "ref", "reference", "source", "fbclid", "gclid", "msclkid", "tracking_id",
        "gh_src", "trk"
    ]

    model_config = SettingsConfigDict(
        env_prefix="CAREERPILOT_",
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
