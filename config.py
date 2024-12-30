AVAILABLE_MODELS = [
    {
        "id": "qwen2.5:7b",
        "name": "Model: Qwen 2.5 7B",
        "default": True
    },
    {
        "id": "qwen2.5:3b",
        "name": "Model:Qwen 2.5 3B",
        "default": False
    }
]

DEFAULT_MODEL = next((model["id"] for model in AVAILABLE_MODELS if model["default"]), AVAILABLE_MODELS[0]["id"]) 