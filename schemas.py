from pydantic import BaseModel, EmailStr

#schema for newuser creation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 
    role: str 

#scema for login
class UserLogin(BaseModel):
    username: str 
    passwrod: str 
