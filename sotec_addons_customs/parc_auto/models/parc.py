from odoo import fields,api,models,tools,_
from dateutil.relativedelta import relativedelta
from datetime import datetime


class FleetTypePermis(models.Model):
    _name = 'fleet.type.permis'

    name = fields.Char("Categorie de permis", required=True)
    description = fields.Text(string='Description')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    permis = fields.Char(string='No permis', required=True)
    dte_expire = fields.Date("Date d'expiration")
    type_permis = fields.Many2one('fleet.type.permis', 'Catégorie de permis', required=True)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # Document technique - Assurance
    assureur_id = fields.Many2one('res.partner', 'Assurance/Assureur')
    date_souscription = fields.Date('Date Souscription')
    montant_souscription = fields.Float('Montant Souscription')
    duree_souscription = fields.Integer('Durée Souscription (En Mois)')
    date_expiration = fields.Date('Date Expiration', compute = '_update_date_expiration_assurance_', store = True)
    couverture_assurance = fields.Text('Couverture assurance')

    # Document technique - visite technique
    centre_controle_id = fields.Many2one('res.partner', 'Centre de controle')
    date_visite_technique = fields.Date('Date Visite technique')
    montant_visite = fields.Float('Montant Visite')
    duree_visite = fields.Integer('Durée Visite (En mois)')
    date_expiration_visite_technique = fields.Date('Date Expiration Visite', compute = '_update_date_expiration_visite_technique_', store = True)
    
    # Document technique - taxe
    annee_paiement = fields.Integer('Annee Paiement')
    date_paiement_taxe = fields.Date('Date Paiement taxe')
    montant_taxe = fields.Float('Montant Taxe')

    @api.depends('date_souscription','duree_souscription')
    def _update_date_expiration_assurance_(self):
        for val in self:
            if val.date_expiration:
                date_expiration_exces = (datetime.strptime(str(val.date_souscription),'%Y-%m-%d') + relativedelta(months=val.duree_souscription)).strftime('%Y-%m-%d')
                val.date_expiration = (datetime.strptime(str(date_expiration_exces),'%Y-%m-%d') - relativedelta(days = 1)).strftime('%Y-%m-%d')
        
    @api.depends('date_visite_technique','duree_visite')
    def _update_date_expiration_visite_technique_(self):
        for val in self:
            if val.date_expiration_visite_technique:
                date_expiration_visite_technique_exces = (datetime.strptime(str(val.date_visite_technique),'%Y-%m-%d') + relativedelta(months=val.duree_visite)).strftime('%Y-%m-%d')
                val.date_expiration_visite_technique = (datetime.strptime(str(date_expiration_visite_technique_exces),'%Y-%m-%d') - relativedelta(days = 1)).strftime('%Y-%m-%d')

    
    def historisation(self):
        champs_documents_techniques = self.env['fleet.vehicle'].search([('id','=',self.id)])
        champ_assureur = champs_documents_techniques.assureur_id
        champ_date_assurance = champs_documents_techniques.date_souscription
        champ_visite_centre_controle = champs_documents_techniques.centre_controle_id
        champ_date_visite = champs_documents_techniques.date_visite_technique
        
        if champ_assureur or champ_date_assurance:
            self.sudo().env['fleet.vehicle.parc.assurance.history'].create({
                'vehicule_id': self.id,
                'assureur_id': self.assureur_id.id,
                'date_souscription': champ_date_assurance, 
                'montant_souscription': self.montant_souscription,
                'duree_souscription': self.duree_souscription,
                'date_expiration': self.date_expiration, 
                'couverture_assurance': self.couverture_assurance,
            })

        if champ_visite_centre_controle or champ_date_visite:
            self.sudo().env['fleet.vehicle.parc.visite.technique.history'].create({
                'vehicule_id': self.id,
                'centre_controle_id': self.centre_controle_id.id,
                'date_visite_technique': champ_date_visite, 
                'montant_visite': self.montant_visite,
                'duree_visite': self.duree_visite,
                'date_expiration_visite_technique': self.date_expiration_visite_technique, 
            })
    
    def write(self,vals):
        self.historisation()
        return super(FleetVehicle,self).write(vals)
    
    # @api.model
    # def create(self,vals):
    #     self.historisation()
    #     return super(FleetVehicle,self).create(vals)


class FleetVehicleParcAssuranceHistory(models.Model):
    _name = 'fleet.vehicle.parc.assurance.history'

    # Historique - Assurance
    vehicule_id = fields.Many2one('fleet.vehicle', 'Véhicule')
    assureur_id = fields.Many2one('res.partner', 'Assurance/Assureur')
    date_souscription = fields.Date('Date Souscription')
    montant_souscription = fields.Float('Montant')
    duree_souscription = fields.Integer('Durée (En Mois)')
    date_expiration = fields.Date('Date Expiration')
    couverture_assurance = fields.Text('Couverture')

class FleetVehicleParcVisiteTechniqueHistory(models.Model):
    _name = 'fleet.vehicle.parc.visite.technique.history'

    # Historique - Visite technique
    vehicule_id = fields.Many2one('fleet.vehicle', 'Véhicule')
    centre_controle_id = fields.Many2one('res.partner', 'Centre de controle')
    date_visite_technique = fields.Date('Date Visite')
    montant_visite = fields.Float('Montant')
    duree_visite = fields.Integer('Durée (En mois)')
    date_expiration_visite_technique = fields.Date('Date Expiration')


class FleetFuel(models.Model):
    _name = 'fleet.fuel'
    _rec_name = 'vehicle_id'

    vehicle_id = fields.Many2one("fleet.vehicle", "Véhicule", required=True)
    prix = fields.Float("Prix du litre", required=True)
    quantite = fields.Float("Quantité", required=True)
    conducteur = fields.Many2one("res.partner", "Conducteur", related='vehicle_id.driver_id')
    license_plate = fields.Char("Immatriculation", related='vehicle_id.license_plate')
    total = fields.Float("Prix total", compute='_mnt_total')
    dte = fields.Date("Date", required=True)
    kilometre = fields.Float("Kilométrage")
    reference = fields.Char("Référence facture")
    observation = fields.Text("Autres informations")
    
    @api.depends('prix', 'quantite')
    def _mnt_total(self):
        for vals in self:
            vals.total = vals.prix * vals.quantite