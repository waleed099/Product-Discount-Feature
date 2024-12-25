from odoo import models, fields , api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Add discount percentage field
    discount_percentage = fields.Float(string="Discount Percentage", default=0.0)
    discounted_price = fields.Float(string="Discounted Price", compute="_compute_discounted_price", store=True)
    
    
    @api.depends('list_price', 'discount_percentage')
    def _compute_discounted_price(self):
        for product in self:
            if product.discount_percentage > 0:
                discount = (product.list_price * product.discount_percentage) / 100
                product.discounted_price = product.list_price - discount
            else:
                product.discounted_price = product.list_price



    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # Add the discounted price field
    discount_percentage = fields.Float(related='product_id.discount_percentage', string="Discount Percentage", store=True)
    discounted_price = fields.Float(related='product_id.discounted_price', string="Discounted Price", store=True)
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Ensure the price reflects the discounted price
            if self.product_id.discount_percentage > 0:
                self.price_unit = self.product_id.discounted_price
            else:
                self.price_unit = self.product_id.list_price

    @api.depends('product_id', 'product_uom_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            # Apply the discount logic here too if necessary
            if line.product_id.discount_percentage > 0:
                line.price_subtotal = line.product_uom_qty * line.product_id.discounted_price
            else:
                line.price_subtotal = line.product_uom_qty * line.product_id.list_price
            super(SaleOrderLine, line)._compute_amount()
                
                

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
   

    
    
    
    # Ensure that the price reflects the discounted price when creating a new order
    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        for line in order.order_line:
            if line.product_id.discount_percentage > 0:
                line.price_unit = line.product_id.discounted_price
            else:
                line.price_unit = line.product_id.list_price
        return order
    
    
   
    # Ensure that the price reflects the discounted price when updating an order
    def action_confirm(self):
        for line in self.order_line:
            if line.product_id.discount_percentage > 0:
                # Ensure that the price_unit reflects the discounted price when confirming
                line.price_unit = line.product_id.discounted_price
        return super(SaleOrder, self).action_confirm()




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    
    discounted_price = fields.Float(related='product_id.discounted_price', string="Discounted Price", store=True)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = self.env['product.product'].browse(vals.get('product_id'))
            if product and product.discount_percentage > 0:
                vals['price_unit'] = product.discounted_price
        return super(AccountMoveLine, self).create(vals_list)


