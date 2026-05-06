from pydantic import BaseModel


def serialize_model(model: BaseModel) -> dict:
    return model.model_dump(mode="json", by_alias=False)


def serialize_models(models: list[BaseModel]) -> list[dict]:
    return [serialize_model(model) for model in models]
