from fastapi import FastAPI, Depends, HTTPException, status 
from h11._readers import Http10Reader
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session 
import models, schemas, utils 
from auth_database import get_db 
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encode_jwt

app =FastAPI()


@app.post("/signup")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    #check the user exist or not
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "User already exists")
    
    #hash the password
    hashed_pwd = utils.hash_password(user.password)

    #create new user 
    new_user = models.User(
        username = user.username, 
        email = user.email, 
        hashed_password = hashed_pwd, 
        role = user.role)
    
    #save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    #return the value(excluding the password)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email, "role": new_user.role}


@app.post("/login")
def login(foram_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == foram_data.username).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid Username")
    if not utils.verify_password(foram_data.password, user.hashed_password):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid password")
    
    token_data = {"sub": user.username, "role": user.role}
    token  = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str  = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "could not validate credential")
    headers = {"WWW-Authenticate": "Bearer"}

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    return {"username": username, "role": role}

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"Message": f"Hello, {current_user['username']} | you accesses a protected route"}

def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Not enough permission")
        
        return current_user
    
    return role_checker


