#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from scoring import get_interests, get_score

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field(object):
    value = None

    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable

    def set_value(self, value):
        self.value = value
        return self

    def validate(self):
        return self.check_required() and self.check_nullable()

    def check_required(self):
        return not self.required or self.value is not None

    def check_nullable(self):
        return self.nullable or (self.value is not None and len(self.value) != 0)

    def empty(self):
        return self.value is None or len(self.value) == 0

    def count(self):
        return 0 if self.value is None else len(str(self.value))

    def __str__(self):
        return '' if self.value is None else self.value.encode('utf-8')

    def __radd__(self, other):
        return str(self) + other

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.value)


class IterableField(Field):
    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, item):
        return self.value[item]


class CharField(Field):
    pass


class ArgumentsField(IterableField):
    pass


class EmailField(CharField):
    def validate(self):
        if not self.required and self.nullable and len(str(self.value)) == 0:
            return True
        return '@' in self.value


class PhoneField(Field):
    PHONE_LENGTH = 11
    PHONE_STARTS_WITH = '7'

    def validate(self):
        if not self.required and self.nullable and len(str(self.value)) == 0:
            return True
        return str(self.value).startswith(self.PHONE_STARTS_WITH) and len(str(self.value)) == self.PHONE_LENGTH


class DateField(Field):
    date_format = '%d.%m.%Y'

    def validate(self):
        try:
            self.parse_date()
            return True
        except BaseException:
            return False

    def parse_date(self):
        return datetime.datetime.strptime(self.value, self.date_format)


class BirthDayField(DateField):
    MAX_AGE = 70

    def validate(self):
        if not self.required and self.nullable and len(str(self)) == 0:
            return True
        if not super(BirthDayField, self).validate():
            return False
        date = self.parse_date()
        age = self.age(date)
        return age <= self.MAX_AGE

    def age(self, date):
        today = datetime.date.today()
        years = today.year - date.year
        if today.month < date.month or (today.month == date.month and today.day < date.day):
            years -= 1
        return years


class GenderField(Field):
    POSSIBLE_VALUES = [0, 1, 2]

    def __str__(self):
        return '' if self.value is None else str(self.value)

    def validate(self):
        if not self.required and self.nullable and len(str(self)) == 0:
            return True
        return self.value in self.POSSIBLE_VALUES


class ClientIDsField(IterableField):
    def validate(self):
        if not super(ClientIDsField, self).validate():
            return False
        if len(self.value) == 0:
            return False
        for val in self.value:
            try:
                int(val)
            except ValueError:
                return False
        return True


class BaseRequest(object):
    fields = {}
    is_admin = False
    errors = ''

    def __init__(self, arguments):
        for field_name, field in self.fields.items():
            field.set_value(arguments[field_name] if field_name in arguments else None)

    def execute(self):
        self.validate()
        return self.execute_api()

    def validate(self):
        errors = ''
        for field_name, field in self.fields.items():
            if not field.validate():
                errors += field_name + ' argument is incorrect. '
        self.errors = errors

    def execute_api(self):
        if len(self.errors) > 0:
            return self.errors, INVALID_REQUEST
        else:
            return self.get_api(), OK

    def get_api(self):
        pass

    def additional_validate(self):
        return ''


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    fields = {
        'clients_ids': client_ids,
        'date': date
    }

    def get_api(self):
        store = {
            "nclients": self.client_ids.count()
        }
        result = {}
        for client_id in self.client_ids:
            result[client_id] = get_interests(store, client_id)
        return result


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    needed_pairs = [
        [phone, email],
        [first_name, last_name],
        [gender, birthday]
    ]

    fields = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "birthday": birthday,
        "gender": gender
    }

    def get_api(self):
        store = {
            "has": self.get_not_empty_fields()
        }
        if self.is_admin:
            return {"score": 42}
        return {
            "score": get_score(store, str(self.phone), str(self.email), str(self.birthday),
                                    str(self.gender), str(self.first_name), str(self.last_name))
        }

    def get_not_empty_fields(self):
        not_empty_fields = []
        for field_name, field in self.fields.items():
            if field.count() > 0:
                not_empty_fields.append(field_name)

    def additional_validate(self):
        for pair in self.needed_pairs:
            pair_exist = True
            for field in pair:
                if field.empty():
                    pair_exist = False
            if pair_exist:
                return ''
        return 'There is no required pair of values'


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    REQUEST_METHOD = {
        'online_score': OnlineScoreRequest,
        'clients_interests': ClientsInterestsRequest
    }

    fields = {
        'account': account,
        'login': login,
        'token': token,
        'arguments': arguments,
        'method': method
    }

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def execute_api(self):
        if len(self.errors) > 0:
            return self.errors, INVALID_REQUEST
        else:
            return self.get_api()

    def get_api(self):
        if self.method in self.REQUEST_METHOD:
            request_object = self.REQUEST_METHOD[self.method](self.arguments)
            if self.is_admin:
                request_object.is_admin = True
            try:
                request_object.validate()
                return request_object.execute()
            except BaseException as e:
                logging.exception(e.message)
                return None, BAD_REQUEST
        else:
            return None, NOT_FOUND


def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    method_request = MethodRequest(request['body'])
    if not check_auth(method_request):
        response, code = None, FORBIDDEN
        return response, code
    return method_request.execute()


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception as e:
            logging.exception(e.message)
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception, e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND
        if code is None:
            code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
