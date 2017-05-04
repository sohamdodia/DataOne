import sys

class Shop (object):
    def __init__ (self, shop_id):
        self.shop_id = shop_id
        self.products = {}

    def add_products (self, products_list, price):
        self.products[products_list] = price

    def __str__ (self):
        s = 'Shop ID: ' + str(self.shop_id) + '\n'
        s += 'Products: ' + str(self.products)
        return s

class Product (object):
    def __init__ (self, name):
        self.name = name
        self.variants = []

    def add (self, price, part_index, part_length):
        self.variants.append({'price': price, 'part_index': part_index, 'part_length': part_length})

    def __str__ (self):
        s = str(self.name)
        s += '\n'
        s += str(self.variants)
        return s

def find_shop_by_id (shops, shop_id):
    for shop in shops:
        if shop.shop_id == shop_id:
            return shop
    return None

def available_in_shop (shop, products_list, query_products):
    shop_products = []
    for key, value in shop.products.items():
        shop_products += products_list[key]
    shop_products = list(set(shop_products))
    for product in query_products:
        try:
            index = shop_products.index(product)
        except ValueError:
            return False
    return True

def add_products (available_products, name, price, part_index, part_length):
    exists = False
    for i in range(len(available_products)):
        a_p = available_products[i]
        if a_p.name == name:
            exists = True
            index = i
            break
    if exists:
        available_products[index].add(price / part_length, part_index, part_length)
    else:
        available_products.append(Product(name))
        available_products[-1].add(price / part_length, part_index, part_length)

def list_contains (l, v):
    try:
        index = l.index(v)
        return True
    except:
        return False

def get_min_price (products_list, products_left, first = False):
    products_left = list(products_left)

    this_product_name = products_left.pop(0)

    if len(products_left) > 0:
        results_list = get_min_price(products_list, products_left)

    this_product = None

    for i in range(len(products_list)):
        if products_list[i].name == this_product_name:
            this_product = products_list[i]

    if this_product is None:
        return 0.0

    to_return = []
    if len(products_left) == 0:
        for i in range(len(this_product.variants)):
            v = this_product.variants[i]
            to_return.append({'indices_selected': [v['part_index']], 'total': v['price'] * v['part_length']})
    else:
        for i in range(len(this_product.variants)):
            v = this_product.variants[i]
            for j in range(len(results_list)):
                r = results_list[j]
                indices_selected = list(r['indices_selected'])
                total = r['total']

                if list_contains(indices_selected, v['part_index']):
                    this_price = total
                else:
                    this_price = total + (v['price'] * v['part_length'])
                    indices_selected.append(v['part_index'])

                to_return.append({'indices_selected': indices_selected, 'total': this_price})

    if not first:
        return to_return

    minimum = to_return[0]['total']
    for r in to_return:
        if r['total'] < minimum:
            minimum = r['total']

    return minimum


def get_number_of_variants (products_list, name):
    for p in products_list:
        if p.name == name:
            return len(p.variants)
    return 0

def main ():
    if len(sys.argv) < 3:
        print 'Usage: python code.py <csv file> <product> <product> ..'
        sys.exit(0)

    csv_file = sys.argv[1]
    products = sys.argv[2:]
    # products.sort()

    file = open(csv_file, 'r')
    lines = file.readlines()

    shops_list = []

    products_list = []

    for line in lines:
        elements = line.split(',')
        for i in range(len(elements)):
            elements[i] = elements[i].strip()
        shop_id = int(elements[0])
        price = float(elements[1])
        shop_products = elements[2:]

        this_shop = find_shop_by_id(shops_list, shop_id)
        if this_shop is None:
            this_shop = Shop(shop_id)
            shops_list.append(this_shop)
        try:
            index = products_list.index(shop_products)
        except ValueError:
            index = len(products_list)
            products_list.append(shop_products)
        this_shop.add_products(index, price)


    eligible_shops = []

    for shop in shops_list:
        if available_in_shop(shop, products_list, products):
            eligible_shops.append(shop)

    if len(eligible_shops) == 0:
        print 'none'
        sys.exit(0)

    results = []

    for shop in eligible_shops:
        available_products = []
        for key, value in shop.products.items():
            these_products = products_list[key]
            for t_p in these_products:
                add_products(available_products, t_p, value, key, len(these_products))
        available_products = sorted(available_products, key = lambda x: len(x.variants), reverse = True)
        products = sorted(products, key = lambda x: get_number_of_variants(available_products, x), reverse = True)

        this_shop_price = get_min_price(available_products, products, True)
        results.append({'shop_id': shop.shop_id, 'total': this_shop_price})

    results = sorted(results, key = lambda x: x['total'])
    
    print str(results[0]['shop_id']) + ', ' + str(results[0]['total'])

if __name__ == '__main__':
    main()