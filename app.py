from flask import *

app = Flask(__name__)
app.secret_key = 'A+4#s_T%P8g0@o?6'

import pymysql

connection = pymysql.connect(host='localhost', user='root', password='',
                             database='Flask_Shop')


@app.route('/')
def home():
    if 'key' in session:
        print(session['key'])

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM products")
        # AFter executing the query above, get all rows

        deals = cursor.fetchall()

        cursor.execute("SELECT * FROM products")
        # AFter executing the query above, get all rows

        peaks = cursor.fetchall()

        return render_template('index.html', deals=deals, peaks=peaks)

    else:
        return redirect('/login')


@app.route('/single/<product_id>')
def single(product_id):
    # Create a cursor to execute SQL Query
    cursor = connection.cursor()
    # below %s is a placeholder o make sure that the id is actually detected
    cursor.execute('SELECT * FROM products WHERE product_id= %s ', (product_id))
    session['key'] = product_id
    # AFter executing the query above, to get one row
    row = cursor.fetchone()
    session['product_id'] = row[0]
    session['product_name'] = row[1]
    session['product_desc'] = row[2]
    session['product_cost'] = row[3]
    session['image_url'] = row[7]

    # after getting the row forward it to single.html for users to access it
    return render_template('cart1.html', row=row)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user_name = request.form['txt']
        user_email = request.form['email']
        user_password = request.form['pswd']
        cursor = connection.cursor()

        sql = "insert into users(user_name,user_email,user_password) values (%s, %s, %s)"

        cursor.execute(sql, (user_name, user_email, user_password))
        connection.commit()

        return render_template('login_signup.html', data="Registered Successfully Click to Login")

    else:

        return render_template('login_signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['pswd']
        cursor = connection.cursor()

        sql = "select * from users where user_email=%s and user_password=%s"
        cursor.execute(sql, (user_email, user_password))
        row = cursor.fetchone()


        if cursor.rowcount == 0:
            return render_template('login_signup.html', message="Invalid Credentials")

        elif cursor.rowcount == 1:
            session['key'] = row[1]
            print(session['key'])
            return redirect('/')


        else:
            return render_template('login_signup.html', message="Something Wrong with Credentials")





    else:
        return render_template('login_signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/addcart')
def add_cart():
    if 'key' in session:
        # cursor = connection.cursor()
        # # below %s is a placeholder o make sure that the id is actually detected
        # # cursor.execute('SELECT * FROM products WHERE product_id= %s ', (product_id))
        # # AFter executing the query above, to get one row
        # row = cursor.fetchone()
        # session['product_id'] = row[0]
        # print(session['product_id'])
        # session['product_name'] = row[1]
        # session['product_desc'] = row[2]
        # session['product_cost'] = row[3]
        # session['image_url'] = row[7]
        # session['product_id'] = row[0]
        # print(session['product_id'])
        # session['product_name'] = row[1]
        # session['product_desc'] = row[2]
        # session['product_cost'] = row[3]
        # session['image_url'] = row[7]

        return render_template('shopping_cart.html')


# add to cart route
@app.route('/add', methods=['POST', 'GET'])
def add_product_to_cart():
    _quantity = int(request.form['quantity'])
    _code = request.form['code']
    # validate the received values
    if _quantity and _code and request.method == 'POST':
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products WHERE product_id= %s", _code)
        row = cursor.fetchone()
        # An array is a collection of items stored at contiguous memory locations. The idea is to store multiple items of the same type together

        itemArray = {str(row['product_id']): {'product_name': row['product_name'], 'product_id': row['product_id'],
                                              'quantity': _quantity, 'product_cost': row['product_cost'],
                                              'image_url': row['image_url'],
                                              'total_price': _quantity * row['product_cost'],
                                              'product_brand': row['product_brand']}}
        print((itemArray))

        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        # if there is an item already
        if 'cart_item' in session:
            # check if the product you are adding is already there
            print("The test cart", type(row['product_id']))
            print("session hf", session['cart_item'])
            if str(row['product_id']) in session['cart_item']:
                print("reached here 1")

                for key, value in session['cart_item'].items():
                    # check if product is there
                    if str(row['product_id']) == key:
                        print("reached here 2")
                        # take the old quantity  which is in session with cart item and key quantity
                        old_quantity = session['cart_item'][key]['quantity']
                        # add it with new quantity to get the total quantity and make it a session
                        total_quantity = old_quantity + _quantity
                        session['cart_item'][key]['quantity'] = total_quantity
                        # now find the new price with the new total quantity and add it to the session
                        session['cart_item'][key]['total_price'] = total_quantity * row['product_cost']

            else:
                print("reached here 3")
                # a new product added in the cart.Merge the previous to have a new cart item with two products
                session['cart_item'] = array_merge(session['cart_item'], itemArray)

            for key, value in session['cart_item'].items():
                individual_quantity = int(session['cart_item'][key]['quantity'])
                individual_price = float(session['cart_item'][key]['total_price'])
                all_total_quantity = all_total_quantity + individual_quantity
                all_total_price = all_total_price + individual_price

        else:
            # if the cart is empty you add the whole item array
            session['cart_item'] = itemArray
            all_total_quantity = all_total_quantity + _quantity
            # get total price by multiplyin the cost and the quantity
            all_total_price = all_total_price + _quantity * float(row['product_cost'])

        # add total quantity and total price to a session
        session['all_total_quantity'] = all_total_quantity
        session['all_total_price'] = all_total_price
        return redirect(url_for('.cart'))
    else:
        return 'Error while adding item to cart'


# function for joining arrays , we have the first array and second array
# if a customer adds an item to a cart ,we take note,
# if they aadd another item , then merge the arrays to get the total items in one list

def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    # takes the new product add to the existing and merge to have one array with two products
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


# delete route
@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = Trtemplatesue
        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/') the cart function
        return redirect(url_for('.cart'))
    except Exception as e:
        print(e)


# empty cart route
@app.route('/empty')
def empty_cart():
    try:
        if 'cart_item' in session or 'all_total_quantity' in session or 'all_total_price' in session:
            session.pop('cart_item', None)
            session.pop('all_total_quantity', None)
            session.pop('all_total_price', None)
            return redirect(url_for('.cart'))
        else:
            return redirect(url_for('.cart'))

    except Exception as e:
        print(e)


#
@app.route('/cart')
def cart():
    return render_template('cart.html')


def check_customer():
    if 'email' in session:
        return True
    else:
        return False


@app.route('/customer_checkout')
def customer_checkout():
    if check_customer():
        return redirect('/cart')
    else:
        return redirect('/signin')


app.run(debug=True)
