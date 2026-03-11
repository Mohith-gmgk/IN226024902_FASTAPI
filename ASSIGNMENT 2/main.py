from fastapi import FastAPI,Query
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query, Response, status
from typing import Optional
from typing import List

app = FastAPI()

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrderproducts(BaseModel):
    company_name: str = Field(..., min_length=2,max_length=100)
    contact_mail: str = Field(..., min_length=2,max_length=100)
    items_list:List[OrderItem]=Field(..., min_items=1)


class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class CustomerFeedbackonProdcuts(BaseModel):
    customer_name: str = Field(..., min_length=2,max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

class OrderRequest(BaseModel):                          # Day 2
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
 
class NewProduct(BaseModel):                            # Day 4
    name:     str  = Field(..., min_length=2, max_length=100)
    price:    int  = Field(..., gt=0)
    category: str  = Field(..., min_length=2)
    in_stock: bool = True

feedback=[]

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop Stand',        'price': 1299, 'category': 'Electronics', 'in_stock': True },
    {'id': 6, 'name': 'Mechanical Keyboard',          'price':  2499, 'category':'Electronics',  'in_stock': True },
    {'id': 7, 'name': 'Webcam',          'price':  1899, 'category':'Electronics',  'in_stock': False },
]
orders = []
order_counter = 1

#Endpoint- Get Products Summary
@app.get('/products/summary')
def get_products_summary():
    in_stock_count=len([p for p in products if p["in_stock"]])
    out_stock_count=len([p for p in products if not p["in_stock"]])
    expensive_product=max(products, key=lambda p: p["price"])
    cheapest_product=min(products, key=lambda p: p["price"])
    categories=list(set([p["category"] for p in products]))

    return {"total products": len(products), "in_stock_count": in_stock_count, "out_of_stock_count": out_stock_count, "most_expensive": {"name": expensive_product["name"] ,"price": expensive_product["price"]}, "cheapest": {"name": cheapest_product["name"] ,"price": cheapest_product["price"]}, "categories": categories,}


@app.post('/products')
def add_product(new_product: NewProduct, response: Response):
    # Check for duplicate name (case-insensitive)
    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}
 
    # Auto-generate next ID
    next_id = max(p['id'] for p in products) + 1
 
    product = {
        'id':       next_id,
        'name':     new_product.name,
        'price':    new_product.price,
        'category': new_product.category,
        'in_stock': new_product.in_stock,
    }
    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}


@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    response:   Response,
    in_stock:   bool = Query(None, description='Update stock status'),
    price:      int  = Query(None, description='Update price'),
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
 
    if in_stock is not None:     # must use 'is not None' — False is a valid value
        product['in_stock'] = in_stock
    if price is not None:
        product['price'] = price
 
    return {'message': 'Product updated', 'product': product}

 
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
 
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}


def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None

def calculate_total(product: dict, quantity: int) -> int:
    return product['price'] * quantity

def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    result = products
    if category  is not None: result = [p for p in result if p['category']==category]
    if min_price is not None: result = [p for p in result if p['price']>=min_price]
    if max_price is not None: result = [p for p in result if p['price']<=max_price]
    if in_stock  is not None: result = [p for p in result if p['in_stock']==in_stock]
    return result

@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
# Endpoint 1 — Return all products 
@app.get('/products')
def get_all_products():
    
    return {'products': products, 'total': len(products)}

# Endpoint 2 — Return one product by its ID 
@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    max_price: int  = Query(None, description='Maximum price'),
    min_price: int  = Query(None, description='Minimum price'),
    in_stock:  bool = Query(None, description='True = in stock only')
):
    result = products 
 
    if category:
        result = [p for p in result if p['category'] == category]
 
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
 
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    
    if min_price:
        result = [p for p in result if p['price'] >= min_price]
 
    return {'filtered_products': result, 'count': len(result)}

@app.get('/products/compare')
def compare_products(product_id_1:int=Query(...), product_id_2:int=Query(...)):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1: return {'error': f'Product {product_id_1} not found'}
    if not p2: return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {'product_1':p1,'product_2':p2,
'better_value':cheaper['name'],
'price_diff':abs(p1['price']-p2['price'])}

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    product = find_product(order_data.product_id)
    if not product:
        return {'error': 'Product not found'}
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
    total = calculate_total(product, order_data.quantity)
    order = {'order_id':order_counter,'customer_name':order_data.customer_name,'product':product['name'],'quantity':order_data.quantity,'delivery_address':order_data.delivery_address,'total_price':total,'status':'pending'}
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}

@app.get('/orders/{order_id}')
def get_order_by_id(order_id: int):
    for order in orders:
        if order['order_id'] == order_id:
            return {'order': order}
    return {'error': 'Order not found'}

@app.patch('/orders/{order_id}/confirm')
def confirm_order(order_id : int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message":"Order Confirmed","order":order}
        return {"error":"Order not found"}
        

# Endpoint 3 - Return in stock products
@app.get('/products/in_stock')
def get_in_stock_products():
    result = [p for p in products if p['in_stock'] == True]
    return {'products': result, 'count': len(result)}

#Endpoint 4 - Return best deal
@app.get("/products/deals")
def get_product_deals():

    best_deal = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])

    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }
 
# Endpoint 5 — Return one product by its ID 
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

@app.get('/products/{product_id}/price')
def get_product_price(product_id:int):
    for p in products:
        if p['id'] == product_id:
            return {'name': p['name'], 'price': p['price']}
    return {'error': 'Product not found'}

# Endpoint 6 - Return products by category
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):

    result = [p for p in products if p['category'] == category_name]

    if result:
        return {'products': result, 'count': len(result)}
    else:
        return {"error": "No products found in this category"}

# Endpoint 7 - Return store summary
@app.get('/store/summary')
def get_store_summaey():
    total_products=len(products)
    in_stock_count=len([p for p in products if p["in_stock"] == True])
    out_of_stock_count=len(products)-in_stock_count
    categories=list(set([p["category"] for p in products]))
    return {"store_name": "My Ecommerce Store", "total_products":total_products,"in_stock":in_stock_count,"out_of_stock":out_of_stock_count, "categories": categories,}



#Endpoint 8 - Return products by searching keyword
@app.get('/products/search/{keyword}')
def get_products_by_keyword(keyword: str):

    result = [p for p in products if keyword.lower() in p['name'].lower()]

    if result:
        return {'keyword': keyword, 'results': result, 'total_matches': len(result)}
    else:
        return {"message": "No products matched your search"}
    
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}

#Post+pydentic
@app.post('/feedback')
def post_customer_feedback(data: CustomerFeedbackonProdcuts):
    feedback.append(data.dict())
    return {'message': 'Feedback submitted successfully','feedback': data, 'total_feedback': len(feedback)}

#post order bulk
@app.post('/orders/bulk')
def place_bulk_order_request(order:BulkOrderproducts):
    confirm=[]
    failed=[]
    total=0
    for item in order.items_list:
        product=next((p for p in products if p["id"]==item.product_id),None)
        if not product:
            failed.append({"product_id":item.product_id,"reason":"Prodcut not found"})
        elif not product["in_stock"]:
            failed.append({"product_id":item.product_id,"reason":f'{product["name"]} is Out of stock'})
        else:
            subtotal=product["price"]*item.quantity
            total=total+subtotal
            confirm.append({"product":product["name"],"quantity":item.quantity,"subtotal":subtotal})
    
    return {"company_name":order.company_name,"confirmed":confirm,"failed":failed, "grand_total": total}
