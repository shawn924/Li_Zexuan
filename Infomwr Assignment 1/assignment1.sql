/* Bank Database */

DROP TABLE IF EXISTS bill;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS partner;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS branch;
DROP TABLE IF EXISTS bill_item;
DROP TABLE IF EXISTS partner_catalog;


CREATE TABLE bill (
    bill_id varchar(20) primary key,            --independent bill
    branch_id varchar(50) not null,          --id for branches
    amount numeric(12,2),             --amount of the bill
    customer_id varchar(20) not null,        --each customer can have multiple bills
    bill_date date,          --date of bill issued
    due_date date,           --date of bill due
    status varchar(20),             --status of the bill(draft,issued,paid,overdue,cancelled,refund)
    payment_methods varchar(20),    --payment_methods(bank_transfer, ideal,apple_pay)
    foreign key(branch_id) REFERENCES branch(branch_id),
    foreign key(customer_id) REFERENCES customer(customer_id)
);

CREATE TABLE customer(
    customer_id varchar(20) primary key,        --independent customer
    name varchar(20),
	gender varchar(10),
	street varchar(100),
    house_number varchar(20),
    city varchar(20),
    country varchar(20),            --address of customer
    phone_number varchar(50) unique,       --one customer is using only one number to register(might be null)
    email varchar(50) not null unique,              --one customer is using only one email to register
    customer_category varchar(20), --type of customer(regular/premium)
    date_of_birth date,
	create_date date         --date of customer is created in the database
);

CREATE TABLE partner(
    partner_id varchar(20) primary key,  --unique id for partners
    company_name varchar(100),
    country varchar(20),
    products_and_services varchar(50),
    email varchar(50),
    industry varchar(50),
    is_active boolean       --might used to be partner,but not anymore
);

CREATE TABLE product(
    product_id varchar(100) primary key,
    product_type varchar(100),
    product_name varchar(100),
    price numeric(12,2),    --price for one product
    stock_quantity int      --quantity that is still in warhouse
);

CREATE TABLE branch(
    branch_id varchar(50) primary key,
    branch_name varchar(50),
    street varchar(100),
    house_number varchar(20),
    city varchar(20),
    country varchar(20),
    postcode varchar(20),
    email varchar(50)
);

CREATE TABLE employee(
    employee_id varchar(20) primary key,
    first_name varchar(50),
    last_name varchar(50),
    email varchar(50) not null unique,
    title varchar(50),
    branch_id varchar(50),
    is_active boolean,
    salary real,
    foreign key(branch_id) REFERENCES branch(branch_id) --1 employee works only in 1 branch,and 1 branch can have many employees.
);

CREATE TABLE bill_item(
    bill_id varchar(20),
    product_id varchar(100),
    quantity int,  --quantity for product that is sold
    price numeric(12,2),
    primary key(bill_id, product_id),
    foreign key(bill_id) REFERENCES bill(bill_id),
    foreign key(product_id) REFERENCES product(product_id)
);

CREATE TABLE partner_catalog(
    partner_id varchar(20),
    product_id varchar(100),
    primary key(partner_id,product_id),
    foreign key(partner_id) REFERENCES partner(partner_id),
    foreign key(product_id) REFERENCES product(product_id)
);


/* Sample Data */


INSERT INTO branch(branch_id, branch_name, street, house_number, city, country, postcode, email) VALUES
('B001','Amsterdam HQ','Damrak','45','Amsterdam','NL','1012LP','hq@tradingco.nl'),
('B002','Berlin Branch','Friedrichstr','210','Berlin','DE','10117',NULL),
('B003','New York Office','Broadway','500','New York','US','10036','ny@tradingco.com'),
('B004','London Branch','Oxford Street','100','London','UK','W1D1LL',NULL),
('B005','Paris Branch','Champs-Élysées','50','Paris','FR','75008','paris@tradingco.fr');

INSERT INTO customer(customer_id, name, gender, street, house_number, city, country, phone_number, email, customer_category, date_of_birth, create_date) VALUES
('C001','Alice','Female','Street 1','10','Amsterdam','NL',NULL,'alice@example.nl','regular','1982-10-11','2025-01-01'),
('C002','Bob','Male','Street 2','20','Berlin','DE',NULL,'bob@example.de','premium','1997-04-08','2025-01-02'),
('C003','Carol','Female','Street 3','30','New York','US','+12125550123','carol@example.com','regular','1983-09-10','2025-01-03'),
('C004','Dave','Male','Street 4','40','London','UK','+442071234567','dave@example.co.uk',NULL,'1970-05-19','2025-01-04'),
('C005','Eve','Female','Street 5','50','Paris','FR',NULL,'eve@example.fr','premium','1984-03-23','2025-01-05'),
('C006','Alice','Female','Street 1','10','Amsterdam','NL',NULL,'alice2@example.nl','regular','1982-10-11','2025-01-01'),
('C007','Grace','Female','Street 7','70','Berlin','DE','+491234567891','grace@example.de',NULL,'1995-07-27','2025-01-07'),
('C008','Heidi','Female','Street 8','80','New York','US',NULL,'heidi@example.com','regular','1989-12-02','2025-01-08'),
('C009','Ivan','Male','Street 9','90','London','UK','+442071234568','ivan@example.co.uk','premium','1978-06-14','2025-01-09'),
('C010','Judy','Female','Street 10','100','Paris','FR',NULL,'judy@example.fr',NULL,'1992-9-30','2025-01-10');

INSERT INTO partner(partner_id, company_name, country, products_and_services, email, industry, is_active) VALUES
('P001','Global Supplies','NL','Electronics','contact@globalsupplies.nl','Wholesale',1),
('P002','BerlinTech','DE',NULL,'info@berlintech.de','Technology',1),
('P003','NY Goods','US','Office Supplies',NULL,'Retail',1),
('P004','London Logistics','UK','Shipping','support@londonlogistics.co.uk','Transport',1),
('P005','Paris Fashion','FR',NULL,'contact@parisfashion.fr','Retail',0);

INSERT INTO product(product_id, product_type, product_name, price, stock_quantity) VALUES
('PR001','Electronics','Laptop',1200.00,50),
('PR002','Electronics','Smartphone',800.00,100),
('PR003','Hardware','Printer',250.00,30),
('PR004','Office','Chair',100.00,200),
('PR005','Office','Desk',200.00,150),
('PR006','Clothing','Jacket',120.00,80),
('PR007','Clothing','Shoes',90.00,120),
('PR008','Electronics','Monitor',300.00,40),
('PR009','Hardware','Keyboard',50.00,70),
('PR010','Office','Notebook',5.00,500);

INSERT INTO employee(employee_id, first_name, last_name, email, title, branch_id, is_active, salary) VALUES
('E001','Alice','Smith','alice.smith@tradingco.com','Manager','B001',1,5500.00),
('E002','Bob','Johnson','bob.johnson@tradingco.com','Sales Representative','B002',1,3200.00),
('E003','Carol','Williams','carol.williams@tradingco.com','Accountant','B003',1,4000.00),
('E004','David','Brown','david.brown@tradingco.com','Warehouse Supervisor','B004',1,3800.00),
('E005','Eve','Davis','eve.davis@tradingco.com','Sales Representative','B005',1,3100.00),
('E006','Frank','Miller','frank.miller@tradingco.com','Logistics Coordinator','B001',1,3600.00),
('E007','Grace','Wilson','grace.wilson@tradingco.com',NULL,'B002',1,NULL),
('E008','Heidi','Moore','heidi.moore@tradingco.com','Accountant','B003',1,4200.00),
('E009','Ivan','Taylor','ivan.taylor@tradingco.com','Sales Manager','B004',0,5000.00),
('E010','Judy','Anderson','judy.anderson@tradingco.com',NULL,'B005',1,NULL);

INSERT INTO partner_catalog(partner_id, product_id) VALUES
('P001','PR001'),
('P001','PR002'),
('P002','PR003'),
('P002','PR009'),
('P003','PR004'),
('P003','PR005'),
('P005','PR006'),
('P005','PR007'),
('P001','PR008'),
('P003','PR010');

INSERT INTO bill(bill_id, branch_id, amount, customer_id, bill_date, due_date, status, payment_methods) VALUES
('BILL001','B001',1500.00,'C001','2025-02-01','2025-02-10','issued','apple_pay'),
('BILL002','B002',800.00,'C002','2025-02-02',NULL,'paid','bank_transfer'),
('BILL003','B003',125.00,'C003','2025-02-03','2025-02-13','overdue','ideal'),
('BILL004','B004',200.00,'C004','2025-02-04',NULL,'draft','apple_pay'),
('BILL005','B005',300.00,'C005','2025-02-05','2025-02-15','refund','bank_transfer'),
('BILL006','B001',1200.00,'C006','2025-02-06',NULL,'paid','ideal'),
('BILL007','B002',100.00,'C007','2025-02-07','2025-02-17','cancelled','apple_pay'),
('BILL008','B003',450.00,'C008','2025-02-08',NULL,'issued','bank_transfer'),
('BILL009','B004',75.00,'C009','2025-02-09','2025-02-19','overdue','ideal'),
('BILL010','B005',220.00,'C010','2025-02-10',NULL,'issued','apple_pay');

INSERT INTO bill_item(bill_id, product_id, quantity, price) VALUES
('BILL001','PR001',1,1200.00),
('BILL001','PR010',60,5.00),
('BILL002','PR002',1,800.00),
('BILL003','PR010',25,5.00),
('BILL004','PR004',2,100.00),
('BILL005','PR005',1,200.00),
('BILL005','PR010',20,5.00),
('BILL006','PR001',1,1200.00),
('BILL007','PR009',2,50.00),
('BILL008','PR002',1,800.00),
('BILL008','PR004',2,100.00),
('BILL009','PR010',15,5.00),
('BILL010','PR006',1,120.00),
('BILL010','PR007',1,90.00),
('BILL002','PR008',1,300.00),
('BILL003','PR003',1,250.00),
('BILL004','PR005',1,200.00),
('BILL006','PR010',10,5.00),
('BILL007','PR004',1,100.00),
('BILL009','PR005',1,200.00);

/*Queries*/

/*
a.
SELECT c.name AS customer_name,
       c.gender,
       p.product_name
FROM customer c
JOIN bill bl ON c.customer_id = bl.customer_id
JOIN bill_product bp ON bl.bill_id = bp.bill_id
JOIN product p ON bp.product_id = p.product_id;

b.
SELECT  
    br.branch_name,  
    SUM(b.amount) AS total_amount,  
    AVG(b.amount) AS avg_amount  
FROM bill b  
JOIN branch br ON b.branch_id = br.branch_id  
GROUP BY br.branch_name;

SELECT br.branch_name,COUNT(e.employee_id) AS total_employees_amoutn
FROM employee e
JOIN branch br ON e.branch_id = br.branch_id
GROUP BY br.branch_name;

SELECT gender, avg(cast((julianday('now') - julianday(date_of_birth)) / 365 AS INT)) AS average_age
FROM customer
GROUP BY gender;

c.
SELECT  
    DISTINCT c.customer_id,  
    c.email  
FROM customer c  
JOIN bill b ON c.customer_id = b.customer_id  
WHERE b.amount > (  
    SELECT AVG(amount) FROM bill  
);

```sql
SELECT name
FROM customer
WHERE (julianday('now') - julianday(date_of_birth)) / 365 > (
    SELECT avg((julianday('now') - julianday(date_of_birth)) / 365) 
    FROM customer
);
*/
