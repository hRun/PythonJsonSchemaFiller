# PythonJsonSchemaFiller

A Python class to take in a json schema and return a json/OrderedDict object or a marshalled marshmallow-compatible schema populated with dummy values.
The json schema can be loaded from an openapi specification file or a json/dict object.
I'm using this to serialize Schemas from an openapi specification.

Can resolve $refs to an external openapi file. I implemented this lazily. You'll have to statically replace the file path with your own in \__init\__().

Might or might not be understood by and helpful to somebody...


## Issues

- No proper error handling
- No handling of oneOf, allOf, anyOf openapi primitives
- No resolving of $refs in populate()


## Examples

### Validate the dump of a marshaled and populated User object is equal to the source json object
import json
import SchemaFiller
from marshmallow import Schema

test_user = '{"user": {"first_name": "John", "last_name": "Doe", "username": "jdoe", "email": "john@doe.com"}, "roles": [{"name": "Admin", "permissions": [{"name": "admin"}]}]}'

schema_filler = SchemaFiller(openapi_spec='mypath/openapi.yaml')
user_schema = Schema.from_dict(schema_filler.populate('User', marshal=True))()

assert json.loads(test_user) == user_schema.loads(test_user)
assert test_user == user_schema.dumps(json.loads(test_user))


### Marshal a marshmallow Schema from an openapi schema definition and populate with data loaded from a MySQL database entry
import SchemaFiller
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload
from models import User, Role, Permission
from marshmallow import Schema

url = "mysql+pymysql://root:example@127.0.0.1:3306/db"
engine = create_engine(url)
session = scoped_session(sessionmaker(autoflush=False, bind=engine))
db = session()
user = db.scalars(select(User).options(joinedload(User.roles).joinedload(Role.permissions)).limit(1)).first()

schema_filler = SchemaFiller(openapi_spec='mypath/openapi.yaml')
user_schema = Schema.from_dict(schema_filler.populate('User', marshal=True))()

user_dict = {"user": user, "roles": user.roles}
user_schema.dumps(user_dict) #'{"user": {"first_name": "Son", "last_name": "Goku", "username": "goku", "email": "goku@kame-house.db"}, "roles": [{"name": "admin", "permissions": [{"name": "all"}]}]}'
user_schema.dumps(user) #'{"roles": [{"name": "admin", "permissions": [{"name": "all"}]}]}'