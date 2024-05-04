import json, jsonref
import random
import re
import rstr
import string
import yaml

from collections import OrderedDict
from datetime    import datetime, UTC
from marshmallow import Schema, fields
from os          import path


class SchemaFiller():
    """
    class to fill a json schema with dummy values or marshmallow-compatible types
    json schema can be loaded from an openapi specification

    expects either openapi_spec (path to a openapi specification file) or json_data (a json schema)
    """
    def __init__(
        self,
        openapi_spec: str = '',
        json_data: dict = {}
    ):
        if openapi_spec == '' and json_data == {}:
            raise ValueError("Either openapi_spec or json_data must be set")
        if openapi_spec:
            with open(openapi_spec, 'r') as f:
                openapi_data = yaml.safe_load(f)

            # always remove external references to the "base api" for easier serialization. inject the required components
            if "base/openapi.yaml" not in openapi_spec:
                base_path = path.join(path.dirname(path.abspath(__file__)), '..', 'openapi.yaml')
                with open(base_path, 'r') as f:
                    base_data = yaml.safe_load(f)
                openapi_data['components']['schemas'].update(base_data['components']['schemas'])

            json_str = json.dumps(openapi_data)
            json_str = re.sub('\\.\\./base/openapi\\.yaml', '', json_str)
            
            self.openapi = True
            self.json_data = jsonref.loads(json_str)
        else:
            self.openapi = False
            self.json_data = json_data


    def populate(self, schema: str, marshal: bool = False) -> OrderedDict:
        """
        populate a json schema definition with dummy data
        this does not work with external $refs
        reference: https://github.com/BhanuAkaveeti/Python/blob/master/GenerateJSONPayloadFromSchema/JSON%20Schema%20to%20Payload%20-%20OpenSource.py

        arguments:
            schema: key of the openapi schema to populate or key of the json schema to populate
            marshal: whether to cast filled in values to marshmallow-compatible types before returning

        returns:
            json schema populated with dummy data
        """
        def generatestring(data: OrderedDict) -> str:
            if 'minLength' in data.keys():
                minLength = data['minLength']
            else:
                minLength = 5

            if 'maxLength' in data.keys():
                maxLength = data['maxLength']
            else:
                maxLength = 25

            if 'enum' in data.keys():
                outstring = random.choice(data['enum'])
            elif 'pattern' in data.keys():
                outstring = rstr.xeger(data['pattern'])
            elif 'format' in data.keys():
                if data['format'] == 'date-time':
                    outstring = now.strftime("%Y-%m-%d %H:%M:%S")
                elif data['format'] == 'date':
                    outstring = now.strftime("%Y-%m-%d")
                else:
                    #pass
                    #print('Unknown format',data['format'])
                    outstring = ''.join(random.choice(letters) for i in range(minLength, maxLength)) # assume a normal string
            else:
                outstring = ''.join(random.choice(letters) for i in range(minLength, maxLength))

            return outstring


        def generatenumber(data: OrderedDict) -> float:
            if 'enum' in data.keys():
                outnumber = random.choice(data['enum'])
            elif 'format' in data.keys():
                if data['format'] in ('float','double'):
                    outnumber = random.random()
                else:
                    #pass
                    #print('Unknown format',data['format'])
                    outnumber = random.random() # assume a normal number
            else:
                outnumber = random.random()

            return outnumber


        def generateinteger(data) -> int:
            if 'multipleOf' in data.keys():
                multipleOf = data['multipleOf']
            else:
                multipleOf = 1

            if 'minimum' in data.keys():
                int32minimum = int(data['minimum'] / multipleOf)
                int64minimum = int(data['minimum'] / multipleOf)
            else:
                int32minimum = 100000
                int64minimum = 10000000000

            if 'maximum' in data.keys():
                int32maximum = int(data['maximum'] / multipleOf)
                int64maximum = int(data['maximum'] / multipleOf)
            else:
                int32maximum = 9000000
                int64maximum = 500000000000

            if 'enum' in data.keys():
                outinteger = random.choice(data['enum'])
            elif 'format' in data.keys():
                if data['format'] =='int32':
                    outinteger = random.randint(int32minimum, int32maximum) * multipleOf
                elif data['format'] =='int64':
                    outinteger = random.randint(int64minimum, int64maximum) * multipleOf
                else:
                    #pass
                    #print('Unknown format',data['format'])
                    outinteger = random.randint(int64minimum, int64maximum) * multipleOf # assume a normal integer
            else:
                outinteger = random.randint(int64minimum, int64maximum) * multipleOf

            return outinteger


        def generatevalue(data: OrderedDict, outdict: OrderedDict) -> list:
            outlist = []
            for key, value in data.items():
                if 'type' in data[key].keys():
                    if data[key]['type'] == 'string':
                        outdict[key] = generatestring(data[key])
                    elif data[key]['type'] == 'boolean':
                        outdict[key] = random.choice([True, False])
                    elif data[key]['type'] == 'integer':
                        outdict[key] = generateinteger(data[key])
                    elif data[key]['type'] == 'number':
                        outdict[key] = generatenumber(data[key])
                    elif data[key]['type'] == 'array':
                        if 'minItems' in data[key]:
                            minItems = data[key]['minItems']
                        else:
                            minItems = 1
                        if 'maxItems' in data[key]:
                            maxItems = data[key]['maxItems']
                        else:
                            maxItems = 3
                        if maxItems <= minItems:
                            maxItems = minItems + 1
                        if marshal:
                            arrayItems = 1
                        else:
                            arrayItems = random.randint(minItems, maxItems)
                        if 'type' in data[key]['items'].keys():
                            array = []
                            if data[key]['items']['type'] == 'string':
                                for n in range(0, arrayItems):
                                    arrayproperty = generatestring(data[key]['items'])
                                    array.append(arrayproperty)
                                outdict[key] = array
                            elif data[key]['items']['type'] == 'boolean':
                                for n in range(0,arrayItems):
                                    arrayproperty = random.choice([True, False])
                                    array.append(arrayproperty)
                                outdict[key] = array
                            elif data[key]['items']['type'] == 'integer':
                                for n in range(0,arrayItems):
                                    arrayproperty = generateinteger(data[key]['items'])
                                    array.append(arrayproperty)
                                outdict[key] = array
                            elif data[key]['items']['type'] == 'number':
                                for n in range(0, arrayItems):
                                    arrayproperty = generatenumber(data[key]['items'])
                                    array.append(arrayproperty)
                                outdict[key] = array
                            elif data[key]['items']['type'] == 'object':
                                arraydict       = OrderedDict()
                                arrayproperties = data[key]['items']['properties']
                                outdict[key]    = generatevalue(arrayproperties, arraydict)
                            else:
                                pass
                                #print('Unknown format',data[key]['format'],'for property',key)
                        elif '$ref' in data[key]['items'].keys():
                            arraypath         = data[key]['items']['$ref'].split('/')
                            arraydict         = OrderedDict()
                            arraydictobj      = OrderedDict()
                            #arrayproperties   = jsondata['definitions'][arraypath[2]]['properties'] # TODO should be? root_json['components']['schemas'][refpath[-1]]['properties']
                            arrayproperties   = self.json_data['components']['schemas'][refpath[-1]]['properties']
                            arraydictobj[key] = generatevalue(arrayproperties, arraydict)
                            arrayofdict.append(arraydictobj)
                        else:
                            pass
                            #print('Unknown array property',data[key]['type'],'for property',key)
                    elif data[key]['type'] == 'object':
                        arraydict       = OrderedDict()
                        arrayproperties = data[key]['properties']
                        outdict[key]    = generatevalue(arrayproperties, arraydict)[0]
                    else:
                        pass
                        #print('Unknown type',data[key]['type'],'for property',key)
                elif '$ref' in data[key].keys():
                    refpath       = data[key]['$ref'].split('/')
                    refdict       = OrderedDict()
                    refList       = []
                    #refproperties = jsondata['definitions'][refpath[2]]['properties'] # TODO should be? root_json['components']['schemas'][refpath[-1]]['properties']
                    refproperties = self.json_data['components']['schemas'][refpath[-1]]['properties']
                    refList       = generatevalue(refproperties, refdict)
                    outdict[key]  = refList[0]

            outlist.append(outdict)
            return outlist


        def to_marshmallow(serialized: OrderedDict) -> OrderedDict: # first call is expected to be a dict or OrderedDict
            if type(serialized) == list: # at this point we expect lists with only one element
                out = None
                if type(serialized[0]) == str:
                    out = fields.String()
                    #out.error_messages = {}
                elif type(serialized[0]) == bool:
                    out = fields.Boolean()
                    #out.error_messages = {}
                elif type(serialized[0]) == int:
                    out = fields.Int()
                    #out.error_messages = {}
                elif type(serialized[0]) == float:
                    out = fields.Float() # fields.Decimal()?
                    #out.error_messages = {}
                elif type(serialized[0]) in [dict, type, OrderedDict]: # recurse
                    out = fields.Nested(to_marshmallow(serialized[0]))
                    #out.error_messages = {}
                return out
            else: # we expect a dict or OrderedDict
                marshmalled = OrderedDict()
                for key in serialized:
                    if type(serialized[key]) == str:
                        out = fields.String()
                        #out.error_messages = {}
                        marshmalled[key] = out
                    elif type(serialized[key]) == bool:
                        out = fields.Boolean()
                        #out.error_messages = {}
                        marshmalled[key] = out
                    elif type(serialized[key]) == int:
                        out = fields.Int()
                        #out.error_messages = {}
                        marshmalled[key] = out
                    elif type(serialized[key]) == float:
                        out = fields.Float() # fields.Decimal()?
                        #out.error_messages = {}
                        marshmalled[key] = out
                    elif type(serialized[key]) == list: # recurse, lists are shit
                        out = fields.List(to_marshmallow(serialized[key]))
                        #out.error_messages = {}
                        marshmalled[key] = out
                    elif type(serialized[key]) in [dict, type, OrderedDict]: # recurse
                        out = fields.Nested(to_marshmallow(serialized[key]))
                        #out.error_messages = {}
                        marshmalled[key] = out
                return marshmalled


        if self.openapi:
            schema = self.json_data['components']['schemas'][schema]['properties']
        else:
            schema = self.json_data[schema]

        letters = string.ascii_uppercase
        now     = datetime.now(UTC)

        dictobj     = OrderedDict()
        initobj     = OrderedDict()
        arrayofdict = []
        finaldict   = OrderedDict()

        dictobj['root'] = generatevalue(schema, initobj)
        arrayofdict.append(dictobj)

        for obj in arrayofdict:
            if 'root' in obj.keys():
                for key, value in obj["root"][0].items():
                    finaldict[key] = value
            else:
                for key, value in obj.items():
                    finaldict[key] = value

        newfinal = OrderedDict()
        if marshal: # convert values to marshmallow-compatible types
            newfinal = to_marshmallow(finaldict)
            return newfinal # has to be wrapped #x['root'] = fill_jsonschema(...); Schema.from_dict(x)

        return finaldict
