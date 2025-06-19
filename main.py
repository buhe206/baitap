from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import mysql.connector
from mysql.connector import Error
from datetime import date

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234567",
    "database": "baitapnhom1"
}

def get_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print("Lỗi khi kết nối với MySQL:", e)
        return None

class CustomerCreate(BaseModel):
    First_name: str
    Last_name: str
    name: str
    Phone_number: str = None
    email: str = None
    address: str = None

class CustomerOut(CustomerCreate):
    Customer_id: int

class OrderCreate(BaseModel):
    OrderDate: date
    Customer_id: int

class OrderOut(OrderCreate):
    OrderID: int

class PerfumeCreate(BaseModel):
    ProductName: str
    Product_brand: str
    size: str
    price: float

class PerfumeOut(PerfumeCreate):
    Product_id: int

class EmployeeCreate(BaseModel):
    employees_name: str
    position: str
    Inventory_id: int

class EmployeeOut(EmployeeCreate):
    Employees_id: int

@app.get("/")
def root():
    return {"message": "FastAPI đang hoạt động"}

@app.get("/api")
def api_root():
    return {"message": "Chào mừng đến với API của bạn"}

@app.post("/customer/", response_model=CustomerOut)
def create_customer(customer: CustomerCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO baitapnhom1.Customer (First_name, Last_name, name, Phone_number, email, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            customer.First_name,
            customer.Last_name,
            customer.name,
            customer.Phone_number,
            customer.email,
            customer.address
        ))
        conn.commit()
        customer_id = cursor.lastrowid
        return CustomerOut(Customer_id=customer_id, **customer.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.get("/customer/", response_model=List[CustomerOut])
def get_customers():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Customer")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.put("/customer/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, customer: CustomerCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Customer WHERE Customer_id = %s", (customer_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        cursor.execute("""
            UPDATE baitapnhom1.Customer SET First_name=%s, Last_name=%s, name=%s, Phone_number=%s, email=%s, address=%s
            WHERE Customer_id=%s
        """, (
            customer.First_name,
            customer.Last_name,
            customer.name,
            customer.Phone_number,
            customer.email,
            customer.address,
            customer_id
        ))
        conn.commit()
        return CustomerOut(Customer_id=customer_id, **customer.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/customer/{customer_id}", response_model=dict)
def delete_customer(customer_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Customer WHERE Customer_id = %s", (customer_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        cursor.execute("DELETE FROM baitapnhom1.Customer WHERE Customer_id = %s", (customer_id,))
        conn.commit()
        return {"message": "Xóa khách hàng thành công"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.get("/customer/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Customer WHERE Customer_id = %s", (customer_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        return row
    finally:
        cursor.close()
        conn.close()

@app.post("/orders/", response_model=OrderOut)
def create_order(order: OrderCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Customer_id FROM baitapnhom1.Customer WHERE Customer_id = %s", (order.Customer_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Khách hàng không tồn tại")
        cursor.execute(
            "INSERT INTO baitapnhom1.Orders (OrderDate, Customer_id) VALUES (%s, %s)",
            (order.OrderDate, order.Customer_id)
        )
        conn.commit()
        order_id = cursor.lastrowid
        return OrderOut(OrderID=order_id, **order.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.get("/orders/", response_model=List[OrderOut])
def get_orders():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Orders")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.put("/orders/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order: OrderCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Orders WHERE OrderID = %s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
        cursor.execute("SELECT Customer_id FROM baitapnhom1.Customer WHERE Customer_id = %s", (order.Customer_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Khách hàng không tồn tại")
        cursor.execute(
            "UPDATE baitapnhom1.Orders SET OrderDate=%s, Customer_id=%s WHERE OrderID=%s",
            (order.OrderDate, order.Customer_id, order_id)
        )
        conn.commit()
        return OrderOut(OrderID=order_id, **order.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/orders/{order_id}", response_model=dict)
def delete_order(order_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Orders WHERE OrderID = %s", (order_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
        cursor.execute("DELETE FROM baitapnhom1.Orders WHERE OrderID = %s", (order_id,))
        conn.commit()
        return {"message": "Xóa đơn hàng thành công"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.post("/perfume/", response_model=PerfumeOut)
def create_perfume(perfume: PerfumeCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO baitapnhom1.Perfume (ProductName, Product_brand, size, price)
            VALUES (%s, %s, %s, %s)
        """, (
            perfume.ProductName,
            perfume.Product_brand,
            perfume.size,
            perfume.price
        ))
        conn.commit()
        product_id = cursor.lastrowid
        return PerfumeOut(Product_id=product_id, **perfume.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.get("/perfume/", response_model=List[PerfumeOut])
def get_perfumes():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Perfume")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.put("/perfume/{product_id}", response_model=PerfumeOut)
def update_perfume(product_id: int, perfume: PerfumeCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Perfume WHERE Product_id = %s", (product_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
        cursor.execute("""
            UPDATE baitapnhom1.Perfume SET ProductName=%s, Product_brand=%s, size=%s, price=%s
            WHERE Product_id=%s
        """, (
            perfume.ProductName,
            perfume.Product_brand,
            perfume.size,
            perfume.price,
            product_id
        ))
        conn.commit()
        return PerfumeOut(Product_id=product_id, **perfume.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/perfume/{product_id}", response_model=dict)
def delete_perfume(product_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Perfume WHERE Product_id = %s", (product_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
        cursor.execute("DELETE FROM baitapnhom1.Perfume WHERE Product_id = %s", (product_id,))
        conn.commit()
        return {"message": "Xóa sản phẩm thành công"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.post("/employees/", response_model=EmployeeOut)
def create_employee(employee: EmployeeCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Inventory_id FROM baitapnhom1.Inventory WHERE Inventory_id = %s", (employee.Inventory_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Kho không tồn tại")
        cursor.execute("""
            INSERT INTO baitapnhom1.Employees (employees_name, position, Inventory_id)
            VALUES (%s, %s, %s)
        """, (
            employee.employees_name,
            employee.position,
            employee.Inventory_id
        ))
        conn.commit()
        employee_id = cursor.lastrowid
        return EmployeeOut(Employees_id=employee_id, **employee.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.get("/employees/", response_model=List[EmployeeOut])
def get_employees():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Employees")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, employee: EmployeeCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Employees WHERE Employees_id = %s", (employee_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
        cursor.execute("SELECT Inventory_id FROM baitapnhom1.Inventory WHERE Inventory_id = %s", (employee.Inventory_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Kho không tồn tại")
        cursor.execute("""
            UPDATE baitapnhom1.Employees SET employees_name=%s, position=%s, Inventory_id=%s
            WHERE Employees_id=%s
        """, (
            employee.employees_name,
            employee.position,
            employee.Inventory_id,
            employee_id
        ))
        conn.commit()
        return EmployeeOut(Employees_id=employee_id, **employee.dict())
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/employees/{employee_id}", response_model=dict)
def delete_employee(employee_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM baitapnhom1.Employees WHERE Employees_id = %s", (employee_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
        cursor.execute("DELETE FROM baitapnhom1.Employees WHERE Employees_id = %s", (employee_id,))
        conn.commit()
        return {"message": "Xóa nhân viên thành công"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi SQL: {e}")
    finally:
        cursor.close()
        conn.close()

@app.get("/statistics/")
def get_statistics():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối DB")
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) as total_customers FROM baitapnhom1.Customer")
        total_customers = cursor.fetchone()['total_customers']
        cursor.execute("SELECT COUNT(*) as total_orders FROM baitapnhom1.Orders")
        total_orders = cursor.fetchone()['total_orders']
        cursor.execute("SELECT SUM(TotalAmount) as total_revenue FROM baitapnhom1.OrderDetails")
        total_revenue = cursor.fetchone()['total_revenue'] or 0
        cursor.execute("SELECT SUM(quantity) as total_inventory FROM baitapnhom1.Inventory")
        total_inventory = cursor.fetchone()['total_inventory'] or 0

        return {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "total_inventory": total_inventory
        }
    finally:
        cursor.close()
        conn.close()