from pydantic import BaseModel, validator, ValidationError, Extra


class CreateChat(BaseModel, extra=Extra.forbid):
    chat_name: str

    @validator('chat_name')
    def name_check(cls, v: str) -> str:
        if not 0 < len(v) <= 255:
            raise ValidationError('From 1 to 150 symbols')
        return v


class AddUser(BaseModel, extra=Extra.forbid):
    user_name: str

    @validator('user_name')
    def name_check(cls, v: str) -> str:
        if not 0 < len(v) <= 255:
            raise ValidationError('From 1 to 150 symbols')
        return v


class SendMessage(BaseModel, extra=Extra.forbid):
    message: str


class SearchMessage(BaseModel, extra=Extra.forbid):
    message: str

    @validator('message')
    def name_check(cls, v: str) -> str:
        if len(v) <= 3:
            raise ValidationError('Should be more than 3 symbols!')
        return v