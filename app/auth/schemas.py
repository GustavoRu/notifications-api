from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(min_length=1 ,max_length=50)
    email: EmailStr = Field(min_length=1 ,max_length=120)

class UserCreate(UserBase):
    #email: str = Field(min_length=1 ,max_length=120)
    password: str = Field(min_length=8, max_length=120) 
    #username: str = Field(min_length=1 ,max_length=50)

class UserRead(BaseModel): 
    #"user public"
    model_config = ConfigDict(from_attributes=True)
    id: int 
    username: str
    email: EmailStr
    created_at: datetime

class Token(BaseModel):
    access_token: str    
    token_type: str = Field(default="bearer")   