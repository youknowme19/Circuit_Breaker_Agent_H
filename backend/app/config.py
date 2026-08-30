import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Circuit Breaker"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cb-dev-secret-key-change-in-prod-99812")

    # Policy Defaults
    MAX_SINGLE_TRANSFER: float = float(os.getenv("MAX_SINGLE_TRANSFER", "10000.0"))
    DAILY_VELOCITY_LIMIT: float = float(os.getenv("DAILY_VELOCITY_LIMIT", "20000.0"))
    NEW_COUNTERPARTY_THRESHOLD: float = float(os.getenv("NEW_COUNTERPARTY_THRESHOLD", "1000.0"))
    DUPLICATE_WINDOW_MINUTES: int = int(os.getenv("DUPLICATE_WINDOW_MINUTES", "15"))
    HIGH_RISK_THRESHOLD: float = float(os.getenv("HIGH_RISK_THRESHOLD", "0.85"))

    # Testnet & Payment Adapter
    ENABLE_TESTNET_EXECUTION: bool = os.getenv("ENABLE_TESTNET_EXECUTION", "false").lower() == "true"
    TESTNET_RPC_URL: str = os.getenv("TESTNET_RPC_URL", "")
    TESTNET_CHAIN_ID: int = int(os.getenv("TESTNET_CHAIN_ID", "11155111"))
    TESTNET_PRIVATE_KEY: str = os.getenv("TESTNET_PRIVATE_KEY", "")
    TESTNET_NETWORK_NAME: str = os.getenv("TESTNET_NETWORK_NAME", "Monad Testnet")
    TESTNET_EXPLORER_URL: str = os.getenv("TESTNET_EXPLORER_URL", "https://testnet.monadexplorer.com/tx/{tx_hash}")
    SENDER_ADDRESS: str = os.getenv("SENDER_ADDRESS", "")
    MOCK_PAYMENT_CONTRACT_ADDRESS: str = os.getenv("MOCK_PAYMENT_CONTRACT_ADDRESS", "0x1234567890123456789012345678901234567890")


    # Storage Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./circuit_breaker.db")

    # TrueForge Harness
    TRUEFORGE_API_KEY: str = os.getenv("TRUEFORGE_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
