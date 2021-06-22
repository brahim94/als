from odoo import api, fields, models

class ResMedia(models.Model):
    _name = "res.media"
    _rec_name = 'title'

    active = fields.Boolean(string='Active', default=True)
    media_type = fields.Selection([('slider', 'Sliders'),
                                    ('news', 'News'),
                                    ('faq', 'FAQ')], string="Type")
    title = fields.Char(string='Titre')
    description = fields.Text('Description')
    image_res = fields.Image('Image', copy=False, attachment=True, max_width=1024, max_height=1024)
    state = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Inactive'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='active', compute="_comute_state")

    @api.depends('active')
    def _comute_state(self):
        for record in self:
            if record.active == True:
                record.state = 'active'
            if record.active == False:
                record.state = 'archived'

class ResStation(models.Model):
    _name = "res.station"

    station_id = fields.Many2one('res.partner',domain="[('partner_type', '=', 'station')]")
    parnter_id = fields.Many2one('res.partner')
    terminus = fields.Boolean(string="Terminus")
    correspondence_ids = fields.Many2many('res.partner',domain="[('partner_type', '=', 'line')]")
    sequence_ref = fields.Integer('Order', compute="_sequence_ref")

    @api.depends('parnter_id.station_ids')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.parnter_id.station_ids:
                no += 1
                l.sequence_ref = no

class ResTimeTable(models.Model):
    _name = "res.timetable"

    name = fields.Char("Name")

class ResPeriod(models.Model):
    _name = "res.period"

    name = fields.Char("Name")

class ResStation(models.Model):
    _name = "res.departure"

    period = fields.Many2one('res.period', string="Period")
    timetable = fields.Many2one('res.timetable', string="Timetable")
    station_id = fields.Many2one('res.partner', string="Station")
    parnter_id = fields.Many2one('res.partner')
    first_departure = fields.Float('First departure')
    last_departure = fields.Float('Last departure')

class ResPartner(models.Model):
    _inherit = "res.partner"

    active = fields.Boolean(string='Active', default=True)
    partner_type = fields.Selection([('client', 'Clients'),
                                    ('pos', 'Point of Sales'),
                                    ('line', 'Lines'),
                                    ('station', 'Stations')], string="Partner Type")
    code = fields.Char(string='Code')
    cin = fields.Char(string='CIN')
    birthday = fields.Date("Birthday")
    gender = fields.Selection([('Male', 'Male'),
                                    ('Female', 'Female')], string="Gender")
    rep_name = fields.Char(string='Name')
    rep_cin = fields.Char(string='CIN')
    rep_phone = fields.Char(string='Phone')
    inst_name = fields.Char(string='Name')
    inst_cne = fields.Char(string='CNE')
    inst_address = fields.Char(string='Address')

    number_of_buses = fields.Integer(string='Number of buses')
    frequency = fields.Integer(string='Frequency')
    rate = fields.Float(string='Rate')
    mileage = fields.Float(string='Mileage')
    travel_time = fields.Float(string='Travel time')

    station_ids = fields.One2many('res.station','parnter_id', string="Station")
    departure_ids = fields.One2many('res.departure','parnter_id', string="Station")
    compaute_station_ids = fields.Many2many('res.partner', compute="_compute_station_record")
    state = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Inactive'),
        ], string='Status', store=True, copy=False, index=True, tracking=3, default='active', compute="_comute_state")

    @api.depends('active')
    def _comute_state(self):
        for record in self:
            if record.active == True:
                record.state = 'active'
            if record.active == False:
                record.state = 'archived'

    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        values = super(ResPartner, self).default_get(default_fields)
        if self.env.context.get('partner_type') == 'client':
            values.update({'partner_type': 'client'})
        if self.env.context.get('partner_type') == 'pos':
            values.update({'partner_type': 'pos'}) 
        if self.env.context.get('partner_type') == 'line':
            values.update({'partner_type': 'line'}) 
        if self.env.context.get('partner_type') == 'station':
            values.update({'partner_type': 'station'})
        return values

    @api.depends('station_ids','departure_ids')
    def _compute_station_record(self):
        for record in self:
            compaute_station_ids = []
            for st in record.station_ids:
                if st.terminus:
                    compaute_station_ids.append(st.station_id.id)
            record.compaute_station_ids = compaute_station_ids
