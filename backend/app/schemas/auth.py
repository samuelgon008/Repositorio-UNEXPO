"""Contratos de entrada/salida de la API de autenticación."""
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import BCRYPT_MAX_BYTES


class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalizar(cls, v: str) -> str:
        return v.strip().lower()


class RegistroIn(BaseModel):
    cedula: str = Field(pattern=r"^[VEve]?-?\d{6,9}$", examples=["V-27123456"])
    nombres: str = Field(min_length=2, max_length=80)
    apellidos: str = Field(min_length=2, max_length=80)
    email: EmailStr
    username: str = Field(pattern=r"^[a-zA-Z0-9_.]{3,40}$")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("cedula")
    @classmethod
    def normalizar_cedula(cls, v: str) -> str:
        digitos = re.sub(r"\D", "", v)
        prefijo = v[0].upper() if v[0].isalpha() else "V"
        return f"{prefijo}-{digitos}"

    @field_validator("username", "email")
    @classmethod
    def minusculas(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_robusta(cls, v: str) -> str:
        if len(v.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError("La contraseña es demasiado larga")
        if not (re.search(r"[A-Za-z]", v) and re.search(r"\d", v)):
            raise ValueError("La contraseña debe combinar letras y números")
        return v


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nombres: str
    apellidos: str
    email: str
    rol: str
    estado: str
    permisos: list[str]


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


class MensajeOut(BaseModel):
    detail: str
