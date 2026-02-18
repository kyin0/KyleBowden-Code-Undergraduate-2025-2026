from pathlib import Path
import yaml

def load_config():
    base_dir = Path(__file__).resolve().parents[2]
    config_path = base_dir / "config" / "config.yml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found at {config_path}")
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)