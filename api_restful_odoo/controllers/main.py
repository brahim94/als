"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import re
import ast
import json
import functools
import logging
from odoo.exceptions import AccessError

from odoo import http
from odoo.addons.api_restful_odoo.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request

_logger = logging.getLogger(__name__)


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


def cast_value(field_type, value):
    if field_type in ['char', 'selection', 'text', 'html']:
        return str(value)
    elif field_type in ['integer', 'many2one']:
        return int(value)
    elif field_type in ['float', 'monetary']:
        return float(value)
    elif field_type in ['date', 'datetime']:
        return value.isoformat()
    elif field_type == 'boolean':
        return bool(int(value))
    else: 
        return value

_routes = ["/api/<model>", "/api/<model>/<id>", "/api/<model>/<id>/<action>","/api/raw/<model>/<method>"]


class APIController(http.Controller):
    """."""

    def __init__(self):
        self._model = "ir.model"


    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["GET"], csrf=False)
    def get(self, model=None, method=None, id=None, **payload):
        """
        """
        try:
            ioc_name = model
            model = request.env[self._model].search([("model", "=", model)], limit=1)
            if model:
                domain, fields, offset, limit, order = extract_arguments(payload)
                data = request.env[model.model].search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order,
                )
                
                if model and method:
                    if method == 'get_sliders':
                        records = request.env[model.model].sudo().search([('media_type','=','slider'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'title':record.title,'description': record.description,'image_res': record.image_res})

                    if method == 'get_news':
                        records = request.env[model.model].sudo().search([('media_type','=','news'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'title':record.title,'description': record.description,'image_res': record.image_res})

                    if method == 'get_faq':
                        records = request.env[model.model].sudo().search([('media_type','=','faq'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'title':record.title,'description': record.description})

                    if method == 'get_products':
                        records = request.env[model.model].sudo().search([])
                        data = []
                        for record in records:
                            data.append({'id':record.id,'description': record.description,'name':record.name,'image_1920': record.image_1920})

                    if method == 'get_pos':
                        records = request.env[model.model].sudo().search([('partner_type','=','pos'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'id':record.id,
                                        'code': record.code,
                                        'name':record.name,
                                        'street': record.street,
                                        'city':record.city,
                                        'phone':record.phone,
                                        'partner_latitude':record.partner_latitude,
                                        'partner_longitude': record.partner_longitude})

                    if method == 'get_stations':
                        records = request.env[model.model].sudo().search([('partner_type','=','station'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'id':record.id,
                                        'code': record.code,
                                        'name':record.name,
                                        'partner_latitude':record.partner_latitude,
                                        'partner_longitude': record.partner_longitude})

                    if method == 'get_lines':
                        records = request.env[model.model].sudo().search([('partner_type','=','line'),('state','=','active')])
                        data = []
                        for record in records:
                            station_list = []
                            for station_rec in record.station_ids:
                                station_list.append({'order':station_rec.sequence_ref,
                                                    'station_id':station_rec.station_id.id,
                                                    'terminus': station_rec.terminus,
                                                    'correspondence_ids': station_rec.correspondence_ids.ids})
                            departure_list = []
                            for departure in record.departure_ids:
                                departure_list.append({'period':departure.period.id,
                                                    'timetable':departure.timetable.id,
                                                    'station_id': departure.station_id.id,
                                                    'first_departure': departure.first_departure,
                                                    'last_departure':departure.last_departure})
                            data.append({'id':record.id,
                                        'code': record.code,
                                        'name':record.name,
                                        'rate':record.rate,
                                        'frequency': record.frequency,
                                        'mileage': record.mileage,
                                        'travel_time': record.travel_time,
                                        'nbr_buses': record.number_of_buses,
                                        'station_ids': station_list,
                                        'departure_ids': departure_list
                                        })

                    if method == 'get_claim_types':
                        records = request.env[model.model].sudo().search([('active','=',True)])
                        data = []
                        for record in records:
                            data.append({'name':record.name})

                    if method == 'get_claim_categories':
                        records = request.env[model.model].sudo().search([])
                        data = []
                        for record in records:
                            data.append({'name':record.name,'claim_type': record.claim_type})
                            
                    if data:
                        return valid_response(data)
                    else:
                        return valid_response(data)
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % ioc_name,
            )
        except AccessError as e:

            return invalid_response("Access error", "Error: %s" % e.name)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["POST"], csrf=False)
    def post(self, model=None, id=None, **payload):
        """Create a new record.
        Basic sage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'token': 'token'
        }
        sale_order = requests.post(url="%s/api/sale.order/" %"http://localhost:8069", data=payload, headers=headers)
        print(sale_order)
        print(sale_order.text)

        order_id = json.loads(sale_order.text).get("data")[0].get('id')
        print(order_id)

        payload = {
            'price_unit': 4000,
            'product_id': 1,
            'order_id': order_id
        }

        order_line1 = requests.post(url="%s/api/sale.order.line/" %"http://localhost:8069", data=payload, headers=headers)
        print(order_line1)
        print(order_line1.text)


        payload = {
            'price_unit': 5000,
            'product_id': 2,
            'order_id': order_id

        }

        order_line2 = requests.post(url="%s/api/sale.order.line/" %"http://localhost:8069", data=payload, headers=headers)
        print(order_line2)
        print(order_line2.text)
        """
        ioc_name = model
        model = request.env[self._model].search([("model", "=", model)], limit=1)
        values = {}
        fields = []
        if model:
            try:
                # changing IDs from string to int.
                for k, v in payload.items():
                    field_type = request.env['ir.model.fields'].search([('model_id','=',model.id),('name','=',k)], limit=1).ttype
                    values[k] = cast_value(field_type, v)
                    fields.append(k)
                resource = request.env[model.model].create(values)
            except Exception as e:
                request.env.cr.rollback()
                return invalid_response("params", e)
            else:
                data = resource.read(fields)
                if resource:
                    return valid_response(data)
                else:
                    return valid_response(data)
        return invalid_response("invalid object model", "The model %s is not available in the registry." % ioc_name,)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["PUT"], csrf=False)
    def put(self, model=None, id=None, **payload):
        """
        import requests

        url = "http://localhost:8069/api/res.partner/15"

        payload = {"name":"partner name edited"}
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'token': "_63e2db121d0ab33a3ea3ddb933249d9291c67c4f"
            }

        response = requests.request("PUT", url, data=payload, headers=headers)

        print(response.text)
        """
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response("invalid object id", "invalid literal %s for id with base " % id)
        _model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        if not _model:
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % model, 404,
            )
        try:
            record = request.env[_model.model].sudo().browse(_id)
            record.write(payload)
        except Exception as e:
            request.env.cr.rollback()
            return invalid_response("exception", e.name)
        else:
            return valid_response(record.read())

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["DELETE"], csrf=False)
    def delete(self, model=None, id=None, **payload):
        """."""
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response("invalid object id", "invalid literal %s for id with base " % id)
        try:
            record = request.env[model].sudo().search([("id", "=", _id)])
            if record:
                record.unlink()
            else:
                return invalid_response("missing_record", "record object with id %s could not be found" % _id, 404,)
        except Exception as e:
            request.env.cr.rollback()
            return invalid_response("exception", e.name, 503)
        else:
            return valid_response("record %s has been successfully deleted" % record.id)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["PATCH"], csrf=False)
    def patch(self, model=None, id=None, action=None, **payload):
        """
        import requests

        url = "http://localhost:8069/api/sale.order/81"

        payload = {"_method":"action_confirm"}
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'token': "_63e2db121d0ab33a3ea3ddb933249d9291c67c4f"
            }

        response = requests.request("PATCH", url, data=payload, headers=headers)

        print(response.text)
        """
        action = action if action else payload.get('_method')
        args = []

        try:
            _id = int(id)
        except Exception as e:
            return invalid_response("invalid object id", "invalid literal %s for id with base" % id)
        try:
            record = request.env[model].sudo().search([("id", "=", _id)])
            _callable = action in [method for method in dir(record) if callable(getattr(record, method))]
            if record and _callable:
                # action is a dynamic variable.
                getattr(record, action)(*args) if args else getattr(record, action)() 
            else:
                return invalid_response(
                    "missing_record",
                    "record object with id %s could not be found or %s object has no method %s" % (_id, model, action),
                    404,
                )
        except Exception as e:
            return invalid_response("exception", e, 503)
        else:
            return valid_response("record %s has been successfully update" % record.id)
