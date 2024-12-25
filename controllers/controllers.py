from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment import utils as payment_utils
from odoo import fields

import  logging

_log = logging.getLogger(__name__)

class CustomWebsiteSale(WebsiteSale):

    
    
    
    
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
        self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
        product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """

     

        # Get or create the order
        order = request.website.sale_get_order(force_create=True)
        if not order or order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=True)
            else:
                return {'lines': [], 'warning': 'Unable to retrieve order'}
        
        
        # Ensure the product exists
        product = request.env['product.product'].browse(product_id)
        if not product.exists():
            return {'lines': [], 'warning': 'Product not found'}

      
        
        product = request.env['product.product'].browse(product_id)
        
        if product:
            # Determine the discounted price
            price = product.list_price
            if hasattr(product, 'discount_percentage') and product.discount_percentage > 0:
                price = product.discounted_price or product.list_price  # Use discounted price if available
                
                
        

        values = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            **kw
        )

        
        for line in order.order_line:
            if hasattr(line.product_id, 'discount_percentage') and line.product_id.discount_percentage > 0:
                line.price_unit = line.product_id.discounted_price
            else:
                line.price_unit = line.product_id.list_price
            
        
        request.session['website_sale_cart_quantity'] = order.cart_quantity

        values['notification_info'] = self._get_cart_notification_information(order, [values['line_id']])
        request.session['website_sale_cart_quantity'] = order.cart_quantity

        if not order.cart_quantity:
            request.website.sale_reset()
            return values

        values['cart_quantity'] = order.cart_quantity
        values['minor_amount'] = payment_utils.to_minor_currency_units(
            order.amount_total, order.currency_id
        ),
        values['amount'] = order.amount_total

        if not display:
            return values
        
        values['cart_ready'] = order._is_cart_ready()
        values['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
            "website_sale.cart_lines", {
                'website_sale_order': order,
                'date': fields.Date.today(),
                'suggested_products': order._cart_accessories()
            }
        )
       
        values['website_sale.total'] = request.env['ir.ui.view']._render_template(
            "website_sale.total", {
                'website_sale_order': order,
            }
        )
        return values
    

    
    
   
    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        
       
        for line in order.order_line:
            if hasattr(line.product_id, 'discount_percentage') and line.product_id.discount_percentage > 0:
                line.price_unit = line.product_id.discounted_price 
        
                
        return super(CustomWebsiteSale, self).shop_payment(**post)
    
    
    
    
    