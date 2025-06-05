from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))

class LoginRequestSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class LoginResponseSchema(Schema):
    message = fields.Str()
    access_token = fields.Str()
    refresh_token = fields.Str()

class RefreshTokenResponseSchema(Schema):
    access_token = fields.Str()

class LogoutResponseSchema(Schema):
    message = fields.Str()

class ProfileResponseSchema(Schema):
    username = fields.Str()
    message = fields.Str()

class CreateUserResponseSchema(Schema):
    message = fields.Str()
    username = fields.Str()

class ErrorSchema(Schema):
    error = fields.Str()
    code = fields.Int()

class HelloResponseSchema(Schema):
    message = fields.Str()
    status = fields.Str() 